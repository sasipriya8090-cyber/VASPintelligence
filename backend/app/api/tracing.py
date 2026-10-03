"""
Phase 3: Fund-Flow Tracing API Router.

Endpoints
---------
POST /api/trace/wallet
    Body: WalletTraceRequest
    Perform a full BFS fund-flow trace and return the graph + statistics.

GET  /api/trace/ethereum/address/{address}
    Query params: max_hops (1-5, default 2), page_size (1-100, default 25)
    Convenience REST endpoint for tracing a single address.

GET  /api/trace/ethereum/address/{address}/summary
    Returns only the TraceSummary (lightweight — no graph data).

Both endpoints:
  - Validate the Ethereum address format.
  - Delegate to TransactionTracingService (BFS over EthereumAdapter).
  - Work in DEMO mode when no API key is configured.
  - Return structured error responses for invalid input / provider failures.
"""
import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.adapters.ethereum import (
    EthereumAdapter,
    InvalidAddressError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
    ETH_ADDRESS_RE,
)
from app.schemas.tracing_schemas import (
    WalletTraceRequest,
    WalletTraceResponse,
    TraceNodeData,
    TraceEdgeData,
    ReactFlowGraph,
    ReactFlowNode,
    ReactFlowEdge,
    TraceSummary,
)
from app.services.tracing_service import (
    TransactionTracingService,
    FundFlowGraph,
    ABSOLUTE_MAX_HOPS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trace", tags=["Fund-Flow Tracing (Phase 3)"])

# One shared service instance (keeps the adapter connection pool alive)
_tracing_service = TransactionTracingService()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_eth_address(address: str) -> str:
    """Strip whitespace, validate format, return cleaned address. Raise 400 on failure."""
    clean = address.strip()
    if not ETH_ADDRESS_RE.match(clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid Ethereum address: '{clean}'. "
                "A valid Ethereum address must start with '0x' followed by "
                "exactly 40 hexadecimal characters."
            ),
        )
    return clean


def _graph_to_response(graph: FundFlowGraph) -> WalletTraceResponse:
    """Convert a FundFlowGraph into a WalletTraceResponse."""
    # ── Summary ──────────────────────────────────────────────────────────
    summary_dict = graph.to_summary()
    summary = TraceSummary(**summary_dict)

    # ── Nodes (raw) ───────────────────────────────────────────────────────
    raw_nodes = [TraceNodeData(**n.to_dict()) for n in graph.nodes]

    # ── Edges (raw) ───────────────────────────────────────────────────────
    raw_edges = [TraceEdgeData(**e.to_dict()) for e in graph.edges]

    # ── React Flow graph ─────────────────────────────────────────────────
    rf_data = graph.to_react_flow()

    rf_nodes = [
        ReactFlowNode(
            id=n["id"],
            type=n.get("type", "customNode"),
            nodeType=n.get("nodeType", "customNode"),
            position=n["position"],
            data=n["data"],
        )
        for n in rf_data["nodes"]
    ]

    rf_edges = [
        ReactFlowEdge(
            id=e["id"],
            source=e["source"],
            target=e["target"],
            animated=e.get("animated", True),
            label=e.get("label"),
            style=e.get("style", {}),
            data=e.get("data", {}),
        )
        for e in rf_data["edges"]
    ]

    rf_graph = ReactFlowGraph(nodes=rf_nodes, edges=rf_edges)

    return WalletTraceResponse(
        summary=summary,
        nodes=raw_nodes,
        edges=raw_edges,
        graph=rf_graph,
    )


async def _run_trace(address: str, max_hops: int, page_size: int) -> WalletTraceResponse:
    """Execute trace and map adapter exceptions to HTTP errors."""
    try:
        graph = await _tracing_service.trace(
            wallet_address=address,
            max_hops=max_hops,
            page_size=page_size,
        )
    except RateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": "60"},
        ) from exc
    except ProviderTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return _graph_to_response(graph)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post(
    "/wallet",
    response_model=WalletTraceResponse,
    summary="Trace Fund Flow from a Wallet (POST)",
    description=(
        "Performs a breadth-first fund-flow trace starting from the given wallet address. "
        "Returns a graph of nodes (wallets) and edges (transactions) with aggregate statistics. "
        "Works in DEMO mode when no API key is configured. "
        "Set `max_hops=1` for direct counterparties only; `max_hops=2` (default) includes "
        "counterparties of counterparties."
    ),
    responses={
        200: {"description": "Fund-flow graph with statistics"},
        400: {"description": "Invalid Ethereum address"},
        422: {"description": "Validation error (e.g. max_hops out of range)"},
        429: {"description": "Blockchain provider rate limit"},
        503: {"description": "Blockchain provider unavailable"},
    },
)
async def trace_wallet_post(payload: WalletTraceRequest) -> WalletTraceResponse:
    """
    POST /api/trace/wallet

    Accepts a JSON body with wallet_address, blockchain, max_hops, page_size.
    """
    if payload.blockchain.lower() != "ethereum":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Blockchain '{payload.blockchain}' is not supported in Phase 3. "
                "Only 'ethereum' is currently available."
            ),
        )

    clean_address = _validate_eth_address(payload.wallet_address)
    logger.info(
        "[trace] POST trace request: address=%s hops=%d size=%d mode=%s",
        clean_address[:10] + "…",
        payload.max_hops,
        payload.page_size,
        "LIVE" if _tracing_service._adapter.is_live else "DEMO",
    )
    return await _run_trace(clean_address, payload.max_hops, payload.page_size)


@router.get(
    "/ethereum/address/{address}",
    response_model=WalletTraceResponse,
    summary="Trace Fund Flow from a Wallet (GET)",
    description=(
        "Convenience GET endpoint for fund-flow tracing. Equivalent to POST /api/trace/wallet "
        "but accepts parameters as path/query arguments."
    ),
    responses={
        200: {"description": "Fund-flow graph with statistics"},
        400: {"description": "Invalid Ethereum address"},
        422: {"description": "Validation error"},
        429: {"description": "Rate limit"},
        503: {"description": "Provider unavailable"},
    },
)
async def trace_wallet_get(
    address: str,
    max_hops: int = Query(
        default=2,
        ge=1,
        le=ABSOLUTE_MAX_HOPS,
        description="Tracing depth (1-5, default 2)",
    ),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
        description="Transactions per address per hop",
    ),
) -> WalletTraceResponse:
    """
    GET /api/trace/ethereum/address/{address}?max_hops=2&page_size=25
    """
    clean_address = _validate_eth_address(address)
    logger.info(
        "[trace] GET trace request: address=%s hops=%d size=%d",
        clean_address[:10] + "…",
        max_hops,
        page_size,
    )
    return await _run_trace(clean_address, max_hops, page_size)


@router.get(
    "/ethereum/address/{address}/summary",
    response_model=TraceSummary,
    summary="Fund-Flow Summary Only (lightweight)",
    description=(
        "Returns only the aggregate flow statistics for a wallet trace — "
        "no graph data. Useful for dashboards or quick risk checks."
    ),
)
async def trace_wallet_summary(
    address: str,
    max_hops: int = Query(default=2, ge=1, le=ABSOLUTE_MAX_HOPS),
    page_size: int = Query(default=25, ge=1, le=100),
) -> TraceSummary:
    """
    GET /api/trace/ethereum/address/{address}/summary
    """
    clean_address = _validate_eth_address(address)
    full_response = await _run_trace(clean_address, max_hops, page_size)
    return full_response.summary

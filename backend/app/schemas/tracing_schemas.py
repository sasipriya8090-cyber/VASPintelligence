"""
Phase 3/4 Tracing API Schemas.

Defines request / response models for fund-flow tracing and
VASP attribution endpoints.

All models are chain-agnostic so they can be reused for
Bitcoin, Tron, etc.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Request
# ─────────────────────────────────────────────────────────────────────────────


class WalletTraceRequest(BaseModel):
    """POST body for /api/trace/wallet."""

    wallet_address: str = Field(
        ...,
        description="Origin wallet address to trace (Ethereum 0x…)",
    )

    blockchain: str = Field(
        default="ethereum",
        description="Target blockchain (only 'ethereum' in current implementation)",
    )

    max_hops: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Tracing depth: 1 = direct counterparties only. Max 5.",
    )

    page_size: int = Field(
        default=25,
        ge=1,
        le=100,
        description="Transactions to fetch per address per hop.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Node / Edge inner models
# ─────────────────────────────────────────────────────────────────────────────


class TraceNodeData(BaseModel):
    """
    Per-address node in the fund-flow graph.

    Phase 4 VASP attribution fields:
    - is_vasp
    - vasp_name
    - vasp_type
    - vasp_confidence
    - vasp_source
    """

    address: str

    hop: int = Field(
        ...,
        description="Distance from origin (0 = origin wallet)",
    )

    is_origin: bool

    # VASP Attribution
    is_vasp: bool
    vasp_name: Optional[str] = None
    vasp_type: Optional[str] = None

    # Phase 4: Attribution confidence and source
    vasp_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for the VASP attribution (0.0-1.0)",
    )

    vasp_source: Optional[str] = Field(
        default=None,
        description="Source of the VASP attribution, e.g. DEMO Registry",
    )

    # Flow statistics
    total_incoming_eth: float
    total_outgoing_eth: float
    net_flow_eth: float
    tx_count: int
    unique_counterparty_count: int

    label: str
    data_mode: str


class TraceEdgeData(BaseModel):
    """A normalized transaction (edge) in the fund-flow graph."""

    tx_hash: str

    from_address: str
    to_address: str

    value_eth: float

    token: str = "ETH"

    timestamp_iso: Optional[str] = None
    block_number: Optional[int] = None

    status: str

    gas_fee_eth: Optional[float] = None

    direction: str

    data_mode: str


# ─────────────────────────────────────────────────────────────────────────────
# React Flow serialization
# ─────────────────────────────────────────────────────────────────────────────


class ReactFlowNode(BaseModel):
    """A node formatted for React Flow."""

    id: str

    type: str = "customNode"

    nodeType: str

    position: Dict[str, float]

    data: Dict[str, Any]


class ReactFlowEdge(BaseModel):
    """An edge formatted for React Flow."""

    id: str

    source: str

    target: str

    animated: bool = True

    label: Optional[str] = None

    style: Dict[str, Any] = Field(
        default_factory=dict
    )

    data: Dict[str, Any] = Field(
        default_factory=dict
    )


class ReactFlowGraph(BaseModel):
    """Full React Flow graph (nodes + edges)."""

    nodes: List[ReactFlowNode]

    edges: List[ReactFlowEdge]


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────


class TraceSummary(BaseModel):
    """High-level aggregate statistics for the trace."""

    origin_address: str

    max_hops: int

    data_mode: str

    traced_at: str = Field(
        ...,
        description="ISO 8601 timestamp when trace ran",
    )

    total_volume_eth: float = Field(
        ...,
        description="Sum of all transaction values in graph",
    )

    total_incoming_eth: float = Field(
        ...,
        description="Incoming to origin wallet",
    )

    total_outgoing_eth: float = Field(
        ...,
        description="Outgoing from origin wallet",
    )

    transaction_count: int

    unique_address_count: int

    vasp_count: int = Field(
        ...,
        description="Number of VASP-attributed nodes in graph",
    )

    unique_direct_counterparties: int


# ─────────────────────────────────────────────────────────────────────────────
# Top-level response
# ─────────────────────────────────────────────────────────────────────────────


class WalletTraceResponse(BaseModel):
    """
    Response schema for:

    POST /api/trace/wallet
    GET /api/trace/ethereum/address/{address}

    Contains:
    - summary : aggregate flow statistics
    - nodes   : raw node data
    - edges   : raw transaction data
    - graph   : React Flow-ready nodes + edges
    """

    summary: TraceSummary

    nodes: List[TraceNodeData]

    edges: List[TraceEdgeData]

    graph: ReactFlowGraph
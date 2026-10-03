"""
Phase 2: Blockchain Data Integration Router.

Provides live/demo Ethereum transaction data with:
  - Address validation
  - In-process TTL caching (no Redis required)
  - Pagination guard (never fetches unlimited history)
  - Structured error handling (invalid address, missing config,
    timeout, rate-limit, provider errors)
  - Clear LIVE vs DEMO data labeling

Endpoint:
    GET /api/blockchain/ethereum/address/{address}/transactions
    GET /api/blockchain/config/status
"""
import datetime
import logging
import time
from typing import Dict, Any, Tuple

from fastapi import APIRouter, HTTPException, Query, status

from app.adapters.ethereum import (
    EthereumAdapter,
    InvalidAddressError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
)
from app.core.config import settings
from app.schemas.blockchain_schemas import (
    BlockchainConfigStatus,
    EthereumAddressTransactionsResponse,
    NormalizedTransaction,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blockchain", tags=["Blockchain Data (Phase 2)"])

# ---------------------------------------------------------------------------
# Single shared adapter instance (keeps connection pool alive)
# ---------------------------------------------------------------------------
_eth_adapter = EthereumAdapter()

# ---------------------------------------------------------------------------
# Simple in-process TTL cache
# key: (address, page, page_size)  →  (timestamp, payload)
# ---------------------------------------------------------------------------
_cache: Dict[Tuple, Tuple[float, Any]] = {}


def _cache_key(address: str, page: int, page_size: int) -> Tuple:
    return (address.lower(), page, page_size)


def _get_cached(key: Tuple) -> Any:
    entry = _cache.get(key)
    if entry is None:
        return None
    cached_at, payload = entry
    if time.monotonic() - cached_at > settings.BLOCKCHAIN_CACHE_TTL:
        del _cache[key]
        return None
    return payload


def _set_cache(key: Tuple, value: Any) -> None:
    _cache[key] = (time.monotonic(), value)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "/config/status",
    response_model=BlockchainConfigStatus,
    summary="Blockchain Provider Configuration Status",
    description=(
        "Returns which blockchain providers are configured without exposing any API keys. "
        "Use this to verify your environment configuration before making data requests."
    ),
)
def get_blockchain_config_status() -> BlockchainConfigStatus:
    """
    Safe configuration status check.

    Reports whether real blockchain APIs are configured and which provider is active,
    but NEVER exposes the actual API key values.
    """
    return BlockchainConfigStatus(
        ethereum_configured=settings.is_ethereum_configured(),
        ethereum_provider=settings.get_ethereum_provider_name(),
        data_mode=settings.get_data_mode(),
        max_tx_per_request=settings.BLOCKCHAIN_MAX_TX_PER_REQUEST,
        cache_ttl_seconds=settings.BLOCKCHAIN_CACHE_TTL,
    )


@router.get(
    "/ethereum/address/{address}/transactions",
    response_model=EthereumAddressTransactionsResponse,
    summary="Fetch Ethereum Transactions for Address",
    description=(
        "Fetches normalized Ethereum transaction history for a given wallet address. "
        "When ETHERSCAN_API_KEY is configured, returns real on-chain data. "
        "When no API key is set, returns clearly labeled DEMO data (identical to Phase 1 behavior). "
        "Results are cached for the configured TTL to avoid redundant API calls."
    ),
    responses={
        200: {"description": "Normalized transaction list (LIVE or DEMO)"},
        400: {"description": "Invalid Ethereum address format"},
        404: {"description": "No transactions found for address"},
        422: {"description": "Validation error (e.g. page_size out of range)"},
        429: {"description": "Blockchain provider rate limit reached"},
        503: {"description": "Blockchain provider unavailable or timeout"},
    },
)
async def get_ethereum_address_transactions(
    address: str,
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        default=25,
        ge=1,
        le=100,
        description="Transactions per page. Maximum 100; hard-capped by server setting.",
    ),
) -> EthereumAddressTransactionsResponse:
    """
    GET /api/blockchain/ethereum/address/{address}/transactions

    Validates the Ethereum address, fetches transaction data from the configured
    provider (or demo data if unconfigured), normalizes the response, and returns
    a paginated result with full metadata including data source and cache status.

    Error Handling:
      - 400 Bad Request: Malformed Ethereum address
      - 429 Too Many Requests: Provider rate limit hit
      - 503 Service Unavailable: Provider timeout or server error
    """
    # ------------------------------------------------------------------
    # 1. Validate Ethereum address format
    # ------------------------------------------------------------------
    clean_address = address.strip()
    if not _eth_adapter.validate_address(clean_address):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid Ethereum address: '{clean_address}'. "
                "A valid Ethereum address must start with '0x' followed by exactly 40 hexadecimal characters."
            ),
        )

    # ------------------------------------------------------------------
    # 2. Check cache
    # ------------------------------------------------------------------
    cache_key = _cache_key(clean_address, page, page_size)
    cached_response = _get_cached(cache_key)
    if cached_response is not None:
        logger.info(
            "[blockchain] Cache HIT for %s page=%d size=%d",
            clean_address[:10] + "...",
            page,
            page_size,
        )
        # Mark as served from cache
        cached_response.cached = True
        return cached_response

    # ------------------------------------------------------------------
    # 3. Fetch from adapter (live or demo)
    # ------------------------------------------------------------------
    logger.info(
        "[blockchain] Fetching transactions for %s... page=%d size=%d mode=%s",
        clean_address[:10] + "...",
        page,
        page_size,
        "LIVE" if _eth_adapter.is_live else "DEMO",
    )

    try:
        raw_txs = await _eth_adapter.get_transactions(
            clean_address, page=page, page_size=page_size
        )
    except RateLimitError as exc:
        logger.warning("[blockchain] Rate limit hit for %s", clean_address[:10] + "...")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers={"Retry-After": "60"},
        ) from exc
    except ProviderTimeoutError as exc:
        logger.error("[blockchain] Timeout for %s", clean_address[:10] + "...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ProviderError as exc:
        logger.error("[blockchain] Provider error for %s: %s", clean_address[:10] + "...", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    # ------------------------------------------------------------------
    # 4. Normalize into response schema
    # ------------------------------------------------------------------
    normalized_txs = []
    for tx in raw_txs:
        normalized_txs.append(
            NormalizedTransaction(
                tx_hash=tx["tx_hash"],
                blockchain=tx["blockchain"],
                from_address=tx["from_address"],
                to_address=tx["to_address"],
                value_eth=tx.get("value_eth", tx.get("amount", 0.0)),
                token=tx.get("token", "ETH"),
                timestamp_iso=tx.get("timestamp_iso"),
                block_number=tx.get("block_number"),
                direction=tx["direction"],
                status=tx.get("status", "unknown"),
                gas_fee_eth=tx.get("gas_fee_eth"),
                confirmations=tx.get("confirmations"),
                data_mode=tx.get("data_mode", settings.DATA_MODE),
            )
        )

    # ------------------------------------------------------------------
    # 5. Determine provider label and data_mode string
    # ------------------------------------------------------------------
    if _eth_adapter.is_live:
        data_mode_str = "LIVE"
        provider_str = settings.get_ethereum_provider_name()
    else:
        data_mode_str = settings.DATA_MODE
        provider_str = "DEMO"

    response = EthereumAddressTransactionsResponse(
        data_mode=data_mode_str,
        provider=provider_str,
        wallet_address=clean_address,
        blockchain="ethereum",
        page=page,
        page_size=page_size,
        transaction_count=len(normalized_txs),
        cached=False,
        transactions=normalized_txs,
        fetched_at=datetime.datetime.now(datetime.timezone.utc),
    )

    # ------------------------------------------------------------------
    # 6. Store in cache
    # ------------------------------------------------------------------
    _set_cache(cache_key, response)

    return response

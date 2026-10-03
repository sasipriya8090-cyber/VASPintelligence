"""
Phase 2 Blockchain API Schemas.

Defines the normalized, chain-agnostic transaction response model
and related schemas for the /api/blockchain endpoints.
"""
import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class NormalizedTransaction(BaseModel):
    """
    Chain-agnostic normalized transaction representation.

    This schema is the common output format for all blockchain adapters.
    Regardless of the source chain (Ethereum, Bitcoin, Tron, etc.), all
    transaction data is normalized to this shape before being returned to
    the client.
    """

    tx_hash: str = Field(..., description="Unique transaction hash / identifier")
    blockchain: str = Field(..., description="Chain name (e.g. 'ethereum')")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    value_eth: float = Field(..., description="Transaction value in native chain token")
    token: str = Field(default="ETH", description="Native token symbol")
    timestamp_iso: Optional[str] = Field(None, description="ISO 8601 timestamp (UTC)")
    block_number: Optional[int] = Field(None, description="Block number containing this transaction")
    direction: str = Field(
        ...,
        description="Transaction direction relative to queried address: INCOMING | OUTGOING | INTERNAL",
    )
    status: str = Field(
        ..., description="Transaction status: confirmed | failed | pending | unknown"
    )
    gas_fee_eth: Optional[float] = Field(None, description="Gas fee in ETH")
    confirmations: Optional[int] = Field(None, description="Number of block confirmations")
    data_mode: str = Field(
        ...,
        description="Indicates whether data is LIVE (real chain data) or DEMO (synthetic).",
    )

    class Config:
        from_attributes = True


class EthereumAddressTransactionsResponse(BaseModel):
    """
    Response schema for GET /api/blockchain/ethereum/address/{address}/transactions
    """

    data_mode: str = Field(
        ...,
        description="'LIVE' if real blockchain data, 'DEMO DATA — NOT LIVE BLOCKCHAIN DATA' if synthetic.",
    )
    provider: str = Field(
        ...,
        description="Data provider name (e.g. 'Etherscan') or 'DEMO' if no provider is configured.",
    )
    wallet_address: str = Field(..., description="Queried wallet address (checksummed)")
    blockchain: str = Field(default="ethereum")
    page: int = Field(default=1, ge=1, description="Current page number (1-based)")
    page_size: int = Field(default=25, ge=1, le=100, description="Transactions per page")
    transaction_count: int = Field(..., description="Number of transactions returned on this page")
    cached: bool = Field(default=False, description="True if this response was served from cache")
    transactions: List[NormalizedTransaction] = Field(
        default_factory=list, description="Normalized transaction list"
    )
    fetched_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Server timestamp when data was fetched or served from cache",
    )


class BlockchainConfigStatus(BaseModel):
    """
    Response schema for GET /api/blockchain/config/status
    Shows which blockchain providers are configured (without exposing keys).
    """

    ethereum_configured: bool
    ethereum_provider: str
    data_mode: str
    max_tx_per_request: int
    cache_ttl_seconds: int
    supported_chains: List[str] = Field(
        default_factory=lambda: ["ethereum"],
        description="Chains with active adapter implementations",
    )
    planned_chains: List[str] = Field(
        default_factory=lambda: ["bitcoin", "tron", "bnb_chain", "solana", "polygon"],
        description="Chains planned for future phases (adapters not yet implemented)",
    )

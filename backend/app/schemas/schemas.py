import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Base & Shared Schemas
class CaseBase(BaseModel):
    title: str
    wallet_address: str
    blockchain: str = "ethereum"
    status: str = "Active"


class CaseCreate(CaseBase):
    pass


class CaseResponse(CaseBase):
    id: int
    case_number: str
    risk_score: float
    risk_level: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


class InvestigationCreate(BaseModel):
    case_number: Optional[str] = None
    title: Optional[str] = None
    wallet_address: str
    blockchain: str = "ethereum"
    summary: Optional[str] = None


class InvestigationResponse(BaseModel):
    id: int
    case_id: int
    summary: str
    created_at: datetime.datetime
    case: Optional[CaseResponse] = None

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: Optional[int] = None
    tx_hash: str
    blockchain: str
    from_address: str
    to_address: str
    amount: float
    token: str
    timestamp: datetime.datetime
    direction: str
    risk_indicators: List[str] = []
    vasp_attribution: Optional[str] = None

    class Config:
        from_attributes = True


class VASPAttribution(BaseModel):
    matched: bool
    name: Optional[str] = None
    type: Optional[str] = None
    blockchain: Optional[str] = None
    address: Optional[str] = None
    confidence: float = 0.0
    source: str = "DEMO Registry"
    attribution_notes: Optional[str] = None


class RiskIndicator(BaseModel):
    category: str
    indicator: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str


class WalletAnalysisRequest(BaseModel):
    wallet_address: str = Field(
        ...,
        description="Wallet address to analyze (e.g. Ethereum 0x...)"
    )
    blockchain: str = Field(
        default="ethereum",
        description="Target blockchain network"
    )


class WalletAnalysisResponse(BaseModel):
    disclaimer: str = "DEMO DATA — NOT LIVE BLOCKCHAIN DATA"
    wallet_address: str
    blockchain: str
    wallet_type: str
    balance: float
    token_symbol: str
    total_transactions_analyzed: int
    risk_score: float
    risk_level: str
    risk_indicators: List[RiskIndicator]
    possible_typologies: List[str]
    vasp_attribution: VASPAttribution
    recent_transactions: List[TransactionResponse]
    graph_nodes: List[Dict[str, Any]]
    graph_edges: List[Dict[str, Any]]

    # Phase 7 — AI Investigation Summary
    ai_investigation: Optional[Dict[str, Any]] = None

    created_at: datetime.datetime
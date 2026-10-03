import re
import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.session import get_db
from app.core.config import settings
from app.models.models import Case, Investigation, Transaction, Wallet, VASP
from app.schemas.schemas import (
    CaseResponse,
    InvestigationCreate,
    InvestigationResponse,
    WalletAnalysisRequest,
    WalletAnalysisResponse,
    TransactionResponse,
    VASPAttribution,
    RiskIndicator
)

from app.adapters.ethereum import EthereumAdapter
from app.services.vasp_service import VASPAttributionService
from app.services.risk_service import RiskAnalysisService
from app.services.ai_investigation_service import AIInvestigationService


router = APIRouter()


# ============================================================
# Initialize services and adapters
# ============================================================

eth_adapter = EthereumAdapter()
vasp_service = VASPAttributionService()
risk_service = RiskAnalysisService()
ai_investigation_service = AIInvestigationService()


ETH_ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")


# ============================================================
# Health Check
# ============================================================

@router.get("/health", summary="Service Health & Status Check")
def health_check():
    """Health check endpoint indicating service availability and DEMO mode status."""

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "data_mode": settings.DATA_MODE,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }


# ============================================================
# Investigations
# ============================================================

@router.get(
    "/investigations",
    response_model=List[InvestigationResponse],
    summary="List all investigations"
)
def get_investigations(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieve all logged forensic investigations."""

    investigations = (
        db.query(Investigation)
        .order_by(desc(Investigation.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return investigations


@router.post(
    "/investigations",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new investigation case"
)
def create_investigation(
    payload: InvestigationCreate,
    db: Session = Depends(get_db)
):
    """Create a new manual case and investigation record."""

    clean_addr = payload.wallet_address.strip()

    if (
        payload.blockchain.lower() == "ethereum"
        and not ETH_ADDRESS_REGEX.match(clean_addr)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid Ethereum address format. "
                "Must begin with '0x' followed by 40 hexadecimal characters."
            )
        )

    # Generate a unique case number if not provided
    case_count = db.query(Case).count() + 1

    case_number = (
        payload.case_number
        or f"CASE-2026-{case_count:03d}"
    )

    title = (
        payload.title
        or f"Forensic Review: {clean_addr[:10]}...{clean_addr[-6:]}"
    )

    summary = (
        payload.summary
        or (
            "Initial intake record created for blockchain entity attribution "
            "and transaction tracking. Requires Further Investigation."
        )
    )

    now = datetime.datetime.now(datetime.timezone.utc)

    new_case = Case(
        case_number=case_number,
        title=title,
        wallet_address=clean_addr,
        blockchain=payload.blockchain.lower(),
        status="Active",
        risk_score=50.0,
        risk_level="MEDIUM",
        created_at=now,
        updated_at=now
    )

    db.add(new_case)
    db.flush()

    new_investigation = Investigation(
        case_id=new_case.id,
        summary=summary,
        created_at=now
    )

    db.add(new_investigation)
    db.commit()
    db.refresh(new_investigation)

    return new_investigation


@router.get(
    "/investigations/{investigation_id}",
    response_model=InvestigationResponse,
    summary="Get investigation details"
)
def get_investigation(
    investigation_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve detailed investigation record by ID."""

    investigation = (
        db.query(Investigation)
        .filter(Investigation.id == investigation_id)
        .first()
    )

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation with ID {investigation_id} not found."
        )

    return investigation


# ============================================================
# Automated Wallet Analysis
# ============================================================

@router.post(
    "/analyze/wallet",
    response_model=WalletAnalysisResponse,
    summary="Perform automated wallet intelligence & risk analysis"
)
async def analyze_wallet(
    payload: WalletAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Automated Blockchain Intelligence & VASP Attribution Engine analysis.

    Performs:
    - Ethereum address validation
    - Blockchain transaction retrieval
    - VASP attribution
    - Risk analysis
    - Transaction risk analysis
    - Fund-flow graph construction
    - AI investigation summary
    """

    clean_addr = payload.wallet_address.strip()
    chain = payload.blockchain.lower()

    # ========================================================
    # 1. Validate blockchain
    # ========================================================

    if chain != "ethereum":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Blockchain '{payload.blockchain}' is not enabled "
                "in Phase 1. Please select 'ethereum'."
            )
        )

    # ========================================================
    # 2. Validate Ethereum address
    # ========================================================

    if not ETH_ADDRESS_REGEX.match(clean_addr):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid Ethereum address format. "
                "Must be a 42-character string starting with '0x'."
            )
        )

    # ========================================================
    # 3. Fetch blockchain data
    # ========================================================

    balance_info = await eth_adapter.get_balance(clean_addr)

    raw_txs = await eth_adapter.get_transactions(clean_addr)

    # ========================================================
    # 4. VASP Attribution
    # ========================================================

    direct_vasp = vasp_service.identify_vasp(
        clean_addr,
        chain
    )

    counterparty_vasp = vasp_service.identify_counterparty_vasp(
        raw_txs,
        clean_addr
    )

    vasp_result = (
        direct_vasp
        if direct_vasp.get("matched")
        else (counterparty_vasp or direct_vasp)
    )

    # ========================================================
    # 5. Risk Indicator Assessment
    # ========================================================

    indicators = risk_service.identify_indicators(
        clean_addr,
        raw_txs,
        vasp_result
    )

    risk_evaluation = risk_service.calculate_wallet_risk(
        indicators
    )

    # ========================================================
    # 6. Map transactions to response format
    # ========================================================

    tx_responses = []

    for tx in raw_txs:

        tx_risk_indicators = (
            risk_service.calculate_transaction_risk(tx)
        )

        # Check if transaction touches a known VASP
        counterparty = (
            tx.get("to_address")
            if tx.get("from_address", "").lower()
            == clean_addr.lower()
            else tx.get("from_address")
        )

        cp_vasp = vasp_service.identify_vasp(
            counterparty or "",
            chain
        )

        vasp_label = (
            cp_vasp.get("name")
            if cp_vasp.get("matched")
            else None
        )

        tx_responses.append(
            TransactionResponse(
                tx_hash=tx["tx_hash"],
                blockchain=chain,
                from_address=tx["from_address"],
                to_address=tx["to_address"],
                amount=tx.get(
                    "value_eth",
                    tx.get("amount", 0.0)
                ),
                token=tx.get("token", "ETH"),
                timestamp=tx.get(
                    "timestamp",
                    tx.get("timestamp_iso")
                ),
                direction=tx["direction"],
                risk_indicators=tx_risk_indicators,
                vasp_attribution=vasp_label
            )
        )

    # ========================================================
    # 7. AI Investigation Summary
    # ========================================================
    #
    # Phase 7:
    # Convert the existing blockchain/risk/VASP findings
    # into a structured investigation summary.
    #
    # This is DEMO/MVP deterministic AI-style analysis.
    # It does not make criminal conclusions.
    # ========================================================

    ai_investigation = (
        ai_investigation_service.generate_summary(
            wallet_address=clean_addr,
            blockchain=chain,
            risk_evaluation=risk_evaluation,
            vasp_attribution=vasp_result,
            transactions=raw_txs
        )
    )

    # ========================================================
    # 8. Build React Flow graph topology
    # ========================================================

    intermediate_a = (
        "0x742d35cc6634c0532925a3b844bc454e4438f44e"
    )

    intermediate_b = (
        "0x89205a3e3b2db69dce6aa645f778d655fba73bfa"
    )

    binance_vasp = (
        "0x28c6c06298d514db089934071355e5743bf21d60"
    )

    nodes = [
        {
            "id": "node-target",
            "type": "customNode",
            "data": {
                "label": "Analyzed Subject Wallet",
                "sublabel": (
                    f"{clean_addr[:8]}..."
                    f"{clean_addr[-6:]}"
                ),
                "fullAddress": clean_addr,
                "role": "Subject Under Review",
                "riskLevel": risk_evaluation["risk_level"],
                "riskScore": risk_evaluation["risk_score"],
                "isTarget": True
            },
            "position": {
                "x": 250,
                "y": 50
            }
        },
        {
            "id": "node-wallet-a",
            "type": "customNode",
            "data": {
                "label": "Wallet A (Intermediary Hop)",
                "sublabel": (
                    f"{intermediate_a[:8]}..."
                    f"{intermediate_a[-6:]}"
                ),
                "fullAddress": intermediate_a,
                "role": "Pass-Through Intermediary",
                "riskLevel": "MEDIUM",
                "riskScore": 62.0,
                "isTarget": False
            },
            "position": {
                "x": 250,
                "y": 200
            }
        },
        {
            "id": "node-wallet-b",
            "type": "customNode",
            "data": {
                "label": "Wallet B (Dispersal Node)",
                "sublabel": (
                    f"{intermediate_b[:8]}..."
                    f"{intermediate_b[-6:]}"
                ),
                "fullAddress": intermediate_b,
                "role": "Split Endpoint",
                "riskLevel": "HIGH",
                "riskScore": 74.0,
                "isTarget": False
            },
            "position": {
                "x": 100,
                "y": 360
            }
        },
        {
            "id": "node-vasp",
            "type": "customNode",
            "data": {
                "label": "VASP Destination (Exchange)",
                "sublabel": "Demo Binance Hot Wallet",
                "fullAddress": binance_vasp,
                "role": "Centralized Exchange (CEX)",
                "riskLevel": "LOW",
                "riskScore": 15.0,
                "isTarget": False,
                "isVASP": True
            },
            "position": {
                "x": 420,
                "y": 360
            }
        }
    ]

    edges = [
        {
            "id": "edge-target-a",
            "source": "node-target",
            "target": "node-wallet-a",
            "animated": True,
            "label": "25.0 ETH",
            "style": {
                "stroke": "#f59e0b",
                "strokeWidth": 2
            }
        },
        {
            "id": "edge-a-b",
            "source": "node-wallet-a",
            "target": "node-wallet-b",
            "animated": True,
            "label": "12.5 ETH",
            "style": {
                "stroke": "#ef4444",
                "strokeWidth": 2
            }
        },
        {
            "id": "edge-a-vasp",
            "source": "node-wallet-a",
            "target": "node-vasp",
            "animated": True,
            "label": "12.5 ETH (Off-ramp)",
            "style": {
                "stroke": "#10b981",
                "strokeWidth": 2
            }
        }
    ]

    # ========================================================
    # 9. Return complete analysis
    # ========================================================

    return WalletAnalysisResponse(
        disclaimer=settings.DATA_MODE,

        wallet_address=clean_addr,

        blockchain=chain,

        wallet_type=(
            "Contract / Scripted Account"
            if clean_addr.endswith("0")
            else "External Owned Account (EOA)"
        ),

        balance=balance_info["balance"],

        token_symbol="ETH",

        total_transactions_analyzed=len(raw_txs),

        risk_score=risk_evaluation["risk_score"],

        risk_level=risk_evaluation["risk_level"],

        risk_indicators=[
            RiskIndicator(
                category=ind["category"],
                indicator=ind["indicator"],
                severity=ind["severity"],
                description=ind["description"]
            )
            for ind in indicators
        ],

        possible_typologies=(
            risk_evaluation["possible_typologies"]
        ),

        vasp_attribution=VASPAttribution(
            matched=vasp_result["matched"],
            name=vasp_result.get("name"),
            type=vasp_result.get("type"),
            blockchain=vasp_result.get("blockchain"),
            address=vasp_result.get("address"),
            confidence=vasp_result.get("confidence", 0.0),
            source=vasp_result.get(
                "source",
                "DEMO Registry"
            ),
            attribution_notes=vasp_result.get(
                "attribution_notes"
            )
        ),

        recent_transactions=tx_responses,

        graph_nodes=nodes,

        graph_edges=edges,
        ai_investigation=ai_investigation,
        created_at=datetime.datetime.now(
            datetime.timezone.utc
        )
    )
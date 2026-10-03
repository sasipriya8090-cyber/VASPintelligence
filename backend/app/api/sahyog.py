from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/sahyog",
    tags=["SAHYOG Integration"],
)


class SAHYOGRequest(BaseModel):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    blockchain: str = Field(default="ethereum")
    vasp_name: Optional[str] = None
    vasp_confidence: Optional[float] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    case_reference: Optional[str] = None
    request_type: str = Field(
        default="VASP_DISCLOSURE_REQUEST"
    )


class SAHYOGResponse(BaseModel):
    success: bool
    request_id: str
    status: str
    message: str
    portal: str
    data_mode: str
    request: Dict[str, Any]


@router.post(
    "/request",
    response_model=SAHYOGResponse,
)
def create_sahyog_request(payload: SAHYOGRequest):
    """
    Create a demo SAHYOG routing request.

    This endpoint does not make a real connection to the
    SAHYOG portal. It creates a synthetic routing record
    for hackathon demonstration purposes.
    """

    wallet = payload.wallet_address.strip()

    if not wallet.startswith("0x") or len(wallet) != 42:
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum wallet address.",
        )

    request_id = (
        "SAHYOG-DEMO-"
        + wallet[-8:].upper()
    )

    return SAHYOGResponse(
        success=True,
        request_id=request_id,
        status="READY_FOR_LAWFUL_SUBMISSION",
        message=(
            "Investigation package routed to the "
            "appropriate VASP workflow."
        ),
        portal="SAHYOG",
        data_mode="DEMO — SYNTHETIC SAHYOG ROUTING",
        request={
            "wallet_address": wallet,
            "blockchain": payload.blockchain,
            "vasp_name": payload.vasp_name,
            "vasp_confidence": payload.vasp_confidence,
            "risk_score": payload.risk_score,
            "risk_level": payload.risk_level,
            "case_reference": payload.case_reference,
            "request_type": payload.request_type,
        },
    )


@router.get("/status")
def sahyog_status():
    """
    Return SAHYOG integration status.
    """

    return {
        "integration": "SAHYOG",
        "status": "AVAILABLE",
        "connected": False,
        "mode": "DEMO",
        "message": (
            "SAHYOG routing support is available in "
            "synthetic demo mode. No live portal connection "
            "is configured."
        ),
    }
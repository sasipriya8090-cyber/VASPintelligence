from typing import Dict, Any, List


class AIInvestigationService:
    """
    Investigation summary service.

    Generates a structured, compliance-safe investigation summary
    from existing blockchain analysis results.

    This is a deterministic MVP service and does not claim
    autonomous law-enforcement conclusions.
    """

    def generate_summary(
        self,
        wallet_address: str,
        blockchain: str,
        risk_evaluation: Dict[str, Any],
        vasp_attribution: Dict[str, Any],
        transactions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:

        risk_score = risk_evaluation.get("risk_score", 0)
        risk_level = risk_evaluation.get("risk_level", "LOW")
        indicators = risk_evaluation.get("indicators", [])
        typologies = risk_evaluation.get("possible_typologies", [])

        vasp_matched = vasp_attribution.get("matched", False)
        vasp_name = vasp_attribution.get("name", "No known VASP identified")
        vasp_confidence = vasp_attribution.get("confidence")

        key_findings = []

        if risk_level in {"HIGH", "CRITICAL"}:
            key_findings.append(
                f"Risk assessment is {risk_level} with a score of {risk_score}/100."
            )

        if indicators:
            key_findings.append(
                f"{len(indicators)} risk indicator(s) were identified "
                "during the wallet assessment."
            )

        if vasp_matched:
            confidence_text = (
                f"{vasp_confidence}%"
                if vasp_confidence is not None
                else "available confidence"
            )
            key_findings.append(
                f"Potential VASP attribution: {vasp_name} "
                f"(confidence: {confidence_text})."
            )
        else:
            key_findings.append(
                "No known VASP attribution was identified in the available registry."
            )

        if transactions:
            key_findings.append(
                f"{len(transactions)} transaction record(s) were considered "
                "for this assessment."
            )

        summary_text = (
            f"The wallet {wallet_address} on {blockchain} was assessed using "
            "available transaction, risk, and VASP attribution data. "
            f"The resulting risk classification is {risk_level} "
            f"with a score of {risk_score}/100. "
            "The findings represent potential risk indicators and possible "
            "transaction typologies and require further investigation."
        )

        next_steps = [
            "Review the identified transaction paths and intermediary wallets.",
            "Validate the VASP attribution against authoritative intelligence sources.",
            "Review the identified risk indicators and possible typologies.",
            "Conduct further investigation before taking any enforcement action.",
        ]

        return {
            "wallet_address": wallet_address,
            "blockchain": blockchain,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "summary": summary_text,
            "key_findings": key_findings,
            "risk_indicators": indicators,
            "possible_typologies": typologies,
            "vasp_attribution": {
                "matched": vasp_matched,
                "name": vasp_name,
                "confidence": vasp_confidence,
            },
            "transaction_count": len(transactions),
            "recommended_next_steps": next_steps,
            "status": "Requires Further Investigation",
            "data_mode": "DEMO — SYNTHETIC INVESTIGATION DATA",
        }
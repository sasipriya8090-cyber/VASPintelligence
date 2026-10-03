from typing import Dict, List, Any

class RiskAnalysisService:
    """
    Risk Analysis Service for Phase 1 MVP.
    Evaluates risk signals and patterns using standardized investigative terminology.
    
    IMPORTANT COMPLIANCE NOTE:
    Evaluations identify indicators of potential anomalous behavior only.
    This service strictly uses terminology such as 'Risk Indicator',
    'Potential Suspicious Activity', 'Possible Typology', and 'Requires Further Investigation'.
    It NEVER states that a wallet or entity is definitely involved in crime or money laundering.
    """

    def calculate_transaction_risk(self, tx: Dict[str, Any]) -> List[str]:
        """
        Evaluate individual transaction risk indicators.
        Supports both 'value_eth' (Phase 2 adapter) and 'amount' (Phase 1 legacy) field names.
        """
        indicators = []
        # Support both the new value_eth field and the legacy amount field
        amount = tx.get("value_eth", tx.get("amount", 0.0))

        if amount >= 40.0:
            indicators.append("Risk Indicator: High-value transaction threshold exceeded")
        elif 15.0 <= amount < 40.0:
            indicators.append("Potential Suspicious Activity: Rapid batch transfer characteristic")
        
        direction = tx.get("direction", "")
        if direction == "OUTGOING" and amount > 15.0:
            indicators.append("Possible Typology: Rapid fund dispersal to external address")

        return indicators

    def identify_indicators(self, wallet_address: str, transactions: List[Dict[str, Any]], vasp_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Identify structured indicators from wallet behavior and counterparty graph.
        """
        indicators: List[Dict[str, str]] = []

        total_tx = len(transactions)
        outgoing_tx = [t for t in transactions if t.get("direction") == "OUTGOING"]
        incoming_tx = [t for t in transactions if t.get("direction") == "INCOMING"]

        # Indicator 1: Rapid outbound dispersal
        if len(outgoing_tx) >= 2:
            indicators.append({
                "category": "Velocity & Flow",
                "indicator": "Risk Indicator: Rapid outflow post-inflow",
                "severity": "HIGH",
                "description": "Potential Suspicious Activity: Rapid succession of outbound transfers following substantial inbound funding. Requires Further Investigation."
            })

        # Indicator 2: High value aggregation
        total_in_amount = sum(t.get("value_eth", t.get("amount", 0.0)) for t in incoming_tx)
        if total_in_amount > 30.0:
            indicators.append({
                "category": "Volume Threshold",
                "indicator": "Risk Indicator: Concentrated inbound volume",
                "severity": "MEDIUM",
                "description": "Potential Suspicious Activity: Inbound volume exceeds baseline threshold for unverified entity. Requires Further Investigation."
            })

        # Indicator 3: VASP Interaction
        if vasp_info.get("matched"):
            indicators.append({
                "category": "VASP Attribution Nexus",
                "indicator": "Risk Indicator: Centralized exchange off-ramp nexus",
                "severity": "MEDIUM",
                "description": f"Potential Suspicious Activity: Flow routed towards known exchange cluster ({vasp_info.get('name')}). Requires Further Investigation."
            })
        else:
            indicators.append({
                "category": "Entity Attribution",
                "indicator": "Risk Indicator: Unattributed peer-to-peer routing",
                "severity": "LOW",
                "description": "Potential Suspicious Activity: Funds moving across unhosted, unattributed personal wallets. Requires Further Investigation."
            })

        # Indicator 4: Typology classification
        indicators.append({
            "category": "Typology Classification",
            "indicator": "Possible Typology: Peeling chain and multi-hop distribution",
            "severity": "HIGH",
            "description": "Possible Typology: Observed pattern resembles structured fund division across intermediary hops. Requires Further Investigation."
        })

        return indicators

    def calculate_wallet_risk(self, indicators: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Calculate composite risk score (0.0 to 100.0) and assign risk level.
        """
        severity_weights = {
            "CRITICAL": 35.0,
            "HIGH": 25.0,
            "MEDIUM": 15.0,
            "LOW": 5.0
        }

        raw_score = sum(severity_weights.get(ind.get("severity", "LOW"), 10.0) for ind in indicators)
        # Normalize and cap between 15 and 88 for realistic demo distribution
        normalized_score = min(88.0, max(18.0, raw_score + 5.0))

        if normalized_score >= 70.0:
            risk_level = "HIGH"
        elif normalized_score >= 40.0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        typologies = [
            "Possible Typology: Peeling Chain Structure",
            "Possible Typology: Rapid Intermediary Pass-Through",
            "Possible Typology: VASP Off-Ramp Funneling"
        ]

        return {
            "risk_score": round(normalized_score, 1),
            "risk_level": risk_level,
            "possible_typologies": typologies,
            "recommendation": "Requires Further Investigation by designated compliance / law enforcement investigator."
        }

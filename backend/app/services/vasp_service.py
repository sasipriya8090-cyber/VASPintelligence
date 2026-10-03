import os
import csv
from typing import Optional, Dict, Any, List

class VASPAttributionService:
    """
    VASP Attribution Service for Phase 1 MVP.
    Identifies Virtual Asset Service Providers (exchanges, payment processors, DEXes)
    based on curated demo registry entries.
    
    DISCLAIMER: All attributions in Phase 1 use DEMO DATA and must not be construed
    as verified real-world entity claims.
    """

    def __init__(self, csv_path: str = None):
        if not csv_path:
            # Look up relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            csv_path = os.path.join(base_dir, "data", "vasp_addresses.csv")
            if not os.path.exists(csv_path):
                # Fallback path if run from backend folder
                csv_path = os.path.join(os.getcwd(), "data", "vasp_addresses.csv")
        
        self.csv_path = csv_path
        self._registry: Dict[str, Dict[str, Any]] = {}
        self.load_registry()

    def load_registry(self) -> None:
        """Load demo VASP addresses from CSV into memory."""
        if not os.path.exists(self.csv_path):
            return

        try:
            with open(self.csv_path, mode="r", encoding="utf-8") as f:
                valid_lines = [line for line in f if line.strip() and not line.strip().startswith("#")]
                reader = csv.DictReader(valid_lines)
                for row in reader:
                    addr = row.get("address", "").strip().lower()
                    if addr:
                        self._registry[addr] = {
                            "name": row.get("name", "Unknown VASP (Demo)"),
                            "type": row.get("type", "Unknown Entity"),
                            "blockchain": row.get("blockchain", "ethereum").lower(),
                            "source": row.get("source", "DEMO Registry"),
                            "confidence": float(row.get("confidence", 0.85))
                        }
        except Exception as e:
            print(f"[VASPAttributionService] Warning reading CSV: {e}")

    def calculate_confidence(self, match_type: str, raw_confidence: float = 0.90, cluster_matches: int = 1) -> float:
        """
        Calculate algorithmic attribution confidence based on heuristic indicators.
        In Phase 1, weights direct match vs counterparty deposit cluster.
        """
        if match_type == "direct_deposit_pool":
            score = min(0.99, raw_confidence)
        elif match_type == "counterparty_nexus":
            score = min(0.92, raw_confidence * 0.95 + (0.02 * cluster_matches))
        else:
            score = 0.70
        return round(score, 2)

    def identify_vasp(self, address: str, blockchain: str = "ethereum") -> Dict[str, Any]:
        """
        Identify whether a specific address belongs to a known VASP.
        Returns attribution metadata including disclaimer.
        """
        addr_clean = address.strip().lower()
        chain_clean = blockchain.strip().lower()

        if addr_clean in self._registry:
            entry = self._registry[addr_clean]
            if entry["blockchain"] == chain_clean:
                confidence = self.calculate_confidence("direct_deposit_pool", entry["confidence"])
                return {
                    "matched": True,
                    "name": entry["name"],
                    "type": entry["type"],
                    "blockchain": entry["blockchain"],
                    "address": address,
                    "confidence": confidence,
                    "source": entry["source"],
                    "attribution_notes": f"DEMO MATCH: Direct identification against synthetic {entry['name']} cluster."
                }

        return {
            "matched": False,
            "name": None,
            "type": "Unattributed / Unhosted Wallet",
            "blockchain": blockchain,
            "address": address,
            "confidence": 0.0,
            "source": "DEMO Registry",
            "attribution_notes": "No known synthetic VASP cluster associated with this specific address."
        }

    def identify_counterparty_vasp(self, transactions: List[Dict[str, Any]], target_address: str) -> Optional[Dict[str, Any]]:
        """
        Identify if any counterparties in the transaction history belong to a known VASP (e.g. Cashout / Deposit point).
        """
        target_lower = target_address.strip().lower()
        for tx in transactions:
            from_addr = tx.get("from_address", "").strip().lower()
            to_addr = tx.get("to_address", "").strip().lower()

            # Check outgoing counterparty
            counterparty = to_addr if from_addr == target_lower else from_addr
            if counterparty in self._registry:
                entry = self._registry[counterparty]
                return {
                    "matched": True,
                    "name": entry["name"],
                    "type": entry["type"],
                    "blockchain": entry["blockchain"],
                    "address": counterparty,
                    "confidence": self.calculate_confidence("counterparty_nexus", entry["confidence"]),
                    "source": entry["source"],
                    "attribution_notes": f"DEMO NEXUS: Target interacts directly with synthetic VASP endpoint ({entry['name']})."
                }
        return None

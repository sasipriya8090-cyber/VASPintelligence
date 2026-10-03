import os
import csv
import datetime
from sqlalchemy.orm import Session
from app.database.session import engine, SessionLocal, Base
from app.models.models import Case, Wallet, Transaction, VASP, Investigation

def init_database():
    """Initializes tables and populates initial demo seed records."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 1. Seed VASPs from CSV if empty
        vasp_count = db.query(VASP).count()
        if vasp_count == 0:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data", "vasp_addresses.csv")
            if not os.path.exists(csv_path):
                csv_path = os.path.join(os.getcwd(), "data", "vasp_addresses.csv")
            
            if os.path.exists(csv_path):
                with open(csv_path, mode="r", encoding="utf-8") as f:
                    valid_lines = [line for line in f if line.strip() and not line.strip().startswith("#")]
                    reader = csv.DictReader(valid_lines)
                    for row in reader:
                        addr = row.get("address", "").strip()
                        if addr:
                            vasp = VASP(
                                name=row.get("name", "Unknown VASP"),
                                type=row.get("type", "CEX"),
                                blockchain=row.get("blockchain", "ethereum"),
                                address=addr.lower(),
                                source=row.get("source", "DEMO Registry"),
                                confidence=float(row.get("confidence", 0.90))
                            )
                            db.add(vasp)
                db.commit()
                print("[init_db] Seeded demo VASP addresses from CSV.")

        # 2. Seed initial demo cases if empty
        case_count = db.query(Case).count()
        if case_count == 0:
            now = datetime.datetime.now(datetime.timezone.utc)
            demo_cases = [
                {
                    "case_number": "CASE-2026-001",
                    "title": "Suspected Peel-Chain Dispersal via Mixer Hop",
                    "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
                    "blockchain": "ethereum",
                    "status": "Active",
                    "risk_score": 78.5,
                    "risk_level": "HIGH",
                    "summary": "Initial intelligence trigger indicated rapid split-distribution of 42.5 ETH across intermediate non-custodial addresses followed by cash-out routing to exchange deposit addresses. Requires Further Investigation."
                },
                {
                    "case_number": "CASE-2026-002",
                    "title": "Unattributed Multi-Hop Flash Funding Cluster",
                    "wallet_address": "0x3cda2097645d52be2250bc33abdb5ac87124f56b",
                    "blockchain": "ethereum",
                    "status": "Under Review",
                    "risk_score": 64.0,
                    "risk_level": "MEDIUM",
                    "summary": "Intermediate wallet associated with high-frequency token swaps and bridge hops. Attribution indicates connection with decentralized liquidity routers. Requires Further Investigation."
                },
                {
                    "case_number": "CASE-2026-003",
                    "title": "High-Volume Liquidity Funnel to CEX Cluster",
                    "wallet_address": "0x28c6c06298d514db089934071355e5743bf21d60",
                    "blockchain": "ethereum",
                    "status": "Active",
                    "risk_score": 82.0,
                    "risk_level": "CRITICAL",
                    "summary": "Known high-volume exchange counterparty nexus. Analyzed for potential mule clustering and rapid structuring outflows. Requires Further Investigation."
                },
                {
                    "case_number": "CASE-2026-004",
                    "title": "Routine Institutional Treasury Audit",
                    "wallet_address": "0x503828976d22510aad0201ac7ec88293211d23dc",
                    "blockchain": "ethereum",
                    "status": "Closed",
                    "risk_score": 22.0,
                    "risk_level": "LOW",
                    "summary": "Baseline assessment of verified institutional custody pool. Normal behavioral heuristics identified."
                }
            ]

            for c_data in demo_cases:
                summary = c_data.pop("summary")
                case = Case(
                    case_number=c_data["case_number"],
                    title=c_data["title"],
                    wallet_address=c_data["wallet_address"],
                    blockchain=c_data["blockchain"],
                    status=c_data["status"],
                    risk_score=c_data["risk_score"],
                    risk_level=c_data["risk_level"],
                    created_at=now - datetime.timedelta(days=demo_cases.index(c_data)),
                    updated_at=now
                )
                db.add(case)
                db.flush()

                # Add corresponding investigation
                inv = Investigation(
                    case_id=case.id,
                    summary=summary,
                    created_at=now - datetime.timedelta(days=demo_cases.index(c_data))
                )
                db.add(inv)

                # Add sample transaction
                tx = Transaction(
                    case_id=case.id,
                    tx_hash=f"0x{hash(case.case_number) & 0xffffffffffffffff:016x}{'a' * 48}",
                    blockchain=case.blockchain,
                    from_address="0x742d35cc6634c0532925a3b844bc454e4438f44e",
                    to_address=case.wallet_address,
                    amount=35.5,
                    token="ETH",
                    timestamp=now - datetime.timedelta(hours=6),
                    direction="INCOMING"
                )
                db.add(tx)

            db.commit()
            print("[init_db] Seeded initial demo cases and investigations.")

    finally:
        db.close()

if __name__ == "__main__":
    init_database()

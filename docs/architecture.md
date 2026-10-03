# System Architecture & Technical Specification

## Project: Automated Blockchain Intelligence & VASP Attribution Engine (Phase 1)

### 1. Architectural Overview

The Automated Blockchain Intelligence & VASP Attribution Engine is an investigative platform engineered to assist cybersecurity analysts, financial intelligence units (FIUs), and law enforcement agencies with cryptocurrency tracing, entity attribution, and risk scoring.

The platform follows a modular, decoupled architecture where:
- Raw blockchain data queries are decoupled from analytical logic via the `BlockchainAdapter` interface.
- Entity clustering is handled independently by the `VASPAttributionService`.
- Risk evaluation is managed by the `RiskAnalysisService` utilizing standardized investigative terminology.
- State is persisted in SQLite via SQLAlchemy ORM.
- The presentation layer is an interactive Single Page Application built on React, Tailwind CSS, and React Flow.

```
+-------------------------------------------------------------------------+
|                  Presentation Layer (React + Vite + Tailwind)           |
|  +--------------------+---------------------+------------------------+  |
|  |     Dashboard      |    Investigation    |      Wallet Graph      |  |
|  | (Metrics & Cases)  |  (Ad-hoc Profiling) |  (React Flow Tracing)  |  |
|  +--------------------+---------------------+------------------------+  |
|  |     Transactions   |       Reports       |    Demo Disclaimers    |  |
|  |   (Ledger Audit)   | (Dossier Briefings) | (Standardized Notice)  |  |
|  +--------------------+---------------------+------------------------+  |
+------------------------------------+------------------------------------+
                                     | JSON REST via HTTP / Vite Proxy
+------------------------------------v------------------------------------+
|                      FastAPI Application (Port 8000)                    |
|  +-------------------------------------------------------------------+  |
|  |                     Endpoints & Request Validation                 |  |
|  |  GET /api/health | POST /api/investigations | POST /analyze/wallet |  |
|  +-------------------------------------------------------------------+  |
|                                    |                                    |
|       +----------------------------+----------------------------+       |
|       |                                                         |       |
|  +----v--------------------+                             +------v----+  |
|  |   Core Analytical Logic |                             | Database  |  |
|  | +---------------------+ |                             | (SQLite + |  |
|  | | VASPAttributionSvc  | |                             |SQLAlchemy)|  |
|  | +---------------------+ |                             |           |  |
|  | | RiskAnalysisSvc     | |                             |  • Cases  |  |
|  | +---------------------+ |                             |  • Wallets|  |
|  |                         |                             |  • Txns   |  |
|  | Blockchain Adapters     |                             |  • VASPs  |  |
|  | +---------------------+ |                             |  • Invs   |  |
|  | | BlockchainAdapter   | |                             +-----------+  |
|  | | (Interface)         | |                                            |
|  | +---------------------+ |                                            |
|  | | EthereumAdapter     | |                                            |
|  | | (Demo/Mock Engine)  | |                                            |
|  | +---------------------+ |                                            |
|  +-------------------------+                                            |
+-------------------------------------------------------------------------+
```

---

### 2. Core Modules & Boundaries

#### A. Blockchain Adapter (`app/adapters/`)
- `BlockchainAdapter` (Abstract Base Class): Defines standard contracts:
  - `get_transactions(wallet_address: str) -> List[Dict]`
  - `get_balance(wallet_address: str) -> Dict`
  - `get_transaction(tx_hash: str) -> Dict`
- `EthereumAdapter`: Concrete Phase 1 implementation providing synthetic DEMO ledger records. All returned structures explicitly attach `"data_mode": "DEMO DATA — NOT LIVE BLOCKCHAIN DATA"`.

#### B. VASP Attribution Service (`app/services/vasp_service.py`)
- Responsible for entity mapping across Centralized Exchanges (CEX), DEX routers, and custodial pools.
- Loads synthetic entities from `data/vasp_addresses.csv`.
- Evaluates:
  1. **Direct Deposit Pool Matches**: When the subject wallet matches a known VASP cluster.
  2. **Counterparty Nexus Matches**: When intermediate transfers interact with known off-ramps or deposit points.
- Outputs confidence scores (0.0 to 1.0) and disclaimer metadata.

#### C. Risk Analysis Service (`app/services/risk_service.py`)
- Adheres strictly to non-accusatory investigative guidelines:
  - Standardized Terms: `Risk Indicator`, `Potential Suspicious Activity`, `Possible Typology`, `Requires Further Investigation`.
  - Never asserts definitive criminal guilt or money laundering.
- Heuristics:
  - Velocity and outflow speed post-consolidation.
  - Value thresholds.
  - Multi-hop peel-chain topologies.
  - VASP nexus off-ramp routing.

#### D. Database Models (`app/models/models.py`)
- **Case**: Tracks primary investigative files, risk scores, status, and target wallets.
- **Wallet**: Stores profiled public keys, blockchain identifiers, and wallet classifications.
- **Transaction**: Records granular ledger transfer events, directions, tokens, and timestamps.
- **VASP**: Registry of known synthetic service providers, types, and baseline confidence values.
- **Investigation**: Stores forensic narrative summaries tied to cases.

---

### 3. Interactive Graph Architecture (React Flow)
- Uses `@xyflow/react` to render interactive DAG visualizations of multi-hop asset movement.
- Visualizes:
  - Subject Target Wallet (Origin)
  - Intermediary Pass-Through Nodes (Wallet A)
  - Split Dispersal Leaf Nodes (Wallet B)
  - Attributed VASP Destination (Exchange Off-Ramp)
- Provides zoom, pan, minimap, draggable layouts, and interactive node inspection.

---

### 4. Phase 1 Boundary & Disclaimers
All data generated and rendered in Phase 1 is labeled:
> **"DEMO DATA — NOT LIVE BLOCKCHAIN DATA"**
No real-world third-party exchange or wallet is represented as verified criminal infrastructure.

# Automated Blockchain Intelligence & VASP Attribution Engine

> **PHASE 1 FOUNDATION — 24-HOUR HACKATHON PROJECT**  
> **DISCLAIMER:** DEMO DATA — NOT LIVE BLOCKCHAIN DATA. All transactions, entities, and risk heuristics presented in Phase 1 utilize synthetic mock data for architectural and prototype demonstration purposes only.

---

## 1. Project Overview & Problem Statement

### Problem Domain
**Cybersecurity / Financial Security / Blockchain Forensics / Law Enforcement Intelligence**

Law enforcement and compliance authorities encounter significant bottlenecks when investigating illicit cryptocurrency flows across decentralized networks:
- Obfuscated fund movement through complex peeling chains and multi-hop routing.
- Difficulties attributing pseudonymous addresses to regulated Virtual Asset Service Providers (VASPs).
- Lack of standardized, non-prejudicial risk categorization and typology classification.
- Inability to quickly generate court-ready forensic dossiers and interactive fund-flow graphs.

### Project Mission
The **Automated Blockchain Intelligence & VASP Attribution Engine** is designed to automate cryptocurrency transaction tracing, VASP entity attribution, multi-hop flow visualization, risk scoring, and forensic dossier generation.

---

## 2. Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (Dark Navy / Cyber Forensic Theme)
- **Routing**: React Router DOM (v6)
- **Graph Visualization**: React Flow (`@xyflow/react`)
- **Icons**: Lucide React

### Backend
- **Framework**: Python 3.12 + FastAPI
- **Data Validation**: Pydantic v2
- **ORM / Persistence**: SQLAlchemy 2.0
- **Database**: SQLite (local single-file MVP store)
- **Server**: Uvicorn ASGI

---

## 3. Project Structure

```
VASPintelligence/
├── backend/
│   ├── app/
│   │   ├── adapters/          # Blockchain data abstraction (EthereumAdapter, BlockchainAdapter)
│   │   ├── api/               # REST API route handlers
│   │   ├── core/              # Global settings and CORS configuration
│   │   ├── database/          # SQLite engine, session maker, init_db seed scripts
│   │   ├── models/            # SQLAlchemy database models (Case, Wallet, Tx, VASP, Inv)
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── services/          # VASP attribution & risk heuristic services
│   │   └── main.py            # FastAPI main entrypoint and lifespan events
│   ├── requirements.txt       # Python dependencies
│   └── vasp_intelligence.db   # SQLite local database
├── frontend/
│   ├── src/
│   │   ├── components/        # Layout, Sidebar, Header, RiskBadge, CustomNode, Banners
│   │   ├── pages/             # Dashboard, Investigation, Transactions, WalletGraph, Reports
│   │   ├── services/          # api.js API client
│   │   ├── App.jsx            # React Router route registry
│   │   ├── index.css          # Tailwind CSS & React Flow custom styles
│   │   └── main.jsx           # React DOM root
│   ├── index.html             # Single-page HTML document
│   ├── package.json           # Frontend dependencies
│   ├── tailwind.config.js     # Dark navy & cyber palette configuration
│   └── vite.config.js         # Vite configuration with API proxy
├── data/
│   └── vasp_addresses.csv     # Synthetic DEMO VASP registry
├── docs/
│   ├── architecture.md        # Deep-dive architectural specification
│   └── api.md                 # REST API reference and payload contracts
├── .env.example               # Environment variables template
└── README.md                  # Project documentation
```

---

## 4. Key Architectural Capabilities (Phase 1)

1. **Modular Blockchain Adapter Pattern**:
   Raw blockchain data collection is abstracted through `BlockchainAdapter`, allowing future multichain adapters (Bitcoin, Solana) to plug in seamlessly without touching core analytical logic.
2. **VASP Attribution Engine**:
   Decoupled entity clustering (`VASPAttributionService`) matches wallet addresses and counterparty nodes against regulated exchange deposit pools and DEX routers with confidence scoring.
3. **Forensic Risk & Typology Engine**:
   `RiskAnalysisService` computes composite risk scores (0–100) and extracts structured indicators using strict evidentiary terms:
   - *Risk Indicator*
   - *Potential Suspicious Activity*
   - *Possible Typology*
   - *Requires Further Investigation*
4. **Interactive Fund-Flow Visualizer**:
   React Flow graph modeling multi-hop flows (`Suspicious Wallet → Wallet A → Wallet B → VASP Hot Wallet`) with node inspector and animated edge volumes.
5. **Investigation-Ready Briefings**:
   Formal case reports printable or exportable for compliance auditing and law enforcement review.

---

## 5. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ and npm (tested on Node v24.19.0 / npm 11.17.0)

### Backend Setup
1. Open terminal and navigate to the project directory:
   ```bash
   cd VASPintelligence
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   # Windows PowerShell
   python -m venv backend\.venv
   .\backend\.venv\Scripts\Activate.ps1
   ```
3. Install backend dependencies:
   ```powershell
   .\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
   ```
4. Initialize the SQLite database and seed initial demo cases:
   ```powershell
   & "backend\.venv\Scripts\python.exe" -m app.database.init_db
   ```

### Frontend Setup
1. Open terminal in `frontend/`:
   ```powershell
   cd VASPintelligence\frontend
   ```
2. Install npm dependencies:
   ```powershell
   npm install
   ```

---

## 6. Running the Application

### 1. Start the FastAPI Backend
From `VASPintelligence/backend`:
```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base URL: `http://127.0.0.1:8000`
- Interactive OpenAPI / Swagger Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

### 2. Start the React Frontend
From `VASPintelligence/frontend`:
```powershell
npm run dev
```
- Frontend Web App: `http://localhost:5173`

---

## 7. Environment Variables (`.env.example`)

Copy `.env.example` to `.env` if custom overrides are required:
```ini
APP_NAME="Automated Blockchain Intelligence & VASP Attribution Engine"
APP_ENV=development
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
DATABASE_URL="sqlite:///./vasp_intelligence.db"
DATA_MODE="DEMO"
```

---

## 8. Phase 1 Boundaries & Limitations

- **Synthetic Mock Data Only**: Transactions and balances are generated algorithmically for testing without querying live mainnet nodes.
- **No Live API Keys**: No Infura, Alchemy, or Etherscan keys are utilized or required.
- **Single-Chain Focus**: Ethereum adapter enabled; Bitcoin and Solana interfaces are stubbed for Phase 2.
- **No Direct SAHYOG Integration**: Formal police portal integration will be developed in Phase 2.
- **Heuristic Indicators**: Never assert definitive criminal culpability or money laundering; statements highlight *Potential Suspicious Activity* requiring further investigation.

---

## 9. Future Phases Roadmap

- **Phase 2 — Live Blockchain Ingestion & Multi-Chain Expansion**:
  - Integrate live RPC / indexing nodes for Ethereum, Bitcoin (UTXO model), and Solana.
  - Live Etherscan and Dune Analytics API connectors.
- **Phase 3 — Advanced Agentic AI & Clustering**:
  - LLM-powered autonomous forensic reasoning agent.
  - Heuristic co-spending and common-input-ownership clustering algorithms.
- **Phase 4 — SAHYOG Portal Law Enforcement Integration**:
  - Secure LEA authentication and automated MLAT / 91 CrPC notice generation.
  - Direct VASP contact registry for statutory preservation orders.

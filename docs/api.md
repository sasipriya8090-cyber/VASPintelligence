# REST API Documentation

## Automated Blockchain Intelligence & VASP Attribution Engine

**Base URL**: `http://localhost:8000/api`  
**Interactive Swagger Docs**: `http://localhost:8000/docs`  
**Data Mode**: `DEMO DATA — NOT LIVE BLOCKCHAIN DATA`

---

### 1. Health Check

#### `GET /api/health`
Returns system status, service title, and current data mode.

**Response `200 OK`**:
```json
{
  "status": "healthy",
  "service": "Automated Blockchain Intelligence & VASP Attribution Engine",
  "version": "1.0.0",
  "data_mode": "DEMO DATA — NOT LIVE BLOCKCHAIN DATA",
  "timestamp": "2026-10-03T09:41:07.704582+00:00"
}
```

---

### 2. List Investigations

#### `GET /api/investigations`
Returns paginated list of logged forensic cases and investigation summaries.

**Query Parameters**:
- `skip` (int, default: 0): Records to skip
- `limit` (int, default: 50): Max records to return

**Response `200 OK`**:
```json
[
  {
    "id": 1,
    "case_id": 1,
    "summary": "Initial intelligence trigger indicated rapid split-distribution...",
    "created_at": "2026-10-03T09:30:00Z",
    "case": {
      "id": 1,
      "case_number": "CASE-2026-001",
      "title": "Suspected Peel-Chain Dispersal via Mixer Hop",
      "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
      "blockchain": "ethereum",
      "status": "Active",
      "risk_score": 78.5,
      "risk_level": "HIGH",
      "created_at": "2026-10-03T09:30:00Z",
      "updated_at": "2026-10-03T09:30:00Z"
    }
  }
]
```

---

### 3. Create Investigation Case

#### `POST /api/investigations`
Registers a new forensic case and intake investigation record.

**Request Body**:
```json
{
  "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
  "blockchain": "ethereum",
  "title": "Ad-Hoc Forensic Review",
  "case_number": "CASE-2026-005",
  "summary": "Suspicious fund consolidation identified via external tip."
}
```

**Response `201 Created`**:
```json
{
  "id": 5,
  "case_id": 5,
  "summary": "Suspicious fund consolidation identified via external tip.",
  "created_at": "2026-10-03T09:45:00Z",
  "case": {
    "id": 5,
    "case_number": "CASE-2026-005",
    "title": "Ad-Hoc Forensic Review",
    "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
    "blockchain": "ethereum",
    "status": "Active",
    "risk_score": 50.0,
    "risk_level": "MEDIUM",
    "created_at": "2026-10-03T09:45:00Z",
    "updated_at": "2026-10-03T09:45:00Z"
  }
}
```

---

### 4. Get Investigation by ID

#### `GET /api/investigations/{id}`
Returns investigation record and associated case metadata.

**Response `200 OK`**:
```json
{
  "id": 1,
  "case_id": 1,
  "summary": "Initial intelligence trigger indicated rapid split-distribution...",
  "created_at": "2026-10-03T09:30:00Z",
  "case": { ... }
}
```

---

### 5. Automated Wallet Analysis

#### `POST /api/analyze/wallet`
Core analytical endpoint. Validates subject address, executes adapter ledger inspection (DEMO), performs synthetic VASP attribution, scores risk heuristics, and generates graph topology.

**Request Body**:
```json
{
  "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
  "blockchain": "ethereum"
}
```

**Response `200 OK`**:
```json
{
  "disclaimer": "DEMO DATA — NOT LIVE BLOCKCHAIN DATA",
  "wallet_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
  "blockchain": "ethereum",
  "wallet_type": "External Owned Account (EOA)",
  "balance": 23.45,
  "token_symbol": "ETH",
  "total_transactions_analyzed": 5,
  "risk_score": 75.0,
  "risk_level": "HIGH",
  "risk_indicators": [
    {
      "category": "Velocity & Flow",
      "indicator": "Risk Indicator: Rapid outflow post-inflow",
      "severity": "HIGH",
      "description": "Potential Suspicious Activity: Rapid succession of outbound transfers following substantial inbound funding. Requires Further Investigation."
    }
  ],
  "possible_typologies": [
    "Possible Typology: Peeling Chain Structure",
    "Possible Typology: Rapid Intermediary Pass-Through",
    "Possible Typology: VASP Off-Ramp Funneling"
  ],
  "vasp_attribution": {
    "matched": true,
    "name": "Demo Kraken Deposit Pool",
    "type": "Centralized Exchange (CEX)",
    "blockchain": "ethereum",
    "address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
    "confidence": 0.89,
    "source": "DEMO Registry",
    "attribution_notes": "DEMO MATCH: Direct identification against synthetic Demo Kraken Deposit Pool cluster."
  },
  "recent_transactions": [
    {
      "tx_hash": "0x...",
      "blockchain": "ethereum",
      "from_address": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
      "to_address": "0x71c7656ec7ab88b098defb751b7401b5f6d8976f",
      "amount": 42.5,
      "token": "ETH",
      "timestamp": "2026-10-03T12:45:00Z",
      "direction": "INCOMING",
      "risk_indicators": ["Risk Indicator: High-value transaction threshold exceeded"],
      "vasp_attribution": null
    }
  ],
  "graph_nodes": [ ... ],
  "graph_edges": [ ... ],
  "created_at": "2026-10-03T09:41:07Z"
}
```

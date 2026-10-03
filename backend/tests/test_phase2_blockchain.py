"""
Phase 2 Tests — Ethereum Blockchain Integration.

Tests cover:
  1. EthereumAdapter address validation
  2. EthereumAdapter DEMO mode (no API key needed)
  3. Transaction normalization (_normalize_etherscan_tx)
  4. Blockchain API endpoints via FastAPI TestClient:
     - GET /api/blockchain/config/status
     - GET /api/blockchain/ethereum/address/{address}/transactions
       * valid address → 200 with demo data
       * invalid address → 400
       * pagination params
  5. Error handling (RateLimitError, ProviderTimeoutError, ProviderError)
  6. In-process cache behaviour

All tests run fully offline — no real Etherscan calls are made.
"""
import datetime
import time
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# ─── App import ─────────────────────────────────────────────────────────────
from app.main import app
from app.adapters.ethereum import (
    EthereumAdapter,
    RateLimitError,
    ProviderTimeoutError,
    ProviderError,
    InvalidAddressError,
)
from app.api import blockchain as blockchain_module

# ─── Shared test addresses ───────────────────────────────────────────────────

VALID_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
VALID_ADDRESS_2 = "0x28C6c06298d514Db089934071355E5743Bf21d60"
INVALID_ADDRESS_SHORT = "0x742d35"
INVALID_ADDRESS_NO_PREFIX = "742d35cc6634c0532925a3b844bc454e4438f44e"
INVALID_ADDRESS_SPACES = "  0x742d35Cc6634C0532925a3b844Bc454e4438f44e  "


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_blockchain_cache():
    """Ensure cache is empty before every test."""
    blockchain_module._cache.clear()
    yield
    blockchain_module._cache.clear()


@pytest.fixture()
def client():
    """FastAPI test client (synchronous — TestClient wraps ASGI)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def adapter():
    """A fresh EthereumAdapter instance for unit tests."""
    return EthereumAdapter()


# ═══════════════════════════════════════════════════════════════════════════
# 1. Address Validation
# ═══════════════════════════════════════════════════════════════════════════

class TestAddressValidation:
    """Unit tests for EthereumAdapter.validate_address."""

    def test_valid_lowercase_address(self, adapter):
        assert adapter.validate_address("0x742d35cc6634c0532925a3b844bc454e4438f44e") is True

    def test_valid_mixed_case_address(self, adapter):
        assert adapter.validate_address(VALID_ADDRESS) is True

    def test_valid_all_uppercase(self, adapter):
        assert adapter.validate_address("0x742D35CC6634C0532925A3B844BC454E4438F44E") is True

    def test_invalid_too_short(self, adapter):
        assert adapter.validate_address(INVALID_ADDRESS_SHORT) is False

    def test_invalid_no_0x_prefix(self, adapter):
        assert adapter.validate_address(INVALID_ADDRESS_NO_PREFIX) is False

    def test_invalid_empty_string(self, adapter):
        assert adapter.validate_address("") is False

    def test_invalid_non_hex_chars(self, adapter):
        # 'g' is not a hex character
        assert adapter.validate_address("0x742d35cc6634c0532925a3b844bc454e4438g44e") is False

    def test_invalid_too_long(self, adapter):
        assert adapter.validate_address("0x742d35cc6634c0532925a3b844bc454e4438f44e00") is False

    def test_strips_whitespace(self, adapter):
        # validate_address strips before matching
        assert adapter.validate_address("  0x742d35cc6634c0532925a3b844bc454e4438f44e  ") is True


# ═══════════════════════════════════════════════════════════════════════════
# 2. DEMO Mode (no API key configured)
# ═══════════════════════════════════════════════════════════════════════════

class TestDemoMode:
    """Tests that DEMO mode returns sane deterministic synthetic data."""

    @pytest.mark.asyncio
    async def test_demo_get_balance_returns_dict(self, adapter):
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            result = await adapter.get_balance(VALID_ADDRESS)
        assert isinstance(result, dict)
        assert "balance" in result
        assert result["blockchain"] == "ethereum"
        assert result["token"] == "ETH"

    @pytest.mark.asyncio
    async def test_demo_get_balance_has_disclaimer(self, adapter):
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            result = await adapter.get_balance(VALID_ADDRESS)
        # DEMO responses carry a disclaimer field
        assert "DEMO" in result.get("data_mode", "") or "DEMO" in result.get("disclaimer", "")

    @pytest.mark.asyncio
    async def test_demo_get_transactions_returns_list(self, adapter):
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            txs = await adapter.get_transactions(VALID_ADDRESS)
        assert isinstance(txs, list)
        assert len(txs) > 0

    @pytest.mark.asyncio
    async def test_demo_transactions_have_required_fields(self, adapter):
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            txs = await adapter.get_transactions(VALID_ADDRESS)
        for tx in txs:
            assert "tx_hash" in tx
            assert "from_address" in tx
            assert "to_address" in tx
            assert "value_eth" in tx
            assert "direction" in tx
            assert tx["blockchain"] == "ethereum"

    @pytest.mark.asyncio
    async def test_demo_directions_are_valid(self, adapter):
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            txs = await adapter.get_transactions(VALID_ADDRESS)
        valid_directions = {"INCOMING", "OUTGOING", "INTERNAL"}
        for tx in txs:
            assert tx["direction"] in valid_directions

    @pytest.mark.asyncio
    async def test_demo_get_transaction_by_hash(self, adapter):
        sample_hash = "0x" + "a" * 64
        with patch.object(type(adapter), "is_live", new_callable=lambda: property(lambda self: False)):
            result = await adapter.get_transaction(sample_hash)
        assert result is not None
        assert result["tx_hash"] == sample_hash


# ═══════════════════════════════════════════════════════════════════════════
# 3. Transaction Normalization
# ═══════════════════════════════════════════════════════════════════════════

class TestTransactionNormalization:
    """Unit tests for _normalize_etherscan_tx."""

    RAW_TX = {
        "hash": "0xabc123",
        "from": "0x742d35cc6634c0532925a3b844bc454e4438f44e",
        "to": "0x28c6c06298d514db089934071355e5743bf21d60",
        "value": str(int(1.5 * 1e18)),       # 1.5 ETH in Wei
        "gasUsed": "21000",
        "gasPrice": "20000000000",            # 20 Gwei
        "timeStamp": "1700000000",
        "blockNumber": "19000000",
        "txreceipt_status": "1",
        "confirmations": "150",
    }

    def test_outgoing_direction(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert result["direction"] == "OUTGOING"

    def test_incoming_direction(self, adapter):
        # Flip the perspective: queried wallet is the recipient
        target = "0x28c6c06298d514db089934071355e5743bf21d60"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert result["direction"] == "INCOMING"

    def test_value_conversion_to_eth(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert abs(result["value_eth"] - 1.5) < 1e-6

    def test_gas_fee_calculated(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        expected_fee = round((21000 * 20000000000) / 1e18, 8)
        assert abs(result["gas_fee_eth"] - expected_fee) < 1e-9

    def test_status_confirmed(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert result["status"] == "confirmed"

    def test_status_failed(self, adapter):
        failed_tx = {**self.RAW_TX, "txreceipt_status": "0"}
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(failed_tx, target)
        assert result["status"] == "failed"

    def test_timestamp_iso_format(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        ts = result["timestamp_iso"]
        # Both "+00:00" suffix and "Z" suffix are valid ISO 8601 UTC representations
        assert ts.endswith("Z") or ts.endswith("+00:00"), f"Unexpected timestamp format: {ts}"

    def test_block_number_integer(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert isinstance(result["block_number"], int)
        assert result["block_number"] == 19000000

    def test_data_mode_is_live(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert result["data_mode"] == "LIVE"

    def test_internal_direction_for_unrelated_address(self, adapter):
        unrelated = "0x0000000000000000000000000000000000000001"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, unrelated)
        assert result["direction"] == "INTERNAL"

    def test_confirmations_parsed(self, adapter):
        target = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        result = adapter._normalize_etherscan_tx(self.RAW_TX, target)
        assert result["confirmations"] == 150


# ═══════════════════════════════════════════════════════════════════════════
# 4. Blockchain API Endpoints
# ═══════════════════════════════════════════════════════════════════════════

class TestBlockchainConfigStatus:
    """Tests for GET /api/blockchain/config/status."""

    def test_config_status_200(self, client):
        response = client.get("/api/blockchain/config/status")
        assert response.status_code == 200

    def test_config_status_schema(self, client):
        data = client.get("/api/blockchain/config/status").json()
        assert "ethereum_configured" in data
        assert "ethereum_provider" in data
        assert "data_mode" in data
        assert "max_tx_per_request" in data
        assert "cache_ttl_seconds" in data
        assert "supported_chains" in data
        assert "planned_chains" in data

    def test_supported_chains_contains_ethereum(self, client):
        data = client.get("/api/blockchain/config/status").json()
        assert "ethereum" in data["supported_chains"]

    def test_no_api_key_exposed(self, client):
        """Ensure the raw API key is never in the response body."""
        raw = client.get("/api/blockchain/config/status").text
        # If ETHERSCAN_API_KEY is set, its value must not appear in the response
        from app.core.config import settings
        if settings.ETHERSCAN_API_KEY:
            assert settings.ETHERSCAN_API_KEY not in raw


class TestEthereumAddressTransactions:
    """Tests for GET /api/blockchain/ethereum/address/{address}/transactions."""

    def test_valid_address_returns_200(self, client):
        response = client.get(f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions")
        assert response.status_code == 200

    def test_response_schema(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        assert "wallet_address" in data
        assert "transactions" in data
        assert "data_mode" in data
        assert "provider" in data
        assert "page" in data
        assert "page_size" in data
        assert "transaction_count" in data
        assert "cached" in data
        assert "fetched_at" in data

    def test_transactions_is_list(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        assert isinstance(data["transactions"], list)

    def test_transaction_count_matches_list(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        assert data["transaction_count"] == len(data["transactions"])

    def test_invalid_address_short_returns_400(self, client):
        response = client.get(
            f"/api/blockchain/ethereum/address/{INVALID_ADDRESS_SHORT}/transactions"
        )
        assert response.status_code == 400

    def test_invalid_address_no_prefix_returns_400(self, client):
        response = client.get(
            f"/api/blockchain/ethereum/address/{INVALID_ADDRESS_NO_PREFIX}/transactions"
        )
        assert response.status_code == 400

    def test_invalid_address_error_message(self, client):
        response = client.get(
            f"/api/blockchain/ethereum/address/{INVALID_ADDRESS_SHORT}/transactions"
        )
        body = response.json()
        assert "detail" in body
        assert "Invalid Ethereum address" in body["detail"]

    def test_default_pagination(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        assert data["page"] == 1
        assert data["page_size"] == 25

    def test_custom_page_size(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions?page_size=10"
        ).json()
        assert data["page_size"] == 10

    def test_page_size_capped_at_100(self, client):
        # page_size > 100 should return 422 (FastAPI validation)
        response = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions?page_size=200"
        )
        assert response.status_code == 422

    def test_page_zero_returns_422(self, client):
        response = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions?page=0"
        )
        assert response.status_code == 422

    def test_first_response_not_cached(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        assert data["cached"] is False

    def test_second_response_is_cached(self, client):
        url = f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        client.get(url)               # warm cache
        data = client.get(url).json() # should hit cache
        assert data["cached"] is True

    def test_cache_respects_page_parameter(self, client):
        url_p1 = f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions?page=1"
        url_p2 = f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions?page=2"
        client.get(url_p1)
        # Different page should NOT be cached
        data2 = client.get(url_p2).json()
        assert data2["cached"] is False

    def test_normalized_transaction_fields(self, client):
        data = client.get(
            f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
        ).json()
        txs = data["transactions"]
        if txs:
            tx = txs[0]
            assert "tx_hash" in tx
            assert "blockchain" in tx
            assert "from_address" in tx
            assert "to_address" in tx
            assert "value_eth" in tx
            assert "direction" in tx
            assert "status" in tx
            assert "data_mode" in tx


# ═══════════════════════════════════════════════════════════════════════════
# 5. Error Handling (mock adapter to inject errors)
# ═══════════════════════════════════════════════════════════════════════════

class TestErrorHandling:
    """Tests that adapter errors map to correct HTTP status codes."""

    def test_rate_limit_error_returns_429(self, client):
        with patch.object(
            blockchain_module._eth_adapter,
            "get_transactions",
            new=AsyncMock(side_effect=RateLimitError("Rate limited")),
        ):
            response = client.get(
                f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
            )
        assert response.status_code == 429

    def test_rate_limit_includes_retry_after_header(self, client):
        with patch.object(
            blockchain_module._eth_adapter,
            "get_transactions",
            new=AsyncMock(side_effect=RateLimitError("Rate limited")),
        ):
            response = client.get(
                f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
            )
        assert "retry-after" in response.headers

    def test_provider_timeout_returns_503(self, client):
        with patch.object(
            blockchain_module._eth_adapter,
            "get_transactions",
            new=AsyncMock(side_effect=ProviderTimeoutError("Timeout")),
        ):
            response = client.get(
                f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
            )
        assert response.status_code == 503

    def test_provider_error_returns_503(self, client):
        with patch.object(
            blockchain_module._eth_adapter,
            "get_transactions",
            new=AsyncMock(side_effect=ProviderError("Server error")),
        ):
            response = client.get(
                f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
            )
        assert response.status_code == 503

    def test_error_response_has_detail(self, client):
        with patch.object(
            blockchain_module._eth_adapter,
            "get_transactions",
            new=AsyncMock(side_effect=ProviderError("Some provider error")),
        ):
            response = client.get(
                f"/api/blockchain/ethereum/address/{VALID_ADDRESS}/transactions"
            )
        body = response.json()
        assert "detail" in body


# ═══════════════════════════════════════════════════════════════════════════
# 6. Custom Exception Classes
# ═══════════════════════════════════════════════════════════════════════════

class TestExceptionHierarchy:
    """Tests for the custom exception hierarchy in the adapter."""

    def test_rate_limit_is_provider_error(self):
        err = RateLimitError("test")
        assert isinstance(err, ProviderError)

    def test_provider_timeout_is_provider_error(self):
        err = ProviderTimeoutError("test")
        assert isinstance(err, ProviderError)

    def test_invalid_address_is_adapter_error(self):
        from app.adapters.ethereum import AdapterError
        err = InvalidAddressError("bad address")
        assert isinstance(err, AdapterError)


# ═══════════════════════════════════════════════════════════════════════════
# 7. Phase 1 Compatibility (ensure existing endpoints still work)
# ═══════════════════════════════════════════════════════════════════════════

class TestPhase1Compatibility:
    """Smoke tests ensuring Phase 1 endpoints still respond correctly."""

    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "blockchain_status" in data   # new Phase 2 field

    def test_investigations_endpoint(self, client):
        response = client.get("/api/investigations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_analyze_wallet_demo_mode(self, client):
        payload = {"wallet_address": VALID_ADDRESS, "blockchain": "ethereum"}
        response = client.post("/api/analyze/wallet", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "risk_score" in data
        assert "vasp_attribution" in data

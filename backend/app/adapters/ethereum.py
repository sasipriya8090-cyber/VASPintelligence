"""
Ethereum Blockchain Adapter — Phase 2.

Supports TWO operating modes selected automatically at startup:

  LIVE MODE  — when ETHERSCAN_API_KEY is set in environment.
               Queries the real Etherscan API for on-chain data.

  DEMO MODE  — when no API key is configured.
               Returns deterministic, clearly labeled synthetic data
               identical to Phase 1 behavior so existing functionality
               is never broken.

Provider supported: Etherscan (https://docs.etherscan.io/)
Future: Alchemy, Infura (JSON-RPC) may be added as alternatives.
"""
import re
import datetime
import hashlib
import logging
from typing import Dict, List, Any, Optional

import httpx

from app.adapters.base import BlockchainAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEMO_DATA_DISCLAIMER = "DEMO DATA — NOT LIVE BLOCKCHAIN DATA"
ETH_ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

# Etherscan result status codes
ETHERSCAN_OK = "1"
ETHERSCAN_NOTX_MSG = "No transactions found"


class EthereumAdapter(BlockchainAdapter):
    """
    Ethereum Blockchain Adapter.

    Automatically operates in LIVE or DEMO mode based on configuration.
    Never raises on missing API key — gracefully falls back to DEMO data
    with a clear disclaimer attached to every response.
    """

    # -----------------------------------------------------------------------
    # Chain Identification
    # -----------------------------------------------------------------------

    @property
    def chain_name(self) -> str:
        return "ethereum"

    @property
    def is_live(self) -> bool:
        return settings.is_ethereum_configured()

    # -----------------------------------------------------------------------
    # Constructor
    # -----------------------------------------------------------------------

    def __init__(self) -> None:
        self._api_key: Optional[str] = settings.ETHERSCAN_API_KEY
        self._base_url: str = settings.ETHERSCAN_BASE_URL
        self._timeout: int = settings.BLOCKCHAIN_REQUEST_TIMEOUT
        self._max_tx: int = settings.BLOCKCHAIN_MAX_TX_PER_REQUEST

        if self.is_live:
            logger.info(
                "[EthereumAdapter] LIVE MODE — provider: %s",
                settings.get_ethereum_provider_name(),
            )
        else:
            logger.warning(
                "[EthereumAdapter] DEMO MODE — no Ethereum API key configured. "
                "Set ETHERSCAN_API_KEY in your environment to enable real data."
            )

    # -----------------------------------------------------------------------
    # Address Validation
    # -----------------------------------------------------------------------

    def validate_address(self, address: str) -> bool:
        """Return True if address is a valid EIP-55 / 0x-prefixed Ethereum address."""
        return bool(ETH_ADDRESS_RE.match(address.strip()))

    # -----------------------------------------------------------------------
    # Public Interface (async)
    # -----------------------------------------------------------------------

    async def get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Fetch ETH balance. Uses live Etherscan or falls back to demo."""
        if self.is_live:
            return await self._live_get_balance(wallet_address)
        return self._demo_get_balance(wallet_address)

    async def get_transactions(
        self,
        wallet_address: str,
        page: int = 1,
        page_size: int = 25,
    ) -> List[Dict[str, Any]]:
        """Fetch transactions. Uses live Etherscan or falls back to demo."""
        if self.is_live:
            return await self._live_get_transactions(wallet_address, page, page_size)
        return self._demo_get_transactions(wallet_address)

    async def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Fetch a single transaction by hash. Uses live Etherscan or falls back to demo."""
        if self.is_live:
            return await self._live_get_transaction(tx_hash)
        return self._demo_get_transaction(tx_hash)

    # -----------------------------------------------------------------------
    # LIVE MODE — Etherscan API
    # -----------------------------------------------------------------------

    async def _etherscan_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a GET request against the Etherscan API.

        The API key is attached here so it never appears in caller code or logs.
        Handles timeouts, HTTP errors, and rate-limit (429) responses.
        """
        # Attach key without logging it
        params["apikey"] = self._api_key

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(self._base_url, params=params)

            if response.status_code == 429:
                logger.warning("[EthereumAdapter] Etherscan rate-limit (HTTP 429) hit.")
                raise RateLimitError(
                    "Etherscan rate limit exceeded. Please wait and retry, or upgrade your API plan."
                )

            response.raise_for_status()
            data = response.json()
            return data

        except RateLimitError:
            raise
        except httpx.TimeoutException as exc:
            logger.error("[EthereumAdapter] Provider timeout: %s", type(exc).__name__)
            raise ProviderTimeoutError(
                "Etherscan did not respond within the timeout period. Please retry later."
            ) from exc
        except httpx.HTTPStatusError as exc:
            logger.error(
                "[EthereumAdapter] HTTP error %s from Etherscan.",
                exc.response.status_code,
            )
            raise ProviderError(
                f"Etherscan returned HTTP {exc.response.status_code}. Please retry later."
            ) from exc
        except Exception as exc:
            logger.error(
                "[EthereumAdapter] Unexpected error contacting Etherscan: %s",
                type(exc).__name__,
            )
            raise ProviderError(
                "Unexpected error contacting the blockchain provider. Please retry later."
            ) from exc

    async def _live_get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Fetch live ETH balance from Etherscan."""
        data = await self._etherscan_get(
            {
                "module": "account",
                "action": "balance",
                "address": wallet_address,
                "tag": "latest",
            }
        )

        if data.get("status") == ETHERSCAN_OK:
            # Balance is returned in Wei (1 ETH = 1e18 Wei)
            wei = int(data.get("result", 0))
            eth_balance = round(wei / 1e18, 6)
        else:
            logger.warning(
                "[EthereumAdapter] Etherscan balance error: %s", data.get("message")
            )
            eth_balance = 0.0

        return {
            "data_mode": "LIVE",
            "wallet_address": wallet_address,
            "blockchain": self.chain_name,
            "balance": eth_balance,
            "token": "ETH",
        }

    async def _live_get_transactions(
        self,
        wallet_address: str,
        page: int = 1,
        page_size: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Fetch normalized Ethereum transactions from Etherscan.

        Pagination is enforced — never fetches unlimited history.
        Responses are normalized to the common transaction schema.
        """
        capped_size = min(page_size, self._max_tx)

        data = await self._etherscan_get(
            {
                "module": "account",
                "action": "txlist",
                "address": wallet_address,
                "startblock": 0,
                "endblock": 99999999,
                "page": page,
                "offset": capped_size,
                "sort": "desc",  # Most recent first
            }
        )

        result = data.get("result", [])

        # Etherscan returns a string message when no transactions exist
        if data.get("status") != ETHERSCAN_OK:
            msg = data.get("message", "")
            if ETHERSCAN_NOTX_MSG in msg or result == []:
                return []
            logger.warning(
                "[EthereumAdapter] Etherscan txlist error: %s | message: %s",
                data.get("status"),
                msg,
            )
            raise ProviderError(
                f"Etherscan returned an error: {msg}. Please check the address and retry."
            )

        normalized: List[Dict[str, Any]] = []
        addr_lower = wallet_address.lower()

        for raw_tx in result:
            try:
                normalized.append(self._normalize_etherscan_tx(raw_tx, addr_lower))
            except Exception as exc:
                # Skip malformed individual transactions but continue processing
                logger.warning(
                    "[EthereumAdapter] Skipping malformed tx %s: %s",
                    raw_tx.get("hash", "?"),
                    exc,
                )
                continue

        return normalized

    async def _live_get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """Fetch a single transaction by hash from Etherscan."""
        data = await self._etherscan_get(
            {
                "module": "proxy",
                "action": "eth_getTransactionByHash",
                "txhash": tx_hash,
            }
        )

        result = data.get("result")
        if not result:
            return None

        # Normalize hex value from Wei to ETH
        value_wei = int(result.get("value", "0x0"), 16)
        eth_value = round(value_wei / 1e18, 8)
        block_number_hex = result.get("blockNumber")
        block_number = int(block_number_hex, 16) if block_number_hex else None

        return {
            "data_mode": "LIVE",
            "tx_hash": tx_hash,
            "blockchain": self.chain_name,
            "from_address": result.get("from", ""),
            "to_address": result.get("to", ""),
            "value_eth": eth_value,
            "block_number": block_number,
            "status": "pending" if block_number is None else "confirmed",
        }

    def _normalize_etherscan_tx(
        self, raw: Dict[str, Any], target_address_lower: str
    ) -> Dict[str, Any]:
        """
        Normalize a raw Etherscan transaction dict into the common schema.

        Fields always present in the normalized output:
          tx_hash, blockchain, from_address, to_address, value_eth,
          value_wei, gas_fee_eth, block_number, timestamp_unix,
          timestamp_iso, direction, status, data_mode
        """
        from_addr = raw.get("from", "").lower()
        to_addr = raw.get("to", "").lower()

        # Determine direction relative to the queried wallet
        if from_addr == target_address_lower:
            direction = "OUTGOING"
        elif to_addr == target_address_lower:
            direction = "INCOMING"
        else:
            direction = "INTERNAL"

        # Convert Wei to ETH
        value_wei = int(raw.get("value", "0"))
        gas_used = int(raw.get("gasUsed", "0"))
        gas_price = int(raw.get("gasPrice", "0"))
        gas_fee_wei = gas_used * gas_price
        value_eth = round(value_wei / 1e18, 8)
        gas_fee_eth = round(gas_fee_wei / 1e18, 8)

        # Timestamp
        ts_unix = int(raw.get("timeStamp", 0))
        ts_iso = (
            datetime.datetime.fromtimestamp(ts_unix, tz=datetime.timezone.utc).isoformat()
            if ts_unix
            else None
        )

        # Transaction success/error
        tx_status = raw.get("txreceipt_status", "")
        if tx_status == "1":
            status = "confirmed"
        elif tx_status == "0":
            status = "failed"
        else:
            status = "unknown"

        return {
            "data_mode": "LIVE",
            "tx_hash": raw.get("hash", ""),
            "blockchain": self.chain_name,
            "from_address": raw.get("from", ""),
            "to_address": raw.get("to", ""),
            "value_eth": value_eth,
            "value_wei": value_wei,
            "token": "ETH",
            "gas_fee_eth": gas_fee_eth,
            "block_number": int(raw.get("blockNumber", 0)),
            "timestamp_unix": ts_unix,
            "timestamp_iso": ts_iso,
            "timestamp": (
                datetime.datetime.fromtimestamp(ts_unix, tz=datetime.timezone.utc)
                if ts_unix
                else datetime.datetime.now(datetime.timezone.utc)
            ),
            "direction": direction,
            "status": status,
            "confirmations": int(raw.get("confirmations", 0)),
        }

    # -----------------------------------------------------------------------
    # DEMO MODE — Deterministic Synthetic Data (Phase 1 compatible)
    # -----------------------------------------------------------------------

    def _generate_deterministic_hash(self, seed: str) -> str:
        return "0x" + hashlib.sha256(seed.encode()).hexdigest()

    def _demo_get_balance(self, wallet_address: str) -> Dict[str, Any]:
        wallet_lower = wallet_address.lower()
        numeric_seed = sum(ord(c) for c in wallet_lower) % 250
        eth_balance = round(12.45 + (numeric_seed / 10.0), 4)

        return {
            "disclaimer": DEMO_DATA_DISCLAIMER,
            "data_mode": DEMO_DATA_DISCLAIMER,
            "wallet_address": wallet_address,
            "blockchain": self.chain_name,
            "balance": eth_balance,
            "token": "ETH",
            "token_usd_value": round(eth_balance * 3150.0, 2),
            "nonce": (numeric_seed * 3) % 150,
        }

    def _demo_get_transactions(self, wallet_address: str) -> List[Dict[str, Any]]:
        wallet_lower = wallet_address.lower()
        now = datetime.datetime.now(datetime.timezone.utc)

        vasp_binance = "0x28c6c06298d514db089934071355e5743bf21d60"
        vasp_coinbase = "0x503828976d22510aad0201ac7ec88293211d23dc"
        wallet_intermediate_a = "0x742d35cc6634c0532925a3b844bc454e4438f44e"
        wallet_intermediate_b = "0x89205a3e3b2db69dce6aa645f778d655fba73bfa"
        high_risk_cluster_c = "0x3cda2097645d52be2250bc33abdb5ac87124f56b"

        raw_txs = [
            {
                "tx_hash": self._generate_deterministic_hash(f"{wallet_lower}_tx_1"),
                "blockchain": self.chain_name,
                "from_address": wallet_intermediate_a,
                "to_address": wallet_address,
                "value_eth": 42.5000,
                "value_wei": int(42.5 * 1e18),
                "token": "ETH",
                "timestamp": now - datetime.timedelta(hours=2, minutes=15),
                "timestamp_iso": (now - datetime.timedelta(hours=2, minutes=15)).isoformat() + "Z",
                "direction": "INCOMING",
                "gas_fee_eth": 0.0035,
                "block_number": 19450210,
                "status": "confirmed",
                "confirmations": 120,
                "data_mode": DEMO_DATA_DISCLAIMER,
            },
            {
                "tx_hash": self._generate_deterministic_hash(f"{wallet_lower}_tx_2"),
                "blockchain": self.chain_name,
                "from_address": wallet_address,
                "to_address": wallet_intermediate_b,
                "value_eth": 25.0000,
                "value_wei": int(25.0 * 1e18),
                "token": "ETH",
                "timestamp": now - datetime.timedelta(hours=1, minutes=45),
                "timestamp_iso": (now - datetime.timedelta(hours=1, minutes=45)).isoformat() + "Z",
                "direction": "OUTGOING",
                "gas_fee_eth": 0.0041,
                "block_number": 19450235,
                "status": "confirmed",
                "confirmations": 105,
                "data_mode": DEMO_DATA_DISCLAIMER,
            },
            {
                "tx_hash": self._generate_deterministic_hash(f"{wallet_lower}_tx_3"),
                "blockchain": self.chain_name,
                "from_address": wallet_address,
                "to_address": vasp_binance,
                "value_eth": 16.8500,
                "value_wei": int(16.85 * 1e18),
                "token": "ETH",
                "timestamp": now - datetime.timedelta(minutes=55),
                "timestamp_iso": (now - datetime.timedelta(minutes=55)).isoformat() + "Z",
                "direction": "OUTGOING",
                "gas_fee_eth": 0.0039,
                "block_number": 19450278,
                "status": "confirmed",
                "confirmations": 88,
                "data_mode": DEMO_DATA_DISCLAIMER,
            },
            {
                "tx_hash": self._generate_deterministic_hash(f"{wallet_lower}_tx_4"),
                "blockchain": self.chain_name,
                "from_address": high_risk_cluster_c,
                "to_address": wallet_address,
                "value_eth": 10.0000,
                "value_wei": int(10.0 * 1e18),
                "token": "ETH",
                "timestamp": now - datetime.timedelta(days=1, hours=4),
                "timestamp_iso": (now - datetime.timedelta(days=1, hours=4)).isoformat() + "Z",
                "direction": "INCOMING",
                "gas_fee_eth": 0.0028,
                "block_number": 19448890,
                "status": "confirmed",
                "confirmations": 1800,
                "data_mode": DEMO_DATA_DISCLAIMER,
            },
            {
                "tx_hash": self._generate_deterministic_hash(f"{wallet_lower}_tx_5"),
                "blockchain": self.chain_name,
                "from_address": wallet_address,
                "to_address": vasp_coinbase,
                "value_eth": 9.2000,
                "value_wei": int(9.2 * 1e18),
                "token": "ETH",
                "timestamp": now - datetime.timedelta(days=1, hours=1),
                "timestamp_iso": (now - datetime.timedelta(days=1, hours=1)).isoformat() + "Z",
                "direction": "OUTGOING",
                "gas_fee_eth": 0.0032,
                "block_number": 19448930,
                "status": "confirmed",
                "confirmations": 1750,
                "data_mode": DEMO_DATA_DISCLAIMER,
            },
        ]
        return raw_txs

    def _demo_get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        return {
            "disclaimer": DEMO_DATA_DISCLAIMER,
            "data_mode": DEMO_DATA_DISCLAIMER,
            "tx_hash": tx_hash,
            "blockchain": self.chain_name,
            "status": "confirmed",
            "confirmations": 45,
            "timestamp_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Custom Exception Hierarchy for adapter error handling
# ---------------------------------------------------------------------------

class AdapterError(Exception):
    """Base class for all adapter errors."""


class ProviderError(AdapterError):
    """General provider/server error (5xx, unexpected response)."""


class ProviderTimeoutError(ProviderError):
    """Provider did not respond within the configured timeout."""


class RateLimitError(ProviderError):
    """Provider returned HTTP 429 Too Many Requests."""


class InvalidAddressError(AdapterError):
    """Address failed validation for this chain."""

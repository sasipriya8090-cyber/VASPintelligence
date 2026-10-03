"""
Chain-agnostic BlockchainAdapter interface.

All blockchain adapters MUST implement this interface.
The architecture is designed to be multi-chain ready for:
  - Ethereum (implemented in Phase 2)
  - Bitcoin (stub - future phase)
  - Tron (stub - future phase)
  - BNB Chain (stub - future phase)
  - Solana (stub - future phase)
  - Polygon (stub - future phase)
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional


class BlockchainAdapter(ABC):
    """
    Abstract interface for blockchain data providers.

    Decouples raw network queries/APIs from core analytical business logic.
    Each concrete adapter is responsible for:
      - Validating addresses for its specific chain format
      - Fetching and normalizing transaction data
      - Handling provider errors and rate limits
      - Reporting whether it is in LIVE or DEMO mode
    """

    # -------------------------------------------------------------------------
    # Chain Identification
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def chain_name(self) -> str:
        """Short lowercase identifier (e.g. 'ethereum', 'bitcoin', 'tron')."""
        ...

    @property
    @abstractmethod
    def is_live(self) -> bool:
        """Return True when the adapter is using a real provider (not demo/mock data)."""
        ...

    # -------------------------------------------------------------------------
    # Address Validation
    # -------------------------------------------------------------------------

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """
        Return True if `address` is a syntactically valid address for this chain.
        Raises nothing — returns bool only.
        """
        ...

    # -------------------------------------------------------------------------
    # Core Data Methods
    # -------------------------------------------------------------------------

    @abstractmethod
    async def get_transactions(
        self,
        wallet_address: str,
        page: int = 1,
        page_size: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve normalized recent transactions for a given wallet address.

        Args:
            wallet_address: Chain-specific wallet address (pre-validated).
            page: 1-based page index.
            page_size: Number of transactions per page (capped by adapter).

        Returns:
            List of normalized transaction dicts conforming to NormalizedTransaction schema.
        """
        ...

    @abstractmethod
    async def get_balance(self, wallet_address: str) -> Dict[str, Any]:
        """
        Retrieve the current account balance for a given wallet address.

        Returns:
            Dict with at minimum: wallet_address, blockchain, balance, token.
        """
        ...

    @abstractmethod
    async def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve transaction details by transaction hash.

        Returns:
            Normalized transaction dict or None if not found.
        """
        ...


# -------------------------------------------------------------------------
# Future Chain Stub Documentation
# -------------------------------------------------------------------------
# The following adapters are planned but NOT yet implemented.
# To add a new chain, create a new file in app/adapters/ that:
#   1. Imports and inherits BlockchainAdapter
#   2. Implements all abstract methods
#   3. Reads its API key/URL from app.core.config.settings
#   4. Returns data normalized to the common transaction schema
#   5. Registers itself in app/adapters/__init__.py
#
# Planned adapters:
#   - BitcoinAdapter    (app/adapters/bitcoin.py)   - Blockstream/Mempool.space
#   - TronAdapter       (app/adapters/tron.py)       - Tronscan API
#   - BNBChainAdapter   (app/adapters/bnb.py)        - BscScan API
#   - SolanaAdapter     (app/adapters/solana.py)     - Helius / Solana RPC
#   - PolygonAdapter    (app/adapters/polygon.py)    - Polygonscan API

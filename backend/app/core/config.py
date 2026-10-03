"""Application configuration and core settings."""
import os
from typing import List, Optional


class Settings:
    PROJECT_NAME: str = "Automated Blockchain Intelligence & VASP Attribution Engine"
    VERSION: str = "2.0.0"
    DATA_MODE: str = "DEMO DATA — NOT LIVE BLOCKCHAIN DATA"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vasp_intelligence.db")

    # CORS Origins for local frontend development
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # -------------------------------------------------------------------------
    # Phase 2: Ethereum Blockchain Provider Configuration
    # Configure ONE of the following providers by setting the env var.
    # The application will automatically detect which is available.
    # -------------------------------------------------------------------------

    # Etherscan API Key (https://etherscan.io/myapikey)
    ETHERSCAN_API_KEY: Optional[str] = os.getenv("ETHERSCAN_API_KEY") or None

    # Etherscan Base URL (default: Ethereum mainnet)
    ETHERSCAN_BASE_URL: str = os.getenv(
        "ETHERSCAN_BASE_URL", "https://api.etherscan.io/api"
    )

    # Alternative: Alchemy API Key (https://dashboard.alchemy.com/)
    ALCHEMY_API_KEY: Optional[str] = os.getenv("ALCHEMY_API_KEY") or None

    # Alternative: Infura Project ID (https://app.infura.io/)
    INFURA_PROJECT_ID: Optional[str] = os.getenv("INFURA_PROJECT_ID") or None

    # Provider request timeout (seconds)
    BLOCKCHAIN_REQUEST_TIMEOUT: int = int(os.getenv("BLOCKCHAIN_REQUEST_TIMEOUT", "15"))

    # In-memory cache TTL (seconds). Default 5 minutes.
    BLOCKCHAIN_CACHE_TTL: int = int(os.getenv("BLOCKCHAIN_CACHE_TTL", "300"))

    # Maximum transactions to fetch per address per request (pagination guard)
    BLOCKCHAIN_MAX_TX_PER_REQUEST: int = int(
        os.getenv("BLOCKCHAIN_MAX_TX_PER_REQUEST", "50")
    )

    # -------------------------------------------------------------------------
    # Phase 2: Future Chain Placeholders (ready but not yet implemented)
    # -------------------------------------------------------------------------
    # BITCOIN_RPC_URL=http://localhost:8332
    # TRON_API_KEY=your_tronscan_api_key
    # BNB_RPC_URL=https://bsc-dataseed.binance.org/
    # SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
    # POLYGON_RPC_URL=https://polygon-rpc.com

    def is_ethereum_configured(self) -> bool:
        """Return True if at least one real Ethereum provider key is configured."""
        return bool(self.ETHERSCAN_API_KEY or self.ALCHEMY_API_KEY or self.INFURA_PROJECT_ID)

    def get_ethereum_provider_name(self) -> str:
        """Return the name of the configured Ethereum provider (for logging, no key exposure)."""
        if self.ETHERSCAN_API_KEY:
            return "Etherscan"
        if self.ALCHEMY_API_KEY:
            return "Alchemy"
        if self.INFURA_PROJECT_ID:
            return "Infura"
        return "None (DEMO mode)"

    def get_data_mode(self) -> str:
        """Return human-readable data mode string."""
        if self.is_ethereum_configured():
            return f"LIVE — Ethereum data via {self.get_ethereum_provider_name()}"
        return self.DATA_MODE


settings = Settings()


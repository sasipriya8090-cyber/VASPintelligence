from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import router
from app.api.blockchain import router as blockchain_router
from app.api.tracing import router as tracing_router
from app.api.sahyog import router as sahyog_router
from app.database.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema is ready and seeded
    init_database()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Automated Blockchain Intelligence & VASP Attribution Engine API — "
        "Phase 7: AI Investigation, Reports & SAHYOG Routing"
    ),
    lifespan=lifespan,
)

# Configure CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 1: Core investigation & analysis endpoints
app.include_router(router, prefix="/api")

# Phase 2: Blockchain data integration endpoints
# Example:
#   /api/blockchain/...
app.include_router(blockchain_router, prefix="/api")

# Phase 3: Transaction tracing & fund-flow endpoints
# Examples:
#   /api/trace/wallet
#   /api/trace/ethereum/address/{address}
#   /api/trace/ethereum/address/{address}/summary
app.include_router(tracing_router, prefix="/api")

# Phase 7: SAHYOG routing support
# Demo/synthetic routing endpoint:
#   /api/sahyog/request
#
# Status endpoint:
#   /api/sahyog/status
app.include_router(sahyog_router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "disclaimer": settings.DATA_MODE,
        "documentation": "/docs",
        "health_check": "/api/health",
        "blockchain_status": "/api/blockchain/config/status",
        "tracing_status": "/api/trace/ethereum/address/{address}",
        "sahyog_status": "/api/sahyog/status",
    }
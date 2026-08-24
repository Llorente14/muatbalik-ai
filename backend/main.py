# ── MuatBalik AI — FastAPI application ──

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from api import inference, orders, matching, backhaul, tracking, dashboard


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


app = FastAPI(
    title="MuatBalik AI",
    description=(
        "Decision-support control tower untuk shipment utama dan muatan balik.\n\n"
        "**Workflow utama:**\n"
        "1. Order intake → AI extraction (`/api/inference/extract`, `/api/orders/parse`)\n"
        "2. Carrier matching (`/api/shipments/{id}/match`, `/confirm`)\n"
        "3. Backhaul discovery (`/api/shipments/{id}/backhaul`, `/consolidate`)\n"
        "4. Control tower (`/api/dashboard/metrics`, tracking events)\n\n"
        "Data bersifat **SIMULATED** — tidak menggunakan data carrier real-time."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS — allow frontend dev server ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ──
app.include_router(inference.router)
app.include_router(orders.router)
app.include_router(matching.router)
app.include_router(backhaul.router)
app.include_router(tracking.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "MuatBalik AI",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }

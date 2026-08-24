# ── MuatBalik AI — Dashboard API ──
# GET /api/dashboard/metrics

import sqlite3

from fastapi import APIRouter, Depends
from database import get_db
from schemas import DashboardMetrics

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Get demo KPI metrics",
    description="Returns primary shipment counts, backhaul status, "
                "load factor, consolidation stats, and response time. "
                "All data is from SIMULATED scenarios.",
)
def get_metrics(db: sqlite3.Connection = Depends(get_db)):
    # ── Shipment counts ──
    confirmed = db.execute(
        "SELECT COUNT(*) FROM shipments WHERE shipment_status IN ('confirmed', 'in_transit')"
    ).fetchone()[0]

    delivered = db.execute(
        "SELECT COUNT(*) FROM shipments WHERE shipment_status = 'delivered'"
    ).fetchone()[0]

    # ── Backhaul counts ──
    backhaul_filled = db.execute(
        "SELECT COUNT(*) FROM shipments WHERE backhaul_status IN ('filled', 'partially_filled')"
    ).fetchone()[0]

    backhaul_unfilled = db.execute(
        "SELECT COUNT(*) FROM shipments WHERE backhaul_status = 'unfilled'"
    ).fetchone()[0]

    # ── Load factor ──
    slots = db.execute("SELECT capacity_kg, filled_kg FROM backhaul_slots").fetchall()
    if slots:
        total_cap = sum(s["capacity_kg"] for s in slots) or 1
        total_before = 0  # before = empty return
        total_after = sum(s["filled_kg"] for s in slots)
        avg_before = round((total_before / total_cap) * 100, 1)
        avg_after = round((total_after / total_cap) * 100, 1)
    else:
        avg_before = 0
        avg_after = 0

    # ── Consolidation count ──
    consolidated = db.execute(
        "SELECT COUNT(*) FROM consolidations WHERE compatibility_status = 'compatible'"
    ).fetchone()[0]

    # ── P95 response (mock — real value would come from metrics middleware) ──
    p95_ms = 2400.0

    return DashboardMetrics(
        confirmed_shipments=confirmed,
        delivered_shipments=delivered,
        backhaul_filled=backhaul_filled,
        backhaul_unfilled=backhaul_unfilled,
        avg_load_factor_before=avg_before,
        avg_load_factor_after=avg_after,
        consolidated_orders=consolidated,
        p95_response_ms=p95_ms,
    )

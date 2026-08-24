# ── MuatBalik AI — Matching API ──
# POST /api/shipments/{order_id}/match     — run matching
# GET  /api/shipments/{order_id}/candidates — get cached candidates
# POST /api/shipments/{order_id}/confirm    — confirm a carrier

import json
import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import (
    MatchResult,
    MatchCandidate,
    CarrierResponse,
    ShipmentResponse,
)
from services.matcher import match_carriers

router = APIRouter(prefix="/api/shipments", tags=["Matching"])


def _row_to_carrier(row: sqlite3.Row) -> dict:
    return dict(row)


def _carrier_response(d: dict) -> CarrierResponse:
    return CarrierResponse(**d)


@router.post(
    "/{order_id}/match",
    response_model=MatchResult,
    summary="Run matching engine for an order",
    description="Applies hard constraints (route, capacity, temperature, deadline) "
                "and weighted scoring to rank all active carriers.",
)
def match_order(order_id: str, db: sqlite3.Connection = Depends(get_db)):
    # 1. Get order
    order_row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order_row:
        raise HTTPException(status_code=404, detail="Order not found")
    order = dict(order_row)

    # 2. Get all active carriers
    carrier_rows = db.execute("SELECT * FROM carriers WHERE status = 'active'").fetchall()
    carriers = [_row_to_carrier(r) for r in carrier_rows]

    # 3. Run matching
    results = match_carriers(order, carriers)

    # 4. Build response
    candidates = []
    for r in results:
        candidates.append(
            MatchCandidate(
                carrier=_carrier_response(r["carrier"]),
                score=r["score"],
                reasons=r["reasons"],
                status=r["status"],
            )
        )

    return MatchResult(order_id=order_id, candidates=candidates)


@router.get(
    "/{order_id}/candidates",
    response_model=MatchResult,
    summary="Get matching candidates (re-runs matching)",
)
def get_candidates(order_id: str, db: sqlite3.Connection = Depends(get_db)):
    return match_order(order_id, db)


@router.post(
    "/{order_id}/confirm",
    response_model=ShipmentResponse,
    summary="Confirm a carrier for the order — creates a shipment",
    description="Creates a shipment with status 'confirmed'. "
                "Backhaul search begins (status = 'searching'). "
                "Primary shipment does NOT wait for backhaul.",
)
def confirm_shipment(
    order_id: str,
    carrier_id: str,
    db: sqlite3.Connection = Depends(get_db),
):
    # Validate order
    order_row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order_row:
        raise HTTPException(status_code=404, detail="Order not found")

    # Validate carrier
    carrier_row = db.execute("SELECT * FROM carriers WHERE id = ?", (carrier_id,)).fetchone()
    if not carrier_row:
        raise HTTPException(status_code=404, detail="Carrier not found")

    carrier = dict(carrier_row)

    # Run matching to get score
    order = dict(order_row)
    results = match_carriers(order, [carrier])
    score = results[0]["score"] if results else 0
    reasons = results[0]["reasons"] if results else []

    if score == 0:
        raise HTTPException(
            status_code=400,
            detail="Carrier rejected by hard constraints — cannot confirm",
        )

    # Create shipment
    shipment_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO shipments
           (id, order_id, carrier_id, shipment_status, backhaul_status,
            match_score, match_reasons)
           VALUES (?, ?, ?, 'confirmed', 'searching', ?, ?)""",
        (shipment_id, order_id, carrier_id, score, json.dumps(reasons)),
    )

    # Update order status
    db.execute("UPDATE orders SET status = 'confirmed' WHERE id = ?", (order_id,))

    # Create backhaul slot from carrier return info
    if carrier.get("return_origin") and carrier.get("return_destination"):
        slot_id = str(uuid.uuid4())
        db.execute(
            """INSERT INTO backhaul_slots
               (id, carrier_id, origin, destination, departure_at,
                capacity_kg, filled_kg, prebook_discount_pct, status)
               VALUES (?, ?, ?, ?, ?, ?, 0, 0, 'searching')""",
            (
                slot_id,
                carrier_id,
                carrier.get("return_origin"),
                carrier.get("return_destination"),
                carrier.get("arrival_at"),
                carrier.get("return_capacity_kg", 0),
            ),
        )

    db.commit()

    row = db.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,)).fetchone()
    return ShipmentResponse(**dict(row))

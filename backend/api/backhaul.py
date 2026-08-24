# ── MuatBalik AI — Backhaul API ──
# GET  /api/shipments/{shipment_id}/backhaul  — overview
# POST /api/backhaul/{slot_id}/prebook        — create pre-booking
# POST /api/backhaul/{slot_id}/consolidate    — run consolidation

import json
import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import (
    BackhaulOverview,
    BackhaulSlotResponse,
    ShipmentResponse,
    ConsolidationCandidate,
)
from services.consolidator import find_backhaul_orders, pack_compatible_orders, compute_load_factor

router = APIRouter(tags=["Backhaul"])


@router.get(
    "/api/shipments/{shipment_id}/backhaul",
    response_model=BackhaulOverview,
    summary="Get backhaul overview for a shipment",
    description="Shows return capacity, consolidation candidates, "
                "and load factor before/after.",
)
def get_backhaul(shipment_id: str, db: sqlite3.Connection = Depends(get_db)):
    # 1. Get shipment
    ship_row = db.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,)).fetchone()
    if not ship_row:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment = ShipmentResponse(**dict(ship_row))

    # 2. Get backhaul slot
    slot_row = db.execute(
        "SELECT * FROM backhaul_slots WHERE carrier_id = ? ORDER BY rowid DESC LIMIT 1",
        (shipment.carrier_id,),
    ).fetchone()

    slot = BackhaulSlotResponse(**dict(slot_row)) if slot_row else None

    # 3. Find consolidation candidates
    candidates: list[ConsolidationCandidate] = []
    load_before = 0.0
    load_after = 0.0

    if slot:
        carrier_row = db.execute(
            "SELECT * FROM carriers WHERE id = ?", (shipment.carrier_id,)
        ).fetchone()
        carrier = dict(carrier_row) if carrier_row else {}

        # Get pending orders on inverse route
        order_rows = db.execute("SELECT * FROM orders WHERE status = 'pending'").fetchall()
        all_orders = [dict(r) for r in order_rows]
        backhaul_orders = find_backhaul_orders(carrier, all_orders)

        for o in backhaul_orders:
            t_min = o.get("temperature_min_c")
            t_max = o.get("temperature_max_c")
            temp_range = f"{t_min}-{t_max}" if t_min is not None else "ambient"
            candidates.append(
                ConsolidationCandidate(
                    order_id=o["id"],
                    commodity=o.get("commodity"),
                    weight_kg=o.get("weight_kg", 0),
                    route=f"{o.get('origin', '?')} → {o.get('destination', '?')}",
                    temperature_range=temp_range,
                )
            )

        load_before = compute_load_factor(slot.filled_kg, slot.capacity_kg)
        # Projected load after consolidation
        projected_fill = slot.filled_kg + sum(o.get("weight_kg", 0) for o in backhaul_orders)
        load_after = compute_load_factor(projected_fill, slot.capacity_kg)

    return BackhaulOverview(
        shipment=shipment,
        slot=slot,
        consolidation_candidates=candidates,
        load_factor_before=load_before,
        load_factor_after=load_after,
    )


@router.post(
    "/api/backhaul/{slot_id}/prebook",
    response_model=BackhaulSlotResponse,
    summary="Create a pre-booking discount on a backhaul slot",
    description="When no backhaul orders exist, opens the slot with "
                "a demo discount (default 15%).",
)
def prebook_slot(
    slot_id: str,
    discount_pct: int = 15,
    db: sqlite3.Connection = Depends(get_db),
):
    row = db.execute("SELECT * FROM backhaul_slots WHERE id = ?", (slot_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Backhaul slot not found")

    db.execute(
        """UPDATE backhaul_slots
           SET status = 'pre_booked', prebook_discount_pct = ?
           WHERE id = ?""",
        (discount_pct, slot_id),
    )

    # Update shipment backhaul_status
    slot = dict(row)
    db.execute(
        """UPDATE shipments SET backhaul_status = 'pre_booked'
           WHERE carrier_id = ? AND backhaul_status = 'searching'""",
        (slot["carrier_id"],),
    )
    db.commit()

    updated = db.execute("SELECT * FROM backhaul_slots WHERE id = ?", (slot_id,)).fetchone()
    return BackhaulSlotResponse(**dict(updated))


@router.post(
    "/api/backhaul/{slot_id}/consolidate",
    response_model=BackhaulSlotResponse,
    summary="Run consolidation on a backhaul slot",
    description="Groups compatible pending orders on the inverse route "
                "into the backhaul slot. Updates filled_kg and status.",
)
def consolidate_slot(slot_id: str, db: sqlite3.Connection = Depends(get_db)):
    slot_row = db.execute("SELECT * FROM backhaul_slots WHERE id = ?", (slot_id,)).fetchone()
    if not slot_row:
        raise HTTPException(status_code=404, detail="Backhaul slot not found")
    slot = dict(slot_row)

    # Get carrier for route info
    carrier_row = db.execute("SELECT * FROM carriers WHERE id = ?", (slot["carrier_id"],)).fetchone()
    if not carrier_row:
        raise HTTPException(status_code=404, detail="Carrier not found")
    carrier = dict(carrier_row)

    # Find backhaul orders
    order_rows = db.execute("SELECT * FROM orders WHERE status = 'pending'").fetchall()
    all_orders = [dict(r) for r in order_rows]
    backhaul_orders = find_backhaul_orders(carrier, all_orders)

    if not backhaul_orders:
        raise HTTPException(status_code=404, detail="No compatible backhaul orders found")

    # Pack orders
    result = pack_compatible_orders(backhaul_orders, slot["capacity_kg"] - slot["filled_kg"])

    if result["compatibility_status"] == "rejected":
        raise HTTPException(status_code=400, detail="Temperature ranges incompatible")

    # Create consolidation record
    consol_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO consolidations
           (id, backhaul_slot_id, order_ids, total_weight_kg,
            temperature_range, compatibility_status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            consol_id,
            slot_id,
            json.dumps(result["packed_order_ids"]),
            result["total_weight_kg"],
            result["temperature_range"],
            result["compatibility_status"],
        ),
    )

    # Update slot
    new_filled = slot["filled_kg"] + result["total_weight_kg"]
    new_status = "filled" if new_filled >= slot["capacity_kg"] else "partially_filled"
    db.execute(
        "UPDATE backhaul_slots SET filled_kg = ?, status = ? WHERE id = ?",
        (new_filled, new_status, slot_id),
    )

    # Update shipment backhaul_status
    db.execute(
        """UPDATE shipments SET backhaul_status = ?
           WHERE carrier_id = ? AND backhaul_status IN ('searching', 'pre_booked', 'partially_filled')""",
        (new_status, slot["carrier_id"]),
    )

    db.commit()

    updated = db.execute("SELECT * FROM backhaul_slots WHERE id = ?", (slot_id,)).fetchone()
    return BackhaulSlotResponse(**dict(updated))

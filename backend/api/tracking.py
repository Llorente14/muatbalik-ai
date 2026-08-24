# ── MuatBalik AI — Tracking API ──
# POST /api/shipments/{shipment_id}/tracking-events

import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import TrackingEventCreate, TrackingEventResponse

router = APIRouter(prefix="/api/shipments", tags=["Tracking"])

# Fixture: cold-storage partners for recommendations
COLD_STORAGE_PARTNERS = {
    "Makassar": "Makassar Cold Hub — Jl. Pelabuhan Soekarno-Hatta",
    "Surabaya": "Surabaya Cold Storage — Tanjung Perak Terminal",
    "Ambon": "Ambon Cold Facility — Pelabuhan Yos Sudarso",
}


@router.post(
    "/{shipment_id}/tracking-events",
    response_model=TrackingEventResponse,
    summary="Log a tracking event for a shipment",
    description="Simulates logistics events: departed, delayed, "
                "temperature_excursion, arrived. "
                "Returns alerts and cold-storage recommendations on excursion.",
)
def create_tracking_event(
    shipment_id: str,
    event: TrackingEventCreate,
    db: sqlite3.Connection = Depends(get_db),
):
    # Validate shipment
    ship_row = db.execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,)).fetchone()
    if not ship_row:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment = dict(ship_row)

    # Get order for temperature validation
    order_row = db.execute(
        "SELECT * FROM orders WHERE id = ?", (shipment["order_id"],)
    ).fetchone()
    order = dict(order_row) if order_row else {}

    # ── Alert + recommendation logic ──
    alert = None
    recommendation = None

    if event.event_type == "temperature_excursion" and event.temperature_c is not None:
        t_min = order.get("temperature_min_c")
        t_max = order.get("temperature_max_c")
        if t_min is not None and t_max is not None:
            if event.temperature_c < t_min or event.temperature_c > t_max:
                alert = (
                    f"⚠ Suhu {event.temperature_c}°C di luar range "
                    f"{t_min}-{t_max}°C"
                )
                # Recommend nearest cold-storage
                location = event.location or ""
                for city, partner in COLD_STORAGE_PARTNERS.items():
                    if city.lower() in location.lower():
                        recommendation = (
                            f"Transit ke {partner} dan prioritaskan "
                            f"reefer inspection sebelum lanjut."
                        )
                        break
                if not recommendation:
                    recommendation = (
                        "Cari cold-storage terdekat dan lakukan inspeksi reefer."
                    )

    if event.event_type == "departed":
        db.execute(
            "UPDATE shipments SET shipment_status = 'in_transit' WHERE id = ?",
            (shipment_id,),
        )

    if event.event_type == "arrived":
        db.execute(
            "UPDATE shipments SET shipment_status = 'delivered' WHERE id = ?",
            (shipment_id,),
        )
        db.execute(
            "UPDATE orders SET status = 'confirmed' WHERE id = ?",
            (shipment["order_id"],),
        )

    # Insert event
    event_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO tracking_events
           (id, shipment_id, event_type, temperature_c, location, note)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            event_id,
            shipment_id,
            event.event_type,
            event.temperature_c,
            event.location,
            event.note,
        ),
    )
    db.commit()

    row = db.execute("SELECT * FROM tracking_events WHERE id = ?", (event_id,)).fetchone()
    resp = dict(row)
    return TrackingEventResponse(
        **resp,
        alert=alert,
        recommendation=recommendation,
    )

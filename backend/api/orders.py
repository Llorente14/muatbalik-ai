# ── MuatBalik AI — Orders API ──
# POST /api/orders/parse   — AI extraction → order
# POST /api/orders          — manual create
# GET  /api/orders/{id}     — get by id

import json
import sqlite3
import uuid

from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import (
    OrderParseRequest,
    OrderParseResponse,
    OrderCreate,
    OrderResponse,
    ExtractionConfidence,
)
from services.extractor import extract_order, inference_to_order_fields, compute_confidence

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def _row_to_order(row: sqlite3.Row) -> OrderResponse:
    return OrderResponse(**dict(row))


@router.post(
    "/parse",
    response_model=OrderParseResponse,
    summary="Parse raw text into a logistics order via AI extraction",
    description="Runs the extractor (mock / Qwen LoRA) on raw text, "
                "creates an order in the database, and returns extraction confidence.",
)
def parse_order(req: OrderParseRequest, db: sqlite3.Connection = Depends(get_db)):
    # 1. Extract
    inference = extract_order(req.raw_text)
    fields = inference_to_order_fields(inference)
    confidence = compute_confidence(fields)

    # 2. Warnings
    warnings: list[str] = []
    if fields.get("origin") is None:
        warnings.append("Field 'origin' tidak terdeteksi")
    if fields.get("destination") is None:
        warnings.append("Field 'destination' tidak terdeteksi")
    if fields.get("weight_kg") is None:
        warnings.append("Field 'weight_kg' tidak terdeteksi")
    if fields.get("temperature_min_c") is None:
        warnings.append("Field 'temperature' tidak terdeteksi — matching tetap berjalan")

    # 3. Insert order
    order_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO orders
           (id, raw_text, origin, destination, commodity, weight_kg,
            temperature_min_c, temperature_max_c, pickup_deadline, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            order_id,
            req.raw_text,
            fields.get("origin"),
            fields.get("destination"),
            fields.get("commodity"),
            fields.get("weight_kg"),
            fields.get("temperature_min_c"),
            fields.get("temperature_max_c"),
            fields.get("pickup_deadline"),
        ),
    )
    db.commit()

    row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    order = _row_to_order(row)

    return OrderParseResponse(
        order=order,
        confidence=ExtractionConfidence(**confidence),
        warnings=warnings,
    )


@router.post(
    "",
    response_model=OrderResponse,
    summary="Create an order manually",
)
def create_order(req: OrderCreate, db: sqlite3.Connection = Depends(get_db)):
    order_id = str(uuid.uuid4())
    db.execute(
        """INSERT INTO orders
           (id, raw_text, origin, destination, commodity, weight_kg,
            volume_m3, temperature_min_c, temperature_max_c,
            pickup_deadline, delivery_deadline, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
        (
            order_id,
            req.raw_text,
            req.origin,
            req.destination,
            req.commodity,
            req.weight_kg,
            req.volume_m3,
            req.temperature_min_c,
            req.temperature_max_c,
            req.pickup_deadline,
            req.delivery_deadline,
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    return _row_to_order(row)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get an order by ID",
)
def get_order(order_id: str, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    return _row_to_order(row)

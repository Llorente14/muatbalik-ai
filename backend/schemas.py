# ── MuatBalik AI — Pydantic schemas ──
# All request/response models for the API.
# Aligned with PRD §8 data model and inference output format.

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Inference  (POST /api/inference/extract)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class InferenceRequest(BaseModel):
    """Raw Indonesian logistics chat text."""
    raw_text: str = Field(
        ...,
        examples=[
            "bos tlg cariin kapal rute bitung k mks buat angkut "
            "1.5 ton cakalang fresh, butuh chiller 2-4 C, tlg muat lusa sore ya."
        ],
    )


class InferenceDetails(BaseModel):
    """Structured fields extracted from raw text."""
    origin: Optional[str] = None
    destination: Optional[str] = None
    cargo_type: Optional[str] = None
    weight: Optional[float] = None
    unit: Optional[str] = "kg"
    temp_requirement: Optional[str] = None
    delivery_time: Optional[str] = None


class InferenceResponse(BaseModel):
    """Model output format — matches fine-tuned Qwen LoRA output."""
    status: str = "success"
    message: str = ""
    details: InferenceDetails


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Orders  (PRD §8 orders table)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OrderParseRequest(BaseModel):
    """Input for POST /api/orders/parse."""
    raw_text: str = Field(
        ...,
        examples=[
            "300 kg tuna Ambon ke Surabaya, suhu 0-4°C, pickup besok pagi"
        ],
    )


class OrderCreate(BaseModel):
    """Manual order creation — all fields explicit."""
    raw_text: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    commodity: Optional[str] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    pickup_deadline: Optional[str] = None
    delivery_deadline: Optional[str] = None


class OrderResponse(BaseModel):
    id: str
    raw_text: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    commodity: Optional[str] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    pickup_deadline: Optional[str] = None
    delivery_deadline: Optional[str] = None
    status: str
    created_at: str


class ExtractionConfidence(BaseModel):
    """Per-field confidence from the extractor."""
    origin: int = 0
    destination: int = 0
    commodity: int = 0
    weight_kg: int = 0
    temperature: int = 0
    pickup_deadline: int = 0


class OrderParseResponse(BaseModel):
    """Result of POST /api/orders/parse."""
    order: OrderResponse
    confidence: ExtractionConfidence
    warnings: list[str] = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Carriers  (PRD §8 carriers table)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CarrierResponse(BaseModel):
    id: str
    name: str
    origin: str
    destination: str
    departure_at: Optional[str] = None
    arrival_at: Optional[str] = None
    capacity_kg: float
    capacity_m3: Optional[float] = None
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None
    price_idr: int
    rating: float
    return_origin: Optional[str] = None
    return_destination: Optional[str] = None
    return_capacity_kg: float = 0
    status: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Matching  (PRD §6 F4)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MatchCandidate(BaseModel):
    carrier: CarrierResponse
    score: int = 0
    reasons: list[str] = []
    status: str = "valid"  # recommended | valid | rejected


class MatchResult(BaseModel):
    order_id: str
    candidates: list[MatchCandidate] = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Shipments  (PRD §8 implicit)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ShipmentResponse(BaseModel):
    id: str
    order_id: str
    carrier_id: str
    shipment_status: str
    backhaul_status: str
    match_score: int = 0
    match_reasons: Optional[str] = None
    created_at: str


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Backhaul  (PRD §8 backhaul_slots, §6 F5/F6)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BackhaulSlotResponse(BaseModel):
    id: str
    carrier_id: str
    origin: str
    destination: str
    departure_at: Optional[str] = None
    capacity_kg: float
    filled_kg: float
    prebook_discount_pct: int = 0
    status: str


class ConsolidationCandidate(BaseModel):
    order_id: str
    commodity: Optional[str] = None
    weight_kg: float = 0
    route: str = ""
    temperature_range: str = ""


class BackhaulOverview(BaseModel):
    shipment: ShipmentResponse
    slot: Optional[BackhaulSlotResponse] = None
    consolidation_candidates: list[ConsolidationCandidate] = []
    load_factor_before: float = 0
    load_factor_after: float = 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Tracking events  (PRD §8 tracking_events, §6 F8)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TrackingEventCreate(BaseModel):
    event_type: str = Field(
        ...,
        examples=["departed", "delayed", "temperature_excursion", "arrived"],
    )
    temperature_c: Optional[float] = None
    location: Optional[str] = None
    note: Optional[str] = None


class TrackingEventResponse(BaseModel):
    id: str
    shipment_id: str
    event_type: str
    temperature_c: Optional[float] = None
    location: Optional[str] = None
    note: Optional[str] = None
    created_at: str
    alert: Optional[str] = None
    recommendation: Optional[str] = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dashboard  (PRD §6 F9)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DashboardMetrics(BaseModel):
    confirmed_shipments: int = 0
    delivered_shipments: int = 0
    backhaul_filled: int = 0
    backhaul_unfilled: int = 0
    avg_load_factor_before: float = 0
    avg_load_factor_after: float = 0
    consolidated_orders: int = 0
    p95_response_ms: float = 0

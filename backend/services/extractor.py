# ── MuatBalik AI — Order extractor (mock) ──
# Keyword-based parser that mimics the Qwen LoRA output.
# Will be replaced by real model inference in production.
#
# Input example:
#   "bos tlg cariin kapal rute bitung k mks buat angkut
#    1.5 ton cakalang fresh, butuh chiller 2-4 C, tlg muat lusa sore ya."
#
# Output format (matches fine-tuned model):
#   {
#     "status": "success",
#     "message": "Bitung siap memuat!",
#     "details": {
#       "origin": "Bitung",
#       "destination": "Makassar",
#       "cargo_type": "cakalang fresh",
#       "weight": 1.5,
#       "unit": "ton",
#       "temp_requirement": "2-4",
#       "delivery_time": "lusa sore"
#     }
#   }

from __future__ import annotations

import re
from typing import Optional

# ── City alias map ──
CITY_ALIASES: dict[str, str] = {
    "ambon": "Ambon",
    "abn": "Ambon",
    "surabaya": "Surabaya",
    "sby": "Surabaya",
    "makassar": "Makassar",
    "mks": "Makassar",
    "ujung pandang": "Makassar",
    "bitung": "Bitung",
    "kendari": "Kendari",
    "ternate": "Ternate",
    "sorong": "Sorong",
    "manado": "Manado",
    "mdo": "Manado",
    "jakarta": "Jakarta",
    "jkt": "Jakarta",
    "jayapura": "Jayapura",
    "merauke": "Merauke",
    "kupang": "Kupang",
    "manokwari": "Manokwari",
    "pelabuhan ambon": "Ambon",
    "pelabuhan surabaya": "Surabaya",
    "pelabuhan makassar": "Makassar",
    "pelabuhan bitung": "Bitung",
}

# ── Commodity patterns ──
COMMODITIES = [
    "tuna beku", "tuna chilled", "tuna segar", "tuna",
    "cakalang fresh", "cakalang", "ikan cakalang",
    "udang beku", "udang", "ikan", "kepiting",
    "rumput laut", "cumi", "bandeng",
    "kopi roasted", "kopi", "beras", "gula",
    "bibit sayur", "sayur", "buah",
    "es krim", "frozen food", "daging beku", "daging",
    "alat packing", "alat packing umkm",
]


def _find_city(text: str, after_keywords: list[str]) -> Optional[str]:
    """Find a city name that appears after one of the given keywords."""
    text_lower = text.lower()
    for kw in after_keywords:
        idx = text_lower.find(kw)
        if idx == -1:
            continue
        # Look at the text after the keyword
        rest = text_lower[idx + len(kw):].strip()
        # Remove leading prepositions
        for prep in ["dari ", "ke ", "k ", "di "]:
            if rest.startswith(prep):
                rest = rest[len(prep):].strip()
                break
        # Try to match a city alias
        for alias, city in sorted(CITY_ALIASES.items(), key=lambda x: -len(x[0])):
            if rest.startswith(alias):
                return city
    return None


def _find_any_city(text: str) -> list[str]:
    """Find all city names mentioned in text, in order of appearance."""
    text_lower = text.lower()
    found: list[tuple[int, str]] = []
    for alias, city in sorted(CITY_ALIASES.items(), key=lambda x: -len(x[0])):
        idx = text_lower.find(alias)
        if idx != -1:
            # Avoid duplicate city
            if city not in [c for _, c in found]:
                found.append((idx, city))
    found.sort(key=lambda x: x[0])
    return [city for _, city in found]


def _extract_weight(text: str) -> tuple[Optional[float], str]:
    """Extract weight and unit from text."""
    # Match patterns like "1.5 ton", "300 kg", "300 kilo"
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(ton|kg|kilo|kilogram)", text.lower())
    if m:
        value = float(m.group(1).replace(",", "."))
        raw_unit = m.group(2)
        unit = "ton" if raw_unit == "ton" else "kg"
        return value, unit
    return None, "kg"


def _extract_temperature(text: str) -> tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract temperature range from text."""
    text_lower = text.lower()

    # Pattern: "minus 18 sampai minus 20", "minus 18 s/d minus 20"
    m = re.search(r"minus\s*(\d+)\s*(?:sampai|s/d|hingga|sd)\s*minus\s*(\d+)", text_lower)
    if m:
        a, b = -int(m.group(1)), -int(m.group(2))
        lo, hi = min(a, b), max(a, b)
        return float(lo), float(hi), f"{lo}_{hi}"

    # Pattern: "suhu 0-4", "chiller 2-4 C", "0 sampai 4 derajat"
    m = re.search(r"(\-?\d+)\s*[-–]\s*(\-?\d+)\s*(?:°?[cC]|derajat)?", text_lower)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        lo, hi = min(a, b), max(a, b)
        return float(lo), float(hi), f"{lo}_{hi}"

    return None, None, None


def _extract_deadline(text: str) -> Optional[str]:
    """Extract delivery/pickup deadline."""
    text_lower = text.lower()
    # Time-of-day patterns
    time_parts = []
    for kw in ["besok pagi", "besok sore", "besok malam", "besok",
                "lusa pagi", "lusa sore", "lusa malam", "lusa",
                "hari ini", "segera", "pagi jam", "pagi ini"]:
        if kw in text_lower:
            time_parts.append(kw)
            break

    # Specific time: "jam 7", "jam 07.00"
    m = re.search(r"jam\s*(\d{1,2}(?:[.:]\d{2})?)\s*(wib|wit|wita)?", text_lower)
    if m:
        time_str = m.group(1).replace(".", ":")
        tz = m.group(2).upper() if m.group(2) else ""
        time_parts.append(f"jam {time_str} {tz}".strip())

    if time_parts:
        return " ".join(dict.fromkeys(time_parts))  # deduplicate, preserve order

    # Pickup-related keyword exists but no specific time
    for kw in ["pickup", "muat", "berangkat", "angkut"]:
        if kw in text_lower:
            return None
    return None


def _extract_commodity(text: str) -> Optional[str]:
    """Extract commodity name from text."""
    text_lower = text.lower()
    for commodity in COMMODITIES:
        if commodity in text_lower:
            return commodity
    return None


def extract_order(raw_text: str) -> dict:
    """
    Mock extractor — parse Indonesian logistics chat into structured JSON.

    Returns the inference output format matching the fine-tuned model:
    {
      "status": "success",
      "message": "...",
      "details": {
        "origin": "...",
        "destination": "...",
        "cargo_type": "...",
        "weight": ...,
        "unit": "...",
        "temp_requirement": "...",
        "delivery_time": "..."
      }
    }
    """
    # ── Extract fields ──
    cities = _find_any_city(raw_text)

    origin = _find_city(raw_text, ["dari ", "asal ", "pelabuhan ", "rute "])
    destination = _find_city(raw_text, ["ke ", "k ", "tujuan "])

    # Fallback: use order of appearance
    if not origin and not destination and len(cities) >= 2:
        origin = cities[0]
        destination = cities[1]
    elif not origin and len(cities) >= 1:
        origin = cities[0] if destination != cities[0] else (cities[1] if len(cities) > 1 else None)
    elif not destination and len(cities) >= 1:
        destination = cities[-1] if origin != cities[-1] else (cities[-2] if len(cities) > 1 else None)

    weight, unit = _extract_weight(raw_text)
    temp_min, temp_max, temp_req = _extract_temperature(raw_text)
    deadline = _extract_deadline(raw_text)
    commodity = _extract_commodity(raw_text)

    # ── Build response ──
    origin_name = origin or "Unknown"
    message = f"{origin_name} siap memuat!"

    return {
        "status": "success",
        "message": message,
        "details": {
            "origin": origin,
            "destination": destination,
            "cargo_type": commodity,
            "weight": weight,
            "unit": unit,
            "temp_requirement": temp_req,
            "delivery_time": deadline,
        },
    }


def inference_to_order_fields(inference: dict) -> dict:
    """
    Convert inference output to PRD-compatible order fields.

    Maps:  cargo_type → commodity
           weight + unit → weight_kg
           temp_requirement → temperature_min_c, temperature_max_c
           delivery_time → pickup_deadline
    """
    details = inference.get("details", {})
    weight = details.get("weight")
    unit = details.get("unit", "kg")

    # Convert to kg
    weight_kg = None
    if weight is not None:
        weight_kg = weight * 1000 if unit == "ton" else weight

    # Parse temp_requirement "2_4" or "2-4" → min=2, max=4
    temp_min = None
    temp_max = None
    temp_req = details.get("temp_requirement")
    if temp_req:
        parts = re.split(r"[_\-]", str(temp_req))
        if len(parts) == 2:
            try:
                temp_min = float(parts[0])
                temp_max = float(parts[1])
            except ValueError:
                pass

    return {
        "origin": details.get("origin"),
        "destination": details.get("destination"),
        "commodity": details.get("cargo_type"),
        "weight_kg": weight_kg,
        "temperature_min_c": temp_min,
        "temperature_max_c": temp_max,
        "pickup_deadline": details.get("delivery_time"),
    }


def compute_confidence(fields: dict) -> dict:
    """Mock confidence scores per field."""
    scores = {}
    for key in ["origin", "destination", "commodity", "weight_kg", "temperature", "pickup_deadline"]:
        if key == "temperature":
            val = fields.get("temperature_min_c")
        else:
            val = fields.get(key)
        scores[key] = 93 + hash(str(val)) % 7 if val is not None else 0
    return scores

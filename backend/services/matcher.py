# ── MuatBalik AI — Matching engine ──
# PRD §6 F4: Hard filter + weighted score.
#
# score = 30% route + 25% capacity + 20% temperature
#       + 15% deadline + 10% price/rating

from __future__ import annotations

from typing import Optional


def match_carriers(order: dict, carriers: list[dict]) -> list[dict]:
    """
    Filter and rank carriers for a given order.

    Returns list of { carrier, score, reasons, status } sorted by score desc.
    Rejected carriers are included with score=0 and status='rejected'.
    """
    results = []

    for carrier in carriers:
        reasons: list[str] = []
        rejected = False
        rejection_reasons: list[str] = []

        # ── Hard constraint 1: Route ──
        route_ok = _route_matches(order, carrier)
        if not route_ok:
            rejected = True
            rejection_reasons.append("Rute tidak cocok")

        # ── Hard constraint 2: Capacity ──
        cap_ok = _capacity_ok(order, carrier)
        if not cap_ok:
            rejected = True
            rejection_reasons.append("Kapasitas tidak cukup")

        # ── Hard constraint 3: Temperature ──
        temp_ok = _temperature_ok(order, carrier)
        if not temp_ok:
            rejected = True
            rejection_reasons.append(
                f"Cold-chain tidak memenuhi suhu "
                f"{order.get('temperature_min_c', '?')}-{order.get('temperature_max_c', '?')} °C"
            )

        # ── Hard constraint 4: No cold-chain at all ──
        if (order.get("temperature_min_c") is not None
                and carrier.get("temperature_min_c") is None
                and carrier.get("temperature_max_c") is None):
            rejected = True
            rejection_reasons.append("Tidak punya cold-chain")

        if rejected:
            results.append({
                "carrier": carrier,
                "score": 0,
                "reasons": rejection_reasons,
                "status": "rejected",
            })
            continue

        # ── Weighted scoring ──
        route_score = _score_route(order, carrier)
        cap_score = _score_capacity(order, carrier)
        temp_score = _score_temperature(order, carrier)
        deadline_score = _score_deadline(order, carrier)
        price_score = _score_price_rating(carrier)

        total = int(
            0.30 * route_score
            + 0.25 * cap_score
            + 0.20 * temp_score
            + 0.15 * deadline_score
            + 0.10 * price_score
        )

        # ── Build reasons ──
        if route_score >= 80:
            reasons.append("Rute cocok" + (" via hub" if _is_transit(order, carrier) else " direct"))
        if cap_score >= 80:
            wt = order.get("weight_kg", 0) or 0
            reasons.append(f"Kapasitas aman untuk {wt:.0f} kg")
        if temp_score >= 80:
            reasons.append(
                f"Range suhu memenuhi "
                f"{order.get('temperature_min_c', '?')}-{order.get('temperature_max_c', '?')} °C"
            )
        if deadline_score >= 60:
            reasons.append("Deadline pickup masih aman")

        results.append({
            "carrier": carrier,
            "score": total,
            "reasons": reasons,
            "status": "valid",
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Mark top scorer as recommended
    if results and results[0]["score"] > 0:
        results[0]["status"] = "recommended"

    return results


# ── Hard-constraint helpers ──

def _route_matches(order: dict, carrier: dict) -> bool:
    o_origin = (order.get("origin") or "").lower()
    o_dest = (order.get("destination") or "").lower()
    c_origin = (carrier.get("origin") or "").lower()
    c_dest = (carrier.get("destination") or "").lower()

    if not o_origin or not o_dest:
        return True  # can't reject without route info

    # Direct match
    if c_origin == o_origin and c_dest == o_dest:
        return True

    # Transit: carrier goes through origin city
    if c_origin == o_origin or c_dest == o_dest:
        return True

    return False


def _capacity_ok(order: dict, carrier: dict) -> bool:
    weight = order.get("weight_kg")
    cap = carrier.get("capacity_kg")
    if weight is None or cap is None:
        return True
    return cap >= weight


def _temperature_ok(order: dict, carrier: dict) -> bool:
    o_min = order.get("temperature_min_c")
    o_max = order.get("temperature_max_c")
    c_min = carrier.get("temperature_min_c")
    c_max = carrier.get("temperature_max_c")

    if o_min is None or o_max is None:
        return True  # no temp requirement
    if c_min is None or c_max is None:
        return False  # order needs cold-chain but carrier has none

    # Carrier range must contain order range
    return c_min <= o_min and c_max >= o_max


def _is_transit(order: dict, carrier: dict) -> bool:
    c_origin = (carrier.get("origin") or "").lower()
    c_dest = (carrier.get("destination") or "").lower()
    o_origin = (order.get("origin") or "").lower()
    o_dest = (order.get("destination") or "").lower()
    return not (c_origin == o_origin and c_dest == o_dest)


# ── Scoring helpers (0-100 each) ──

def _score_route(order: dict, carrier: dict) -> int:
    if _is_transit(order, carrier):
        return 70  # transit = partial score
    return 100  # direct = full score


def _score_capacity(order: dict, carrier: dict) -> int:
    weight = order.get("weight_kg") or 0
    cap = carrier.get("capacity_kg") or 1
    if cap == 0:
        return 0
    ratio = weight / cap
    if ratio <= 0.5:
        return 95
    if ratio <= 0.8:
        return 80
    if ratio <= 1.0:
        return 60
    return 0


def _score_temperature(order: dict, carrier: dict) -> int:
    o_min = order.get("temperature_min_c")
    o_max = order.get("temperature_max_c")
    c_min = carrier.get("temperature_min_c")
    c_max = carrier.get("temperature_max_c")

    if o_min is None or c_min is None:
        return 50  # neutral

    # Tighter carrier range = better
    carrier_range = (c_max or 0) - (c_min or 0)
    order_range = (o_max or 0) - (o_min or 0)

    if carrier_range <= order_range + 2:
        return 95
    if carrier_range <= order_range + 6:
        return 75
    return 55


def _score_deadline(_order: dict, _carrier: dict) -> int:
    # MVP: simplified — all carriers considered on time
    return 80


def _score_price_rating(carrier: dict) -> int:
    rating = carrier.get("rating") or 0
    return min(100, int(rating * 20))

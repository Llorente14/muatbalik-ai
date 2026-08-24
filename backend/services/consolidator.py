# ── MuatBalik AI — Consolidation engine ──
# PRD §6 F5/F6: Backhaul discovery + order consolidation.

from __future__ import annotations


def find_backhaul_orders(
    carrier: dict,
    all_orders: list[dict],
) -> list[dict]:
    """
    Find orders on the inverse (return) route that are compatible
    with the carrier's return trip.
    """
    ret_origin = (carrier.get("return_origin") or "").lower()
    ret_dest = (carrier.get("return_destination") or "").lower()

    if not ret_origin or not ret_dest:
        return []

    candidates = []
    for order in all_orders:
        o_origin = (order.get("origin") or "").lower()
        o_dest = (order.get("destination") or "").lower()
        o_status = order.get("status", "")

        # Must be on the return route and pending
        if o_origin == ret_origin and o_dest == ret_dest and o_status == "pending":
            candidates.append(order)

    return candidates


def pack_compatible_orders(
    orders: list[dict],
    capacity_kg: float,
) -> dict:
    """
    Greedily pack compatible orders into the return capacity.

    Returns {
      "packed_order_ids": [...],
      "total_weight_kg": ...,
      "remaining_kg": ...,
      "temperature_range": "min-max",
      "compatibility_status": "compatible" | "rejected",
    }
    """
    packed: list[str] = []
    total_weight = 0.0
    temp_mins: list[float] = []
    temp_maxs: list[float] = []

    for order in orders:
        weight = order.get("weight_kg") or 0
        if total_weight + weight > capacity_kg:
            continue  # skip, would exceed capacity

        packed.append(order.get("id", ""))
        total_weight += weight

        t_min = order.get("temperature_min_c")
        t_max = order.get("temperature_max_c")
        if t_min is not None:
            temp_mins.append(t_min)
        if t_max is not None:
            temp_maxs.append(t_max)

    # Check temperature compatibility (ranges must overlap)
    compat = "compatible"
    temp_range = ""
    if temp_mins and temp_maxs:
        overall_min = max(temp_mins)  # tightest lower bound
        overall_max = min(temp_maxs)  # tightest upper bound
        if overall_min > overall_max:
            compat = "rejected"
        temp_range = f"{overall_min}-{overall_max}"

    return {
        "packed_order_ids": packed,
        "total_weight_kg": total_weight,
        "remaining_kg": capacity_kg - total_weight,
        "temperature_range": temp_range,
        "compatibility_status": compat,
    }


def compute_load_factor(filled_kg: float, capacity_kg: float) -> float:
    """Load factor as percentage."""
    if capacity_kg <= 0:
        return 0.0
    return round((filled_kg / capacity_kg) * 100, 1)

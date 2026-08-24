# ── MuatBalik AI — Seed fixture data ──
# Populates the database with simulated carriers and backhaul orders
# for the Ambon–Makassar–Surabaya demo scenario.

import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).parent / "muatbalik.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def seed():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")

    # Init schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # ── Carriers (from PRD demo scenario) ──
    carriers = [
        {
            "id": str(uuid.uuid4()),
            "name": "Nusantara Coldline 07",
            "origin": "Ambon",
            "destination": "Surabaya",
            "departure_at": "2024-08-24T07:30:00+09:00",
            "arrival_at": "2024-08-26T18:00:00+07:00",
            "capacity_kg": 1200,
            "capacity_m3": 8.0,
            "temperature_min_c": -2,
            "temperature_max_c": 6,
            "price_idr": 4800000,
            "rating": 4.8,
            "return_origin": "Surabaya",
            "return_destination": "Ambon",
            "return_capacity_kg": 1000,
            "status": "active",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Samudra Reefer Express",
            "origin": "Ambon",
            "destination": "Surabaya",
            "departure_at": "2024-08-24T12:00:00+09:00",
            "arrival_at": "2024-08-27T06:00:00+07:00",
            "capacity_kg": 500,
            "capacity_m3": 4.0,
            "temperature_min_c": 0,
            "temperature_max_c": 5,
            "price_idr": 5600000,
            "rating": 4.6,
            "return_origin": "Surabaya",
            "return_destination": "Ambon",
            "return_capacity_kg": 400,
            "status": "active",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Lintas Timur Dry Cargo",
            "origin": "Ambon",
            "destination": "Surabaya",
            "departure_at": "2024-08-24T09:00:00+09:00",
            "arrival_at": "2024-08-26T22:00:00+07:00",
            "capacity_kg": 2000,
            "capacity_m3": 15.0,
            "temperature_min_c": None,
            "temperature_max_c": None,
            "price_idr": 3200000,
            "rating": 4.3,
            "return_origin": "Surabaya",
            "return_destination": "Ambon",
            "return_capacity_kg": 1800,
            "status": "active",
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Pelni Coldchain Makassar",
            "origin": "Bitung",
            "destination": "Makassar",
            "departure_at": "2024-08-25T06:00:00+08:00",
            "arrival_at": "2024-08-26T14:00:00+08:00",
            "capacity_kg": 2000,
            "capacity_m3": 12.0,
            "temperature_min_c": -5,
            "temperature_max_c": 8,
            "price_idr": 3800000,
            "rating": 4.5,
            "return_origin": "Makassar",
            "return_destination": "Bitung",
            "return_capacity_kg": 1500,
            "status": "active",
        },
    ]

    for c in carriers:
        conn.execute(
            """INSERT OR IGNORE INTO carriers
               (id, name, origin, destination, departure_at, arrival_at,
                capacity_kg, capacity_m3, temperature_min_c, temperature_max_c,
                price_idr, rating, return_origin, return_destination,
                return_capacity_kg, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                c["id"], c["name"], c["origin"], c["destination"],
                c["departure_at"], c["arrival_at"],
                c["capacity_kg"], c["capacity_m3"],
                c["temperature_min_c"], c["temperature_max_c"],
                c["price_idr"], c["rating"],
                c["return_origin"], c["return_destination"],
                c["return_capacity_kg"], c["status"],
            ),
        )

    # ── Backhaul demo orders (Surabaya → Ambon) ──
    backhaul_orders = [
        {
            "id": str(uuid.uuid4()),
            "raw_text": "kopi roasted 180 kg Surabaya ke Ambon, suhu ruang",
            "origin": "Surabaya",
            "destination": "Ambon",
            "commodity": "kopi roasted",
            "weight_kg": 180,
            "temperature_min_c": 15,
            "temperature_max_c": 25,
            "pickup_deadline": "besok sore",
        },
        {
            "id": str(uuid.uuid4()),
            "raw_text": "alat packing UMKM 220 kg Surabaya ke Ambon",
            "origin": "Surabaya",
            "destination": "Ambon",
            "commodity": "alat packing umkm",
            "weight_kg": 220,
            "temperature_min_c": 15,
            "temperature_max_c": 25,
            "pickup_deadline": "lusa pagi",
        },
        {
            "id": str(uuid.uuid4()),
            "raw_text": "bibit sayur chilled 140 kg Makassar ke Ambon, suhu 2-8 C",
            "origin": "Makassar",
            "destination": "Ambon",
            "commodity": "bibit sayur",
            "weight_kg": 140,
            "temperature_min_c": 2,
            "temperature_max_c": 8,
            "pickup_deadline": "besok pagi",
        },
    ]

    for o in backhaul_orders:
        conn.execute(
            """INSERT OR IGNORE INTO orders
               (id, raw_text, origin, destination, commodity, weight_kg,
                temperature_min_c, temperature_max_c, pickup_deadline, status)
               VALUES (?,?,?,?,?,?,?,?,?,'pending')""",
            (
                o["id"], o["raw_text"], o["origin"], o["destination"],
                o["commodity"], o["weight_kg"],
                o["temperature_min_c"], o["temperature_max_c"],
                o["pickup_deadline"],
            ),
        )

    conn.commit()
    conn.close()
    print(f"[OK] Seeded {len(carriers)} carriers and {len(backhaul_orders)} backhaul orders")
    print(f"  Database: {DB_PATH}")


if __name__ == "__main__":
    seed()

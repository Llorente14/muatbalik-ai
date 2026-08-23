-- ============================================================
-- MuatBalik AI — Database Schema (SQLite MVP)
-- Source: PRD Section 8 "Data model MVP"
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ────────────────────────────────────────────────────────────
-- 1. orders (PRD §8 explicit)
-- Raw and parsed order from shipper/UMKM.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
    id                 TEXT PRIMARY KEY,
    raw_text           TEXT    NOT NULL,
    origin             TEXT,
    destination        TEXT,
    commodity          TEXT,
    weight_kg          REAL,
    volume_m3          REAL,
    temperature_min_c  REAL,
    temperature_max_c  REAL,
    pickup_deadline    TEXT,
    delivery_deadline  TEXT,
    status             TEXT    NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending','confirmed','matched')),
    created_at         TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ────────────────────────────────────────────────────────────
-- 2. carriers (PRD §8 explicit)
-- Fleet registry: route, capacity, cold-chain, return info.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS carriers (
    id                   TEXT PRIMARY KEY,
    name                 TEXT    NOT NULL,
    origin               TEXT    NOT NULL,
    destination          TEXT    NOT NULL,
    departure_at         TEXT,
    arrival_at           TEXT,
    capacity_kg          REAL    NOT NULL DEFAULT 0,
    capacity_m3          REAL,
    temperature_min_c    REAL,
    temperature_max_c    REAL,
    price_idr            INTEGER NOT NULL DEFAULT 0,
    rating               REAL    DEFAULT 0,
    return_origin        TEXT,
    return_destination   TEXT,
    return_capacity_kg   REAL    DEFAULT 0,
    status               TEXT    NOT NULL DEFAULT 'active'
                         CHECK (status IN ('active','inactive'))
);

-- ────────────────────────────────────────────────────────────
-- 3. shipments (PRD §8 implicit — required by tracking_events,
--    API /shipments, and dual status machine)
-- Bridge: links one order to one carrier.
-- Holds independent shipment_status and backhaul_status.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shipments (
    id                TEXT PRIMARY KEY,
    order_id          TEXT    NOT NULL REFERENCES orders(id),
    carrier_id        TEXT    NOT NULL REFERENCES carriers(id),
    shipment_status   TEXT    NOT NULL DEFAULT 'pending'
                      CHECK (shipment_status IN (
                          'pending','confirmed','in_transit','delivered'
                      )),
    backhaul_status   TEXT    NOT NULL DEFAULT 'searching'
                      CHECK (backhaul_status IN (
                          'searching','pre_booked','partially_filled',
                          'filled','unfilled'
                      )),
    match_score       INTEGER DEFAULT 0,
    match_reasons     TEXT,            -- JSON array of strings
    created_at        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ────────────────────────────────────────────────────────────
-- 4. backhaul_slots (PRD §8 explicit)
-- Return-trip capacity slot on a carrier.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS backhaul_slots (
    id                   TEXT PRIMARY KEY,
    carrier_id           TEXT    NOT NULL REFERENCES carriers(id),
    origin               TEXT    NOT NULL,
    destination          TEXT    NOT NULL,
    departure_at         TEXT,
    capacity_kg          REAL    NOT NULL DEFAULT 0,
    filled_kg            REAL    NOT NULL DEFAULT 0,
    prebook_discount_pct INTEGER DEFAULT 0,
    status               TEXT    NOT NULL DEFAULT 'searching'
                         CHECK (status IN (
                             'searching','pre_booked','partially_filled',
                             'filled','unfilled'
                         ))
);

-- ────────────────────────────────────────────────────────────
-- 5. consolidations (PRD §8 explicit)
-- Groups multiple small orders into one backhaul slot.
-- order_ids stored as JSON array for MVP simplicity.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS consolidations (
    id                   TEXT PRIMARY KEY,
    backhaul_slot_id     TEXT    NOT NULL REFERENCES backhaul_slots(id),
    order_ids            TEXT    NOT NULL DEFAULT '[]',  -- JSON array
    total_weight_kg      REAL    NOT NULL DEFAULT 0,
    temperature_range    TEXT,
    compatibility_status TEXT    NOT NULL DEFAULT 'compatible'
                         CHECK (compatibility_status IN ('compatible','rejected')),
    created_at           TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ────────────────────────────────────────────────────────────
-- 6. tracking_events (PRD §8 explicit)
-- Simulated logistics events for a shipment.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tracking_events (
    id              TEXT PRIMARY KEY,
    shipment_id     TEXT    NOT NULL REFERENCES shipments(id),
    event_type      TEXT    NOT NULL
                    CHECK (event_type IN (
                        'departed','delayed','temperature_excursion','arrived'
                    )),
    temperature_c   REAL,
    location        TEXT,
    note            TEXT,
    created_at      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);

-- ────────────────────────────────────────────────────────────
-- Indexes for common queries
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_orders_status
    ON orders(status);

CREATE INDEX IF NOT EXISTS idx_carriers_route
    ON carriers(origin, destination);

CREATE INDEX IF NOT EXISTS idx_carriers_return_route
    ON carriers(return_origin, return_destination);

CREATE INDEX IF NOT EXISTS idx_shipments_order
    ON shipments(order_id);

CREATE INDEX IF NOT EXISTS idx_shipments_carrier
    ON shipments(carrier_id);

CREATE INDEX IF NOT EXISTS idx_shipments_status
    ON shipments(shipment_status, backhaul_status);

CREATE INDEX IF NOT EXISTS idx_backhaul_slots_carrier
    ON backhaul_slots(carrier_id);

CREATE INDEX IF NOT EXISTS idx_backhaul_slots_route
    ON backhaul_slots(origin, destination);

CREATE INDEX IF NOT EXISTS idx_tracking_events_shipment
    ON tracking_events(shipment_id);

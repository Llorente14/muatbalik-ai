# MuatBalik AI

Static frontend mockup for the MuatBalik AI hackathon MVP.

## Current scope

- Vite + React + TypeScript frontend.
- Tailwind CSS v4 styling.
- Lucide icons and Recharts charts.
- Static simulated data for order extraction, carrier matching, async backhaul, consolidation, pre-booking, and control tower analytics.
- No real carrier data, booking, payment, or backend integration yet.

## Run locally

```bash
npm install
npm run dev
```

Production build:

```bash
npm run build
```

## PRD alignment

- `/order` equivalent: order intake, voice upload mock, extracted JSON, confidence per field.
- `/matching/:orderId` equivalent: candidate carriers, hard-constraint rejection, scoring, recommendation reasons.
- `/backhaul/:shipmentId` equivalent: inverse route, consolidation candidates, pre-booking slot.
- `/control-tower` equivalent: KPI cards, status table, load-factor chart, response-time chart, tracking simulator.

The current implementation is a single responsive static page with anchor navigation. Backend, model serving, and training folders can be added in the next phase.

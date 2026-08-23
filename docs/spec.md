# PRD — MuatBalik AI

**Status:** Hackathon MVP specification  
**Tema:** Smart Commerce / Logistics  
**Target demo:** 2–3 hari implementasi  
**Primary user:** UMKM/shipper pangan segar, freight forwarder, operator cold-storage  
**Core promise:** Pengiriman utama tetap berjalan; AI mencari muatan balik secara paralel untuk menaikkan load factor perjalanan balik.

## 1. Ringkasan produk

MuatBalik AI adalah **decision-support control tower**, bukan marketplace kapal penuh. User mengirim order melalui form/chat simulator atau voice note. Model AI yang sudah di-fine-tune memahami bahasa logistik Indonesia dan mengubah order menjadi JSON. Backend lalu memfilter serta me-ranking armada berdasarkan rute, kapasitas, suhu, dan deadline. Setelah armada utama dipilih, sistem mencari order pada rute balik, menggabungkan beberapa order kecil melalui consolidation, atau membuka slot pre-booking jika belum ada muatan.

Pengiriman utama tidak menunggu backhaul. Status utama dan status backhaul disimpan terpisah.

```text
shipment_status: pending → confirmed → in_transit → delivered
backhaul_status: searching → pre_booked → partially_filled → filled / unfilled
```

## 2. Problem statement

Biaya logistik Indonesia diperkirakan sekitar **14,29% dari PDB**. Pemerintah juga mengidentifikasi masalah informasi yang tidak simetris dan kurangnya integrasi antarpelaku logistik. [Kemenko Perekonomian](https://www.ekon.go.id/publikasi/detail/5380/capai-pertumbuhan-ekonomi-berkualitas-menko-airlangga-tegaskan-logistik-menjadi-key-driver-utama)

Wilayah kepulauan menghadapi masalah tambahan: armada membawa kebutuhan ke wilayah Timur Indonesia, tetapi sering kembali dengan kapasitas minim atau kosong. Kemenhub menyebut pengisian muatan balik dan ketersediaan cold-storage sebagai tantangan penting. [Kemenhub](https://dephub.go.id/portal-kemenhub/index.php/post/read/menghidupkan-nadi-logistik-wilayah-3tp--tantangan-muatan-balik-dari-timur-indonesia)

Order UMKM/nelayan masih tersebar di WhatsApp dan telepon. Informasi penting seperti berat, suhu, rute, dan deadline tidak terstruktur. Akibatnya shipper sulit menemukan armada yang cocok, carrier kehilangan potensi muatan, dan produk segar berisiko rusak.

### Problem statement pitch

> Nelayan dan UMKM pangan di Indonesia Timur kesulitan menemukan armada yang sesuai dengan kapasitas, suhu, rute, dan deadline pengiriman. Pada saat yang sama, banyak kapal kembali dengan kapasitas kosong. Karena order masih tersebar di chat dan telepon, muatan yang sebenarnya cocok tidak pernah bertemu.

## 3. Goals dan non-goals

### Goals MVP

1. Mengubah chat/voice order menjadi JSON logistik yang konsisten.
2. Memberi rekomendasi armada yang tidak melanggar constraint wajib.
3. Mencari dan menggabungkan muatan balik secara asynchronous.
4. Membuka slot pre-booking dengan harga backhaul demo ketika belum ada order.
5. Menampilkan dashboard status pengiriman dan load factor sebelum/sesudah.
6. Membuktikan fine-tuning melalui dataset, script training, adapter model, dan evaluasi holdout.

### Non-goals

- Tidak membuat jaringan kapal nasional.
- Tidak melakukan booking atau pembayaran sungguhan.
- Tidak mengklaim data kapal real-time.
- Tidak mengintegrasikan WhatsApp Business secara penuh untuk MVP.
- Tidak membuat model speech-to-text dari nol.
- Tidak memblokir pengiriman utama ketika backhaul kosong.

## 4. Persona dan use case utama

### Shipper — UMKM/nelayan

Memasukkan order seperti: "300 kg tuna Ambon ke Surabaya, suhu 0–4°C, pickup besok pagi." Mereka ingin pilihan armada yang cepat, aman, dan transparan.

### Carrier/operator kapal

Memasukkan rute, jadwal, kapasitas, kemampuan cold-chain, dan kapasitas balik. Mereka ingin mengisi kapasitas yang seharusnya kosong.

### Control-tower operator

Melihat order, kandidat armada, status backhaul, dan anomali. Operator dapat menyetujui atau menolak rekomendasi AI.

## 5. User journey end-to-end

1. Shipper mengetik order atau mengunggah voice note.
2. Voice note ditranskrip menggunakan speech-to-text pretrained.
3. Qwen yang sudah di-fine-tune mengekstrak `origin`, `destination`, `weight`, `commodity`, `temperature`, dan `deadline`.
4. UI menampilkan hasil ekstraksi dan meminta konfirmasi jika field penting belum lengkap.
5. Matching engine menerapkan hard constraint: rute, kapasitas, suhu, dan deadline.
6. Kandidat yang lolos diberi skor berdasarkan waktu, biaya, rating, dan kecocokan kapasitas.
7. Shipper memilih atau operator menyetujui armada utama. `shipment_status` menjadi `confirmed` tanpa menunggu backhaul.
8. Backhaul engine mencari order pada rute balik dengan jadwal yang kompatibel.
9. Beberapa order kecil digabungkan jika total berat/volume masih di bawah kapasitas.
10. Jika belum ada order, sistem membuat `backhaul_slot` dan menawarkan harga diskon simulasi.
11. Jika tetap kosong, status menjadi `unfilled`, tetapi shipment tetap berjalan.
12. Dashboard menampilkan load factor sebelum dan sesudah consolidation.
13. Operator dapat memasukkan event suhu/keterlambatan simulasi dan melihat rekomendasi cold-storage/transit hub.

## 6. Feature scope

### F1 — Order intake

- Form input teks.
- Chat simulator dengan beberapa contoh prompt.
- Upload audio opsional.
- Tombol "Parse order".

### F2 — AI order extraction

- Menjalankan model fine-tuned.
- Menampilkan JSON dan confidence per field.
- Menandai field wajib yang kosong.
- User dapat mengedit JSON sebelum matching.

### F3 — Fleet registry

- CRUD data armada dummy.
- Field: carrier, route, departure, arrival, capacity, temperature range, price, rating, return route, return capacity.
- Import CSV/JSON untuk mempercepat setup demo.

### F4 — Primary shipment matching

- Hard filter untuk constraint wajib.
- Weighted score untuk kandidat yang lolos.
- Explanation "mengapa direkomendasikan".
- Pengiriman utama tidak bergantung pada hasil backhaul.

### F5 — Backhaul discovery

- Mencari order pada inverse route.
- Menghitung kapasitas kosong.
- Menampilkan kandidat consolidation.
- Membuat slot pre-booking jika belum ada order.
- Menetapkan status `searching`, `pre_booked`, `partially_filled`, `filled`, atau `unfilled`.

### F6 — Consolidation

- Mengelompokkan order dengan origin/destination, time window, dan temperature range yang kompatibel.
- Menolak kombinasi yang melebihi berat/volume atau melanggar suhu.
- Menampilkan load factor sebelum/sesudah.

### F7 — Route alternative

- Jika direct route tidak tersedia, menampilkan satu transit hub dari fixture data, misalnya Makassar.
- Menampilkan cold-storage alternatif di hub.
- Tidak perlu melakukan route optimization geografis kompleks untuk MVP.

### F8 — Tracking simulator

- Input event manual: departed, delayed, temperature excursion, arrived.
- Alert jika suhu berada di luar range.
- Rekomendasi transit hub/cold-storage dari daftar fixture.

### F9 — Demo analytics

- Primary shipments confirmed/delivered.
- Backhaul filled/unfilled.
- Load factor sebelum dan sesudah.
- Jumlah order yang berhasil dikonsolidasikan.
- Waktu respons parse dan matching.

## 7. Model dan implementasi AI

### Model wajib: order extractor

**Base model:** `Qwen/Qwen2.5-1.5B-Instruct`  
**Training:** QLoRA/PEFT 4-bit  
**Task:** instruction-to-JSON extraction untuk chat logistik berbahasa Indonesia.

Input:

```text
Cari kapal 300 kilo tuna dari Ambon ke Surabaya, suhu 0-4 derajat, berangkat besok pagi.
```

Target output:

```json
{
  "origin": "Ambon",
  "destination": "Surabaya",
  "commodity": "tuna",
  "weight_kg": 300,
  "temperature_min_c": 0,
  "temperature_max_c": 4,
  "pickup_deadline": "besok pagi"
}
```

### Dataset fine-tuning

Gunakan 500–1.000 contoh JSONL yang dibuat dari template dan direview manusia. Variasi minimal:

- Bahasa Indonesia formal dan bahasa chat.
- Typo, singkatan, campuran angka/satuan.
- Voice transcript dengan filler words.
- Field tidak lengkap.
- Nama pelabuhan dan kota Indonesia.
- Komoditas kering vs chilled/frozen.

Split dataset:

```text
80% train / 10% validation / 10% held-out test
```

Tidak boleh menggunakan test set untuk membuat prompt atau memperbaiki label.

### Training configuration target

- 4-bit quantization.
- LoRA rank 16, alpha 32, dropout 0.05.
- 3 epoch sebagai titik awal.
- Learning rate `2e-4` untuk adapter.
- Gradient accumulation agar bisa berjalan di GPU Colab.
- Simpan adapter dan tokenizer di `models/order-extractor-lora/`.

### Inference pipeline

```text
audio → speech-to-text pretrained → Qwen LoRA → JSON schema validation → user confirmation
```

Speech-to-text memakai Whisper/faster-whisper pretrained; Whisper tidak perlu di-fine-tune untuk MVP.

### Matching model

MVP memakai deterministic hybrid engine, bukan LLM:

1. Hard filters: rute, kapasitas, suhu, deadline.
2. Weighted score:

```text
score = 30% route + 25% capacity + 20% temperature
      + 15% deadline + 10% price/rating
```

3. Optional phase 2: fine-tune `intfloat/multilingual-e5-base` dengan positive/negative order–carrier pairs untuk ranking semantik. Fitur ini tidak wajib untuk demo pertama.

### Guardrail

- Model tidak boleh mengubah constraint yang dikonfirmasi user.
- Rule engine berhak menolak rekomendasi model.
- Semua rekomendasi menampilkan alasan dan data sumbernya.
- Operator dapat override dan mencatat alasan.

## 8. Data model MVP

### `orders`

```text
id, raw_text, origin, destination, commodity, weight_kg,
volume_m3, temperature_min_c, temperature_max_c,
pickup_deadline, delivery_deadline, status, created_at
```

### `carriers`

```text
id, name, origin, destination, departure_at, arrival_at,
capacity_kg, capacity_m3, temperature_min_c, temperature_max_c,
price_idr, rating, return_origin, return_destination,
return_capacity_kg, status
```

### `backhaul_slots`

```text
id, carrier_id, origin, destination, departure_at,
capacity_kg, filled_kg, prebook_discount_pct, status
```

### `consolidations`

```text
id, backhaul_slot_id, order_ids, total_weight_kg,
temperature_range, compatibility_status, created_at
```

### `tracking_events`

```text
id, shipment_id, event_type, temperature_c,
location, note, created_at
```

## 9. Backend implementation

### Recommended stack

- **API:** FastAPI + Pydantic.
- **Database:** SQLite untuk demo; PostgreSQL jika deploy.
- **Model serving:** Transformers + PEFT; optional vLLM jika GPU server tersedia.
- **Matching:** Python service dengan pure functions yang mudah dites.
- **Background jobs:** FastAPI BackgroundTasks untuk backhaul search; Celery/Redis tidak wajib.
- **Storage:** local files untuk audio dan model pada MVP.

### Service modules

```text
backend/
  api/orders.py          # parse dan CRUD order
  api/matching.py        # kandidat armada
  api/backhaul.py        # slot dan consolidation
  api/tracking.py        # event simulasi
  services/extractor.py  # Qwen LoRA inference
  services/matcher.py    # hard constraint + scoring
  services/consolidator.py
  services/alternatives.py
  db/models.py
  schemas.py
```

### API endpoints

```text
POST /api/orders/parse
POST /api/orders
GET  /api/orders/{id}
POST /api/shipments/{id}/match
GET  /api/shipments/{id}/candidates
POST /api/shipments/{id}/confirm
GET  /api/shipments/{id}/backhaul
POST /api/backhaul/{slot_id}/prebook
POST /api/backhaul/{slot_id}/consolidate
POST /api/shipments/{id}/tracking-events
GET  /api/dashboard/metrics
```

### Backhaul behavior

```python
confirm_primary_shipment(order, carrier)
set_backhaul_status(carrier, "searching")

matches = find_inverse_route_orders(carrier)
if matches:
    consolidation = pack_compatible_orders(matches, carrier.return_capacity)
    update_backhaul(consolidation)
else:
    create_prebooking_slot(carrier, discount_pct=15)

# shipment_status remains confirmed/in_transit regardless of backhaul outcome
```

## 10. Frontend implementation

### Recommended stack

- Next.js/React.
- Tailwind CSS.
- React Query untuk API state.
- MapLibre atau peta statis untuk demo rute.
- Recharts untuk load-factor chart.

### Screens

#### `/order`

- Chat simulator/text area.
- Upload audio.
- "Parse order".
- Editable extracted JSON.
- "Find shipment".

#### `/matching/:orderId`

- Ringkasan order.
- Card kandidat armada.
- Score dan alasan rekomendasi.
- Warning constraint.
- Tombol confirm.

#### `/backhaul/:shipmentId`

- Rute utama dan inverse route.
- Kapasitas balik total/terisi.
- Order kecil yang bisa digabung.
- Tombol pre-booking.
- Status `searching`, `partially_filled`, `filled`, atau `unfilled`.

#### `/control-tower`

- KPI cards.
- Shipment status.
- Backhaul status.
- Load factor chart.
- Simulasi event suhu/keterlambatan.

## 11. Data sources dan penggunaan

### Sumber problem validation

- [Kemenko Perekonomian — biaya logistik dan integrasi logistik](https://www.ekon.go.id/publikasi/detail/5380/capai-pertumbuhan-ekonomi-berkualitas-menko-airlangga-tegaskan-logistik-menjadi-key-driver-utama)
- [Kemenhub — tantangan muatan balik wilayah 3TP](https://dephub.go.id/portal-kemenhub/index.php/post/read/menghidupkan-nadi-logistik-wilayah-3tp--tantangan-muatan-balik-dari-timur-indonesia)
- [BPS — Statistik E-Commerce 2023](https://www.bps.go.id/id/publication/2025/01/30/d52af11843aee401403ecfa6)
- [Ringkasan studi Bappenas/Bapanas tentang food loss/waste](https://www.antaranews.com/berita/4394698/bapanas-dapat-dukungan-denmark-soal-pangan-di-indonesia)

### Sumber teknis opsional

- [OpenStreetMap](https://www.openstreetmap.org/) untuk koordinat pelabuhan/hub.
- [Geofabrik OpenStreetMap extracts](https://download.geofabrik.de/) jika membutuhkan data geospasial lokal.
- [Mozilla Common Voice datasets](https://commonvoice.mozilla.org/en/datasets) sebagai referensi voice dataset; voice logistics sendiri dibuat dari transcript sintetis/anonymized.

### Strategi data MVP

Jangan mengklaim data carrier real-time. Gunakan fixture anonim/sintetis dengan skenario Ambon–Makassar–Surabaya, termasuk kapasitas, jadwal, suhu, harga, dan order balik. Cantumkan label `SIMULATED` pada dashboard.

## 12. KPI dan acceptance criteria

### KPI demo

- Order extraction menghasilkan JSON valid pada minimal 90% held-out test set.
- Tidak ada kandidat final yang melanggar hard constraint.
- Backhaul consolidation meningkatkan load factor pada skenario simulasi; contoh target demo 10% → 60%.
- Minimal satu shipment utama tetap `in_transit` saat backhaul berstatus `unfilled`.
- Minimal satu skenario berhasil membuat pre-booking slot.
- Minimal satu skenario berhasil menggabungkan dua atau lebih order kecil.
- P95 parse + matching di bawah 10 detik pada environment demo.

### Acceptance scenarios

1. **Direct + backhaul found:** order utama dikonfirmasi, dua order balik terkonsolidasi.
2. **No backhaul:** shipment tetap berjalan, slot pre-booking dibuat.
3. **Invalid carrier:** carrier tanpa cold-chain ditolak.
4. **Partial fill:** satu order balik masuk, status berubah `partially_filled`.
5. **No direct route:** sistem menampilkan transit hub dan cold-storage alternatif.
6. **Temperature excursion:** alert muncul dan rekomendasi hub alternatif ditampilkan.

## 13. Timeline implementasi hackathon

### Hari 1 — Core flow

- Buat schema database dan fixture data.
- Buat training dataset JSONL.
- Jalankan fine-tuning QLoRA di Colab.
- Buat endpoint parse order.

### Hari 2 — Matching dan backhaul

- Implement hard filter dan scoring.
- Implement inverse-route search.
- Implement consolidation dan pre-booking.
- Buat dashboard matching/backhaul.

### Hari 3 — Polish dan demo

- Tambah voice input.
- Tambah tracking simulator.
- Tambah load-factor chart.
- Jalankan held-out evaluation.
- Rekam demo dan rapikan pitch.

## 14. Struktur repository

```text
muatbalik-ai/
  frontend/
  backend/
  training/
    dataset/
    train_order_extractor.py
    evaluate_order_extractor.py
  models/
  data/
    carriers.simulated.json
    orders.simulated.json
    ports.simulated.json
  docs/
  README.md
```

## 15. Demo script

1. Masukkan voice note order tuna Ambon → Surabaya.
2. Tampilkan hasil ekstraksi Qwen LoRA.
3. Tunjukkan dua kapal ditolak karena constraint suhu/kapasitas.
4. Pilih kapal yang memenuhi syarat.
5. Tampilkan status shipment `confirmed`.
6. Buka halaman backhaul dan masukkan dua order kecil Surabaya → Ambon.
7. Jalankan consolidation.
8. Tampilkan load factor sebelum/sesudah.
9. Hapus satu order balik dan tunjukkan sistem membuat pre-booking.
10. Tegaskan bahwa shipment utama tetap berjalan walau backhaul belum terisi.

## 16. Inspirasi implementasi AI

- [CrisisConnect / AIdmatch](https://github.com/gsinchan135/AIdmatch) — pola fine-tuned BERT dan matching.
- [AgriMind](https://github.com/ClosetCoderSad/AgriMind-LAHacks/tree/asus-supercomputer-ML) — contoh fine-tuning LoRA untuk konteks agrifood.
- [DispatcherAI](https://github.com/DispatcherAI/DispatcherAI) — contoh fine-tuned model untuk triage operasional.

## 17. Risiko dan mitigasi

| Risiko | Mitigasi MVP |
|---|---|
| Data kapal real-time tidak tersedia | Gunakan fixture sintetis dan label SIMULATED |
| Model mengeluarkan JSON invalid | Pydantic validation + retry dengan schema |
| Rekomendasi melanggar suhu/kapasitas | Hard constraint selalu dijalankan setelah model |
| Fine-tuning terlalu lama | QLoRA 4-bit, model 1.5B, dataset kecil |
| Demo terlihat seperti marketplace biasa | Tonjolkan asynchronous backhaul, consolidation, dan load-factor chart |
| KPI disalahartikan sebagai dampak nasional | Tulis "hasil simulasi skenario demo" di UI dan pitch |

## 18. Definition of done

MVP dianggap selesai jika user dapat memasukkan satu order, melihat JSON hasil fine-tuned model, mendapatkan rekomendasi armada valid, mengonfirmasi shipment utama tanpa menunggu backhaul, melihat pencarian/consolidation/pre-booking order balik, dan melihat dashboard load factor dari data simulasi.

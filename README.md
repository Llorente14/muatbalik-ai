# MuatBalik AI — Decision-Support Control Tower MVP

MVP untuk membantu UMKM, Freight Forwarder, dan Operator Cold-Storage mencocokkan muatan utama dan menemukan peluang muatan balik (backhaul) menggunakan AI.

## Batasan Ruang Lingkup

1. **Frontend (UI):** Hanya alur interaksi inti — input chat dari pengguna dan output AI & rekomendasi. Tidak ada dashboard analitik, auth, atau riwayat.
2. **Backend (API):** Arsitektur sinkron, tanpa background jobs, tanpa infrastruktur DB terdistribusi (SQLite lokal). Sepenuhnya dapat direproduksi via Docker Compose.
3. **Model AI:** Inferensi utama dengan parameter statis. Inferensi mock dapat langsung diganti dengan endpoint model LLM fine-tuned (lihat bagian Integrasi Model AI).

## Menjalankan Aplikasi (Docker Compose)

Pastikan Docker dan Docker Compose sudah terinstall.

1. Clone repositori ini dan masuk ke direktori utama.
2. Jalankan:
   ```bash
   docker-compose up --build
   ```
3. Tunggu proses build selesai hingga log mengindikasikan server menyala.

### Akses Layanan

- UI / Frontend: [http://localhost:5173](http://localhost:5173)
- Dokumentasi API (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
- API Base URL: `http://localhost:8000`

## Menjalankan Tanpa Docker (Manual Lokal)

### 1. Backend (Terminal 1)

```bash
cd backend
pip install -r requirements.txt
python db/seed.py  # opsional, mengisi database lokal
python -m uvicorn main:app --reload --port 8000
```

API berjalan di `http://127.0.0.1:8000`

### 2. Frontend (Terminal 2)

```bash
npm install
npm run dev
```

Buka browser di `http://localhost:5173`

## Daftar API Utama

Dokumentasi interaktif tersedia di `http://localhost:8000/docs`. Endpoint inti:

- `POST /api/orders/parse` — mengekstrak teks chat logistik bahasa natural menjadi Order (JSON) via AI.
- `POST /api/shipments/{id}/match` — menjalankan algoritma skor (hard constraints: suhu, rute, kapasitas) untuk mencari kapal/armada terbaik.

## Integrasi Model AI Asli

Logika ekstraksi saat ini berada di `backend/services/extractor.py` menggunakan mock inference. Setelah model dilatih (misalnya via Unsloth/LoRA) dan di-hosting (misalnya via Ollama atau vLLM), perbarui file tersebut:

```python
# backend/services/extractor.py
import requests

def extract_order(raw_text: str) -> dict:
    response = requests.post("URL_MODEL_ANDA", json={"prompt": raw_text})
    return response.json()
```

UI dan arsitektur database tidak perlu diubah — sistem akan otomatis merender hasil dari model AI asli.
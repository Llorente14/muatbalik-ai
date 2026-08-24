# MuatBalik AI — Decision-Support Control Tower MVP

Proyek ini adalah MVP (Minimum Viable Product) untuk membantu UMKM, Freight Forwarder, dan Operator Cold-Storage dalam mencocokkan muatan utama dan menemukan peluang muatan balik (backhaul) menggunakan AI.

---

## 🎯 Kepatuhan Terhadap Batasan Ruang Lingkup (Sesuai Ketentuan)

Proyek ini dirancang **secara ketat** mematuhi batasan penyisihan:
1. **Frontend (UI):** Hanya berfokus pada alur interaksi inti (menerima input tunggal (chat) dari pengguna dan menampilkan output AI & rekomendasi). Tidak ada dashboard analitik tingkat lanjut, auth, atau riwayat.
2. **Backend (API):** Menggunakan arsitektur sinkron (*synchronous interaction*) tanpa *background jobs*, tanpa infrastruktur DB terdistribusi (hanya menggunakan SQLite lokal). **Sepenuhnya dapat direproduksi via Docker Compose.**
3. **Model AI:** Berfokus pada inferensi utama dengan parameter statis. Arsitektur telah disiapkan sedemikian rupa agar inferensi AI mentah (Mock) dapat langsung diganti dengan endpoint Model LLM Fine-Tuned kapan saja (lihat bagian Integrasi Model AI).

---

## 🚀 Cara Menjalankan Aplikasi (Docker Compose)

Pastikan **Docker** dan **Docker Compose** sudah terinstall di sistem Anda.

1. Clone repositori ini dan masuk ke direktori utama.
2. Jalankan perintah berikut di terminal:
   ```bash
   docker-compose up --build
   ```
3. Tunggu hingga proses *build* selesai dan pesan logs mengindikasikan server menyala.

### Akses Layanan:
- **UI / Frontend Aplikasi:** [http://localhost:5173](http://localhost:5173)
- **Dokumentasi API (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Base URL:** `http://localhost:8000`

---

## 💻 Cara Menjalankan Tanpa Docker (Manual Lokal)

Jika Anda ingin menjalankan tanpa Docker, ikuti panduan berikut:

### 1. Menjalankan Backend (Terminal 1)
```bash
cd backend
pip install -r requirements.txt
python db/seed.py  # (Opsional) Mengisi database lokal
python -m uvicorn main:app --reload --port 8000
```
API akan berjalan di `http://127.0.0.1:8000`

### 2. Menjalankan Frontend (Terminal 2)
```bash
npm install
npm run dev
```
Buka browser di `http://localhost:5173`

---

## 🧩 Daftar API Utama (Swagger)

Akses **http://localhost:8000/docs** untuk menguji endpoint secara interaktif.  
Endpoint inti untuk alur MVP ini meliputi:
- `POST /api/orders/parse` : Mengirim teks chat logistik bahasa natural untuk diekstrak menjadi Order (Format JSON) oleh AI.
- `POST /api/shipments/{id}/match` : Menjalankan algoritma skor (*Hard constraints* Suhu, Rute, Kapasitas) untuk mencari Kapal/Armada terbaik.

---

## 🧠 Integrasi Model AI Asli (Untuk Tahap Selanjutnya)

Pada MVP ini, logika ekstraksi berada di **`backend/services/extractor.py`** menggunakan *mock inference*. Jika Anda sudah melatih model menggunakan *Unsloth/LoRA* dan mem-hosting-nya (misalnya melalui Ollama atau vLLM), Anda cukup memperbarui file tersebut:

```python
# Di dalam backend/services/extractor.py
import requests

def extract_order(raw_text: str) -> dict:
    # Cukup ganti dengan panggilan API ke model lokal/remote Anda
    response = requests.post("URL_MODEL_ANDA", json={"prompt": raw_text})
    return response.json()
```
Seluruh UI dan arsitektur database tidak perlu diubah, sistem akan otomatis merender hasil dari model AI asli.

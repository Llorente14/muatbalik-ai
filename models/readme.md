# Model

Model bisa di-download dari sini: `<ISI_LINK_HUGGINGFACE>`

## Menjalankan model lokal

Simpan file `.gguf` di folder ini, lalu jalankan llama.cpp server:

```bash
llama-server -m models/order-extractor.Q4_K_M.gguf --host 0.0.0.0 --port 8080
```

Backend akan memakai model server jika `MODEL_BASE_URL` diisi:

```text
MODEL_BASE_URL=http://localhost:8080/v1
MODEL_NAME=order-extractor
MODEL_TIMEOUT_SECONDS=60
```

Jika backend berjalan di Docker sementara llama-server berjalan di host Windows, gunakan `MODEL_BASE_URL=http://host.docker.internal:8080/v1`.

Jika `MODEL_BASE_URL` kosong, backend otomatis memakai extractor mock untuk development.

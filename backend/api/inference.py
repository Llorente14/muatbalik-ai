# ── MuatBalik AI — Inference API ──
# POST /api/inference/extract
# Endpoint for connecting to the Qwen LoRA model (mock for now).

from fastapi import APIRouter
from schemas import InferenceRequest, InferenceResponse, InferenceDetails
from services.extractor import extract_order

router = APIRouter(prefix="/api/inference", tags=["Inference"])


@router.post(
    "/extract",
    response_model=InferenceResponse,
    summary="Extract structured logistics JSON from raw Indonesian text",
    description="""
Accepts raw Indonesian logistics chat text and extracts structured fields.

**Mock mode**: Uses keyword-based parser.  
**Production**: Will call the fine-tuned Qwen LoRA model.

### Example input
```
bos tlg cariin kapal rute bitung k mks buat angkut 1.5 ton cakalang fresh,
butuh chiller 2-4 C, tlg muat lusa sore ya.
```

### Example output
```json
{
  "status": "success",
  "message": "Bitung siap memuat!",
  "details": {
    "origin": "Bitung",
    "destination": "Makassar",
    "cargo_type": "cakalang fresh",
    "weight": 1.5,
    "unit": "ton",
    "temp_requirement": "2_4",
    "delivery_time": "lusa sore"
  }
}
```
    """,
)
def extract_from_text(req: InferenceRequest) -> InferenceResponse:
    result = extract_order(req.raw_text)
    return InferenceResponse(
        status=result["status"],
        message=result["message"],
        details=InferenceDetails(**result["details"]),
    )

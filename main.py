import os
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import List
import re

app = FastAPI(title="Medical Code Lookup API", version="1.0.0")
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Simple ICD-10 code database (common codes) - static data, no external calls
ICD10_CODES = {
    "A00": {"description": "Cholera", "category": "Intestinal infectious diseases"},
    "A01": {"description": "Typhoid and paratyphoid fever", "category": "Intestinal infectious diseases"},
    "A02": {"description": "Zymotic diseases chiefly affecting the digestive system", "category": "Intestinal infectious diseases"},
    "B00": {"description": "Varicella", "category": "Virus diseases"},
    "B01": {"description": "Chickenpox", "category": "Virus diseases"},
    "C00": {"description": "Malignant neoplasm of lip", "category": "Malignant neoplasms of lip, oral cavity and pharynx"},
    "C01": {"description": "Malignant neoplasm of base of tongue", "category": "Malignant neoplasms of lip, oral cavity and pharynx"},
    "C34": {"description": "Malignant neoplasm of bronchus and lung", "category": "Malignant neoplasms of respiratory and intrathoracic organs"},
    "E10": {"description": "Type 1 diabetes mellitus", "category": "Endocrine, nutritional and metabolic diseases"},
    "E11": {"description": "Type 2 diabetes mellitus", "category": "Endocrine, nutritional and metabolic diseases"},
    "E12": {"description": "Gestational diabetes mellitus", "category": "Endocrine, nutritional and metabolic diseases"},
    "I10": {"description": "Essential (primary) hypertension", "category": "Diseases of the circulatory system"},
    "I11": {"description": "Hypertensive heart disease", "category": "Diseases of the circulatory system"},
    "I15": {"description": "Hypertensive disease involving vessels of brain and eye", "category": "Diseases of the circulatory system"},
    "I25": {"description": "Chronic ischemic heart disease", "category": "Diseases of the circulatory system"},
    "J45": {"description": "Unspecified asthma", "category": "Diseases of the respiratory system"},
    "J45.9": {"description": "Unspecified asthma", "category": "Diseases of the respiratory system"},
    "M54": {"description": "Dorsopathologies", "category": "Diseases of the musculoskeletal system and connective tissue"},
    "M54.5": {"description": "Low back pain", "category": "Diseases of the musculoskeletal system and connective tissue"},
    "R53": {"description": "Malaise and fatigue", "category": "Symptoms and signs involving digestive and abdominal symptoms"},
    "R53.2": {"description": "Other fatigue", "category": "Symptoms and signs involving digestive and abdominal symptoms"},
    "Z00": {"description": "General medical examination", "category": "Factors influencing health status"},
    "Z00.0": {"description": "Routine infant and child health check", "category": "Factors influencing health status"},
}

API_KEY = os.environ.get("API_KEY", "demo-key-change-me")

def check_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    if x_api_key and x_api_key == API_KEY:
        return True
    if x_api_key is None:
        # Allow demo key for testing
        return True
    raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/lookup/{code}")
def lookup_code(code: str, x_api_key: str = Header(None, alias="X-API-Key")):
    code_upper = code.upper().strip()
    if code_upper in ICD10_CODES:
        data = ICD10_CODES[code_upper]
        return {
            "code": code_upper,
            "description": data["description"],
            "category": data["category"],
            "valid": True
        }
    raise HTTPException(status_code=404, detail="Code not found")

@app.get("/search")
def search_codes(q: str, limit: int = 10, x_api_key: str = Header(None, alias="X-API-Key")):
    q_lower = q.lower().strip()
    results = []
    for code, data in ICD10_CODES.items():
        if q_lower in code.lower() or q_lower in data["description"].lower():
            results.append({
                "code": code,
                "description": data["description"],
                "category": data["category"],
                "matches": [m for m in [code, data["description"], data["category"]] if q_lower in m.lower()]
            })
            if len(results) >= limit:
                break
    return {"query": q, "results": results, "count": len(results)}

@app.get("/validate/{code}")
def validate_code(code: str, x_api_key: str = Header(None, alias="X-API-Key")):
    pattern = r'^[A-Z]\d{2}(\.\d+)?$'
    code_upper = code.upper().strip()
    in_db = code_upper in ICD10_CODES
    valid_format = bool(re.match(pattern, code_upper))
    return {
        "code": code_upper,
        "valid_format": valid_format,
        "in_database": in_db,
        "valid": valid_format and in_db
    }

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    pass

# Medical Code Lookup API

Lookup and validate ICD-10 medical codes. No database required - static data embedded.

## Endpoints

### `GET /health`
Health check endpoint (no auth required)

### `GET /lookup/{code}`
Lookup an ICD-10 code by exact match.
```bash
curl https://medical-code-lookup.vercel.app/lookup/E11
```
Response:
```json
{
  "code": "E11",
  "description": "Type 2 diabetes mellitus",
  "category": "Endocrine, nutritional and metabolic diseases",
  "valid": true
}
```

### `GET /search?q={query}&limit={limit}`
Search codes by description or partial code match.
```bash
curl "https://medical-code-lookup.vercel.app/search?q=diabetes"
```

### `GET /validate/{code}`
Validate ICD-10 code format and check if in database.
```bash
curl https://medical-code-lookup.vercel.app/validate/E11.9
```
Response:
```json
{
  "code": "E11.9",
  "valid_format": true,
  "in_database": false,
  "valid": false
}
```

## Authentication
All endpoints except `/health` require `X-API-Key` header. Set your own key via `API_KEY` environment variable.

## Postman
[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/BT-Builds/medical-code-lookup/main/postman_collection.json)

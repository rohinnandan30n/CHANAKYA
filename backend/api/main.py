from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.api.recite import router as recite_router

app = FastAPI(title="Svara-Chanda API", version="0.1.0")

# CORS middleware for frontend/extension access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the recite router
app.include_router(recite_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.get("/api/v1/status")
def status():
    return {
        "pipeline": "ready",
        "modules": ["linguistic", "melodic", "audio"]
    }

# Example of structured error handling
@app.get("/api/v1/error-test")
def error_test():
    raise HTTPException(status_code=400, detail="This is a structured error response")

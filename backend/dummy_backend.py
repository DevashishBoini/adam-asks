"""
Mini GitHub Copilot Backend - Dummy Endpoint
Phase 0, Test 2: VS Code Extension Dummy Backend

Run with:
    python dummy_backend.py
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/dummy")
async def dummy():
    return JSONResponse(content={"message": "Hello from backend!"})

import os

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

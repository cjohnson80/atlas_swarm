from fastapi import FastAPI, Response
from typing import Dict

# Initialize FastAPI application
app = FastAPI()

@app.get("/hello", response_model=Dict[str, str])
async def hello_world() -> Response:
    """Returns the standard greeting message."""
    content = {"message": "Hello, World from AtlasSwarm!"}
    
    # SECURITY HARDENING: Applying standard security headers for production readiness
    # X-Content-Type-Options: Prevents MIME sniffing.
    # X-Frame-Options: Prevents clickjacking by disallowing embedding in iframes.
    headers = {"X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY"}
    
    return Response(content=content, media_type="application/json", headers=headers)

# Note: In a production environment, remove --reload flag from uvicorn execution.
# To run this locally:
# 1. pip install -r requirements.txt
# 2. uvicorn app:app --port 8000

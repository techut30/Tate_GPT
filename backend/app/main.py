from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import router as api_router

app = FastAPI(
    title="TateGPT API",
    description="Backend for the TateGPT AI Assistant",
    version="1.0.0"
)

# Optional: Allow CORS for frontend use (Streamlit, React, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

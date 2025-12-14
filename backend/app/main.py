import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import upload, analyze, controls, history, export
from .config import ALLOWED_ORIGINS

app = FastAPI(title="VendorGuard - Procurement & Vendor Risk Analyzer")

# allow configured origins (defaults cover localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(controls.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(export.router, prefix="/api")
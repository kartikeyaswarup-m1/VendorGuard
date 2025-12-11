from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import upload, analyze, controls, history, export

app = FastAPI(title="VendorGuard - Procurement & Vendor Risk Analyzer")

# allow localhost:3000 (your Next dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(analyze.router, prefix="/api")
app.include_router(controls.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(export.router, prefix="/api")
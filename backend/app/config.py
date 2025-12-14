import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/vendorguard/uploads")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
EMBEDDING_PROVIDER = "gemini"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", None)
LLM_PROVIDER = "gemini"
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
GEMINI_LLM_MODEL = os.getenv("GEMINI_LLM_MODEL", "gemini-2.5-flash")


def _default_embedding_dim():
	"""Pick a sane default dimension based on provider/model to avoid Qdrant size mismatches."""
	# Known dimensions: OpenAI text-embedding-3-small = 1536, Gemini gemini-embedding-001 ~= 768
	if EMBEDDING_PROVIDER == "gemini" and GEMINI_EMBEDDING_MODEL == "gemini-embedding-001":
		return 768
	# Fallback to Gemini default if unknown
	return 768


EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", str(_default_embedding_dim())))

# Keep history under the uploads volume so it persists with the existing mount
HISTORY_DIR = os.path.join(UPLOAD_DIR, "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

# Allow overriding CORS origins via env (comma separated)
RAW_ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
ALLOWED_ORIGINS = [o.strip() for o in RAW_ALLOWED_ORIGINS.split(",") if o.strip()]
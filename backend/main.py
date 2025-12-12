# Load environment variables first
import warnings
import sys

# Suppress SyntaxWarnings from moviepy library (known issue in moviepy 1.0.3)
# Must be set before any imports that might trigger moviepy
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", message=".*invalid escape sequence.*")

from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ALLOW_ORIGINS, IS_PROD
from routes import screenshot, generate_code, home, evals, models

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

def _parse_cors_origins(raw: str | None) -> list[str]:
    if not raw:
        return []
    origins = [o.strip() for o in raw.split(",")]
    return [o for o in origins if o]


# Configure CORS settings
allow_origins = ["*"]
allow_credentials = True
if IS_PROD:
    parsed = _parse_cors_origins(CORS_ALLOW_ORIGINS)
    allow_origins = parsed if parsed else []
    # Allowing "*" with credentials is invalid/insecure; default to no credentials.
    allow_credentials = allow_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(generate_code.router)
app.include_router(screenshot.router)
app.include_router(home.router)
app.include_router(evals.router)
app.include_router(models.router)

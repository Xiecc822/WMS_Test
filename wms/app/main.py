from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.router import router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="WMS API", docs_url="/docs", openapi_url="/openapi.json")
app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)


@app.get("/healthz")
def root_health() -> dict[str, str]:
    return {"status": "ok"}

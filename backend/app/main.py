from fastapi import FastAPI

from backend.app.api.chat import router as chat_router
from backend.app.api.documents import router as documents_router
from backend.app.api.health import router as health_router
from backend.app.api.memories import router as memories_router
from backend.app.api.traces import router as traces_router
from backend.app.core.database import init_database


def create_app() -> FastAPI:
    init_database()
    app = FastAPI(title="EMKA Phase 1 MVP", version="0.1.0")
    app.include_router(health_router)
    app.include_router(chat_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")
    app.include_router(memories_router, prefix="/api/v1")
    app.include_router(traces_router, prefix="/api/v1")
    return app


app = create_app()

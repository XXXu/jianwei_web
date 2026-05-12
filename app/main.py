from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.api import router as api_router
from app.routes.pages import router as pages_router


def create_app() -> FastAPI:
    app = FastAPI(title="Jianwei", version="0.1.0")
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    app.include_router(api_router)
    app.include_router(pages_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "jianwei"}

    return app


app = create_app()

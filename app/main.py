from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import Base, engine, SessionLocal
from app.db.init_db import seed_from_csv
from app.routes.clients import router as clients_router
from app.routes.train import router as train_router
from app.core.ml_config import _init_mlflow


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.APP_NAME)

    # Crée les tables
    Base.metadata.create_all(bind=engine)

    _init_mlflow()

    # Seed CSV si nécessaire
    db = SessionLocal()
    try:
        seed_from_csv(db)
    finally:
        db.close()

    app.include_router(clients_router)
    app.include_router(train_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    logger.info("Application démarrée.")
    return app


app = create_app()

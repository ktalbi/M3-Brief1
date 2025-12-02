import pandas as pd
from sqlalchemy.orm import Session
from loguru import logger

from app.models.client import Client
from app.core.config import settings


def seed_from_csv(db: Session):
    count = db.query(Client).count()
    if count > 0:
        logger.info(f"DB déjà initialisée ({count} lignes).")
        return

    logger.info(f"Chargement initial depuis {settings.CSV_PATH} ...")
    df = pd.read_csv(settings.CSV_PATH)

    # renommer la colonne id
    if "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "id"})

    records = df.to_dict(orient="records")

    objs = [Client(**r) for r in records]
    db.add_all(objs)
    db.commit()

    logger.info(f"Seed terminé : {len(objs)} lignes insérées.")

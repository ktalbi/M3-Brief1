from pydantic import BaseModel
from pathlib import Path


class Settings(BaseModel):
    APP_NAME: str = "CSV REST API"
    DB_URL: str = "sqlite:///./app.db"
    CSV_PATH: str = str(Path(__file__).resolve().parents[2] / "fichier_clean.csv")


settings = Settings()

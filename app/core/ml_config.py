import os
from os.path import join as join
from pathlib import Path

import joblib
import pandas as pd
from loguru import logger
import mlflow

# Racine projet (models au même niveau que app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"

# Colonnes d'entrée (features)
INPUT_COLUMNS = [
    "age",
    "sport_licence",
    "niveau_etude",
    "revenu_estime_mois",
    "risque_personnel",
    "loyer_mensuel",
    "anciennete_ans"
]

# Colonne cible
TARGET_COLUMN = "montant_pret"

# Chemins absolus vers models/
MLFLOW_URI_PATH = MODELS_DIR / "mlflow_model_uri.txt"
MLFLOW_MODEL_URI_FILE = str(MLFLOW_URI_PATH)  # si tu en as besoin en str

MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "api_experiment")

# preprocessor.pkl à côté de app/
preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")


def _init_mlflow():
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", f"file:{PROJECT_ROOT / 'mlruns'}")
    logger.info(
        f"MLflow: TRACKING_URI={tracking_uri}, EXPERIMENT={MLFLOW_EXPERIMENT_NAME}"
    )
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def _check_columns_train(df: pd.DataFrame):
    missing_inputs = [c for c in INPUT_COLUMNS if c not in df.columns]
    missing_target = [] if TARGET_COLUMN in df.columns else [TARGET_COLUMN]
    missing = missing_inputs + missing_target
    if missing:
        raise ValueError(
            f"Colonnes manquantes pour l'entraînement : {missing}. "
            f"Attendu: features={INPUT_COLUMNS} + target={TARGET_COLUMN}"
        )


def _save_model_uri(model_uri: str):
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    MLFLOW_URI_PATH.write_text(model_uri)
    logger.info(f"URI MLflow sauvegardée dans {MLFLOW_URI_PATH}")

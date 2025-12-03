from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.orm import Session
import pandas as pd
from tempfile import NamedTemporaryFile

import mlflow
import mlflow.sklearn   

from app.db.session import get_db
from app.models.client import Client
from app.core.ml_config import (
    TARGET_COLUMN,
    preprocessor,
    _check_columns_train,
    _save_model_uri,
)


from models.models import create_nn_model, train_model, model_predict
from modules.evaluate import evaluate_performance

router = APIRouter(tags=["Training"]) 

_model = None
_model_version = "none"


@router.post("/train")
def train_from_db(db: Session = Depends(get_db)):
    """
    Entraîne (ou réentraîne) un modèle à partir de la table clients :
    - lit la DB
    - vérifie la structure
    - entraîne le modèle
    - logue dans MLflow
    - recharge le modèle courant depuis MLflow
    """
    global _model, _model_version

    try:
        # 1) Lire la table clients
        rows = db.query(Client).all()
        if not rows:
            raise HTTPException(status_code=404, detail="Aucun client en base pour entraîner.")

        # 2) Convertir en DataFrame
        data = [
            {k: v for k, v in r.__dict__.items() if not k.startswith("_")}
            for r in rows
        ]
        df = pd.DataFrame(data)
       
        print('******* dataframe colonnes ******')
        cols = df.columns.tolist()
        print(cols)
        df.drop(columns=["id"], inplace=True)


        # 3) Vérifier colonnes (features + target)
        _check_columns_train(df)

        # 4) Prétraitement + split
        y = df[TARGET_COLUMN].values
        X_raw = df.drop(columns=[TARGET_COLUMN])
        # preprocessing deja realisé sur les données (module 2)
        X = X_raw

        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        epochs = 60
        batch_size = 32

        # 5) MLflow run
        with mlflow.start_run() as run:
            run_id = run.info.run_id
            logger.info(f"Début du run MLflow (DB TRAIN) : {run_id}")

            mlflow.log_param("epochs", epochs)
            mlflow.log_param("batch_size", batch_size)
            mlflow.log_param("source", "api/train_from_db")
            mlflow.log_param("n_rows", len(df))

            # 6) Entraîner
            model = create_nn_model(X_train.shape[1])
            model, _hist = train_model(
                model,
                X_train,
                y_train,
                X_val=X_test,
                y_val=y_test,
                epochs=epochs,
                batch_size=batch_size,
            )

            # 7) Évaluer + log metrics
            preds = model_predict(model, X_test)
            perf = evaluate_performance(y_test, preds)

            mlflow.log_metric("MAE", perf["MAE"])
            mlflow.log_metric("MSE", perf["MSE"])
            mlflow.log_metric("R2", perf["R²"])

            # 8) Log dataset DB en artifact
            with NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                df.to_csv(tmp.name, index=False)
                tmp.flush()
                mlflow.log_artifact(tmp.name, artifact_path="training_data_db")

            # 9) Log du modèle
            mlflow.sklearn.log_model(model, artifact_path="mlflow_model")
            model_uri = f"runs:/{run_id}/mlflow_model"

        # 10) Recharger en mémoire
        logger.info(f"Fin du run MLflow {run_id}, chargement du modèle : {model_uri}")
        _model = mlflow.sklearn.load_model(model_uri)
        _model_version = run_id
        _save_model_uri(model_uri)

        return {
            "message": "Modèle entraîné depuis la DB et loggé dans MLflow.",
            "metrics": perf,
            "model_version": _model_version,
            "mlflow_model_uri": model_uri,
            "mlflow_run_id": run_id,
            "n_rows": len(df),
        }

    except ValueError as ve:
        logger.warning(f"Erreur de validation DB : {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur pendant l'entraînement DB avec MLflow.")
        raise HTTPException(status_code=500, detail=str(e))

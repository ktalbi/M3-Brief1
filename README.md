# M3 -Brief 1 : API Clients + Réentraînement ML + MLflow (FastAPI / SQLite)

## Objectif du projet

Ce projet met en place une API REST FastAPI permettant de :

- **Gérer une base de clients** stockée en **SQLite** via **SQLAlchemy**
  - liste, détail
  - ajout
  - suppression
  - endpoints utilitaires (`/count`, `/latest`)
- **Réentraîner un modèle ML** directement à partir du contenu de la table `clients`
  - la **target est `montant_pret`**
  - les features correspondent à `INPUT_COLUMNS`
- **Tracer les entraînements et modèles dans MLflow**
  - paramètres, métriques, dataset en artefact
  - modèle loggué en artefact MLflow
  - URI du dernier modèle persistée dans `models/mlflow_model_uri.txt`
- **Journaliser l’API avec Loguru**
- Fournir une documentation Swagger automatique (FastAPI)

L’approche couvre un cycle ML simple :
**DB  → entraînement → suivi MLflow → modèle courant .

---

## 1. Architecture du projet

```
project_root/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── ml_config.py
│   ├── db/
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   └── client.py
│   ├── schemas/
│   │   └── client.py
│   ├── routes/
│   │   ├── clients.py
│   │   └── train.py
│   └── services/
│       └── training_service.py
├── models/
│   ├── preprocessor.pkl
│   └── mlflow_model_uri.txt   (créé/maj automatiquement)
├── logs/
├── mlruns/                    (créé par MLflow)
├── fichier_clean.csv                (seed initial)
├── requirements.txt
└── README.md
```


---

## 2. Fonctionnalités principales

### 2.1 API Clients (CRUD minimal)

Endpoints :

- **GET `/clients/`**
  - liste tous les clients
- **GET `/clients/{client_id}`**
  - récupère un client par id
- **POST `/clients/`**
  - ajoute un client (id auto-incrémenté)
- **DELETE `/clients/{client_id}`**
  - supprime un client
- **GET `/clients/count`**
  - renvoie le nombre total de clients
- **GET `/clients/latest`**
  - renvoie le dernier client (id max)

### 2.2 Entraînement depuis la DB

Endpoint :

- **POST `/train`**
  - lit la table `clients`
  - vérifie que les colonnes attendues sont présentes (`INPUT_COLUMNS` + `montant_pret`)
  - split train/test
  - entraîne le modèle (TensorFlow/Keras via `create_nn_model`)
  - log dans MLflow :
    - params : epochs, batch_size, n_rows, source
    - metrics : MAE, MSE, R²
    - artefacts : dataset DB, modèle
  - met à jour `models/mlflow_model_uri.txt`
  - recharge le dernier modèle en mémoire

### 2.3 Suivi MLflow

Chaque run loggue :

| Métrique | Description |
|---------|-------------|
| **MAE** | Mean Absolute Error |
| **MSE** | Mean Squared Error |
| **R²** | Variance expliquée |

Le dernier modèle sera accessible via l’URI stockée dans :

```
models/mlflow_model_uri.txt
```

---

## 3. Lancement local (hors Docker)

### 3.1 Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# ou
.venv\Scripts\Activate.ps1  # Windows PowerShell
```

### 3.2 Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3.3 Lancer l’API

Depuis la racine :

```bash
uvicorn app.main:app --reload
```

Swagger :

- http://127.0.0.1:8000/docs

---

## 4. Seed initial depuis CSV

Au démarrage, si la table est vide :

- `fichier_clean.csv` est chargé automatiquement
- les ids sont générés par SQLite

Pour repartir de zéro :

```bash
rm app.db
uvicorn app.main:app --reload
```

---

## 5. Entraîner depuis la base

```bash
curl -i -X POST http://127.0.0.1:8000/train
```

Retour :

```json
{
  "message": "...",
  "metrics": {"MAE":..., "MSE":..., "R²":...},
  "model_version": "...",
  "mlflow_model_uri": "...",
  "mlflow_run_id": "...",
  "n_rows": 1234
}
```

---

## 6. Lancer MLflow UI

Depuis la racine (où `mlruns/` est créé) :

```bash
mlflow ui --backend-store-uri ./mlruns
```

Puis :

- http://127.0.0.1:5000

---

## 7. Conclusion

Ce projet fournit :

- une API REST proprement structurée
- une base SQLite manipulée via SQLAlchemy
- un pipeline de réentraînement en DB
- un suivi MLflow reproductible
- des logs robustes via Loguru



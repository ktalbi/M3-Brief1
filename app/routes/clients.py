from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc,func
from loguru import logger

from app.db.session import get_db
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientRead

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/count")
def count_clients(db: Session = Depends(get_db)):
    total = db.query(func.count(Client.id)).scalar()
    return {"count": total}

@router.get("/", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db)):
    rows = db.query(Client).all()
    logger.info(f"GET /clients -> {len(rows)} lignes")
    return rows

@router.get("/latest", response_model=ClientRead)
def get_latest_clients(db: Session = Depends(get_db)):
    row = db.query(Client).order_by(desc(Client.id)).first()
    if not row:
        raise HTTPException(status_code=404, detail="No clients in database")
    return row

@router.get("/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    row = db.query(Client).filter(Client.id == client_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="client not found")
    logger.info(f"GET /clients/{client_id}")
    return row



@router.post("/", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    obj = Client(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)

    logger.info(f"POST /clients -> id={obj.id}")
    return obj



@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    row = db.query(Client).filter(Client.id == client_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="client not found")

    db.delete(row)
    db.commit()

    logger.info(f"DELETE /clients/{client_id}")
    return None

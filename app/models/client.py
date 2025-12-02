from sqlalchemy import Column, Integer, Float
from app.db.session import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    age = Column(Float, nullable=False)
    sport_licence = Column(Integer, nullable=False)
    niveau_etude = Column(Integer, nullable=False)
    revenu_estime_mois = Column(Float, nullable=False)
    risque_personnel = Column(Float, nullable=False)
    loyer_mensuel = Column(Float, nullable=False)
    montant_pret = Column(Float, nullable=False)
    anciennete_ans = Column(Float, nullable=False)

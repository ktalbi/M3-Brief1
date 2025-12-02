from pydantic import BaseModel, ConfigDict


class ClientBase(BaseModel):
    age: float
    sport_licence: int
    niveau_etude: int
    revenu_estime_mois: float
    risque_personnel: float
    loyer_mensuel: float
    montant_pret: float
    anciennete_ans: float


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

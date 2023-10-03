from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    
    with db.engine.begin() as connection:
        sql = "SELECT num_red_potions, num_red_ml, gold from global_inventory"
        results = connection.execute(sqlalchemy.text(sql))
        first_row = results.first()
    
    if not first_row.num_red_potions or not first_row.num_red_ml or not first_row.gold:
            return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 0}


    return {"number_of_potions": first_row.num_red_potions, "ml_in_barrels": first_row.num_red_ml, "gold": first_row.gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"

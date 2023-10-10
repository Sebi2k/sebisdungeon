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
        sql = "SELECT num_red_potions, num_red_ml, gold, num_blue_ml, num_blue_potions, num_green_ml, num_green_potions from global_inventory"
        results = connection.execute(sqlalchemy.text(sql))
        first_row = results.first()
        potions = first_row.num_red_potions + first_row.num_green_potions + first_row.num_blue_potions
        ml = first_row.num_red_ml + first_row.num_green_ml + first_row.num_blue_ml

    return {"number_of_potions": potions, "ml_in_barrels": ml, "gold": first_row.gold}

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
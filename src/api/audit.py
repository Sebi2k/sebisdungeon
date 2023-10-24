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
        sql = "SELECT type, SUM(delta) AS sum FROM global_ledger GROUP BY type"
        results = connection.execute(sqlalchemy.text(sql))
        r = g = b = d = gold = None

        for type, sum in results:
            print(type,sum)
            if type == 'num_red_ml':
                r = sum
            elif type == 'num_green_ml':
                g = sum
            elif type == 'num_blue_ml':
                b = sum
            elif type == 'num_dark_ml':
                d = sum
            elif type == 'gold':
                gold = sum
        
        ml = r+g+b+d

        result = connection.execute(sqlalchemy.text("SELECT SUM(delta) AS potions FROM catalog_ledger"))

    return {"number_of_potions": result.first().potions, "ml_in_barrels": ml, "gold": gold}

    

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

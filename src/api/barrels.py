from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError


router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    with db.engine.begin() as connection:
        for barrel in barrels_delivered:
            type = ''
            if barrel.potion_type == [1,0,0,0]:
                type = 'num_red_ml'
            elif barrel.potion_type == [0,1,0,0]:
                type = 'num_green_ml'
            elif barrel.potion_type == [0,0,1,0]:
                type = 'num_blue_ml'
            elif barrel.potion_type == [0,0,0,1]:
                type = 'num_dark_ml'
            
            gold_delta = -(barrel.price * barrel.quantity)
            ml_delta = barrel.ml_per_barrel * barrel.quantity

            # make transaction
            result = connection.execute(sqlalchemy.text("INSERT INTO transactions (description) VALUES (:description) RETURNING id"),
                     [{"description": f"I bought {barrel.quantity} {barrel.sku} for {barrel.price} gold for and got {barrel.ml_per_barrel} ml {type}"}])
            t_id = result.first().id

            # append to global ledger
            connection.execute(
                sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta)VALUES (:transaction_id, :type, :delta)"),
                    [{"transaction_id": t_id, "type": type, "delta": ml_delta},
                    {"transaction_id": t_id, "type": "gold", "delta": gold_delta}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    plan = []

    with db.engine.begin() as connection:

        # buy green and blue barrels too
        sql = "SELECT type, SUM(delta) AS sum FROM global_ledger GROUP BY type"
        result = connection.execute(sqlalchemy.text(sql))
        for type, sum in result:
            if type == 'gold':
                gold = sum
        
        for barrel in wholesale_catalog:
            sku = barrel.sku
            if sku == "MINI_GREEN_BARREL" or sku == "MINI_BLUE_BARREL" or sku == "MINI_RED_BARREL":
                if gold >= barrel.price and barrel.quantity >= 1:
                    plan.append({"sku": sku, "quantity": 1})

    return plan
    

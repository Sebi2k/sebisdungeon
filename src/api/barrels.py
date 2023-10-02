from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

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
        #query for gold and ml
        sql = "SELECT gold, num_red_ml from global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        
        # for every barrel delivered add ml and sub gold
        for barrel in barrels_delivered:
            s = "UPDATE global_inventory SET gold = gold - " + str(first_row.gold - barrel.price)
            connection.execute(sqlalchemy.text(s))
            q = "UPDATE global_inventory SET num_red_ml = num_red_ml + " + str(first_row.num_red_ml + barrel.ml_per_barrel)
            connection.execute(sqlalchemy.text(q))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:

        # buy SMALL_RED_BARREL if less than 10 potions and we have $
        sql = "SELECT gold, num_red_potions FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()

        # get barrel
        smallred = None

        for curBarrel in wholesale_catalog:
            if curBarrel.sku == "SMALL_RED_BARREL":
                smallred = curBarrel

        # dont buy if more than 10 or insufficient funds
        if first_row.num_red_potions >= 10 or first_row.gold < smallred.price:
            return []

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

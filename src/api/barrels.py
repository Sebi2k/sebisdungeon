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
        sql = "SELECT gold, num_red_ml, num_green_ml, num_blue_ml from global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        
        # for every barrel delivered add ml and sub gold
        for barrel in barrels_delivered:
            if (barrel.potion_type == [1, 0, 0, 0]):
                s = "UPDATE global_inventory SET gold = gold - " + str(first_row.gold - barrel.price)
                connection.execute(sqlalchemy.text(s))
                q = "UPDATE global_inventory SET num_red_ml = num_red_ml + " + str(first_row.num_red_ml + barrel.ml_per_barrel)
                connection.execute(sqlalchemy.text(q))
            
            elif (barrel.potion_type == [0, 1, 0, 0]):
                l = f"UPDATE global_inventory SET gold = gold - {str(first_row.gold - barrel.price)}"
                connection.execute(sqlalchemy.text(l))
                b = "UPDATE global_inventory SET num_green_ml = num_green_ml + " + str(first_row.num_green_ml + barrel.ml_per_barrel)
                connection.execute(sqlalchemy.text(b))

            elif (barrel.potion_type == [0, 0, 1, 0]):
                a = "UPDATE global_inventory SET gold = gold - " + str(first_row.gold - barrel.price)
                connection.execute(sqlalchemy.text(a))
                d = "UPDATE global_inventory SET num_blue_ml = num_blue_ml + " + str(first_row.num_blue_ml + barrel.ml_per_barrel)
                connection.execute(sqlalchemy.text(d))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    plan = []

    with db.engine.begin() as connection:

        # buy green and blue barrels too
        sql = "SELECT gold, num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()

        if (first_row.num_green_potions < 3):
            plan.append({
                "sku": "SMALL_GREEN_BARREL",
                "quantity": 1,
            })
        if (first_row.num_blue_potions < 3):
            plan.append({
                "sku": "SMALL_BLUE_BARREL",
                "quantity": 1,
            })
        if (first_row.num_red_potions < 3):
            plan.append({
                "sku": "SMALL_RED_BARREL",
                "quantity": 1,
            })

    return plan
    

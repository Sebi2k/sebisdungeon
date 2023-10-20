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

    gold = red = green = blue = dark = 0

    for barrel in barrels_delivered:
        if barrel.potion_type == [1,0,0,0]:
            red += (barrel.ml_per_barrel * barrel.quantity)
            gold += (barrel.price* barrel.quantity)
        elif barrel.potion_type == [0,1,0,0]:
            green += (barrel.ml_per_barrel * barrel.quantity)
            gold += (barrel.price* barrel.quantity)
        elif barrel.potion_type == [0,0,1,0]:
            blue += (barrel.ml_per_barrel * barrel.quantity)
            gold += (barrel.price* barrel.quantity)
        elif barrel.potion_type == [0,0,0,1]:
            dark += (barrel.ml_per_barrel * barrel.quantity)
            gold += (barrel.price* barrel.quantity)

    with db.engine.begin() as connection:
        
        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET gold = gold - :gold,
        num_red_ml = num_red_ml + :num_red_ml,
        num_green_ml = num_green_ml + :num_green_ml,
        num_blue_ml = num_blue_ml + :num_blue_ml,
        num_dark_ml = num_dark_ml + :num_dark_ml"""), [{"gold": gold, "num_red_ml": red, "num_green_ml": green, "num_blue_ml": blue, "num_dark_ml": dark}])

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    plan = []

    with db.engine.begin() as connection:

        # buy green and blue barrels too
        sql = "SELECT gold FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        row = result.first()
        gold = row.gold
        for barrel in wholesale_catalog:
            sku = barrel.sku
            if sku == "SMALL_GREEN_BARREL" or sku == "SMALL_BLUE_BARREL" or sku == "SMALL_RED_BARREL":
                if gold >= barrel.price:
                    plan.append({"sku": sku, "amount": 1})

    return plan
    

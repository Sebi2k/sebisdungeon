from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)

    with db.engine.begin() as connection:
        for potions in potions_delivered:
            # incrementing numredpotions by quantity of potions_delivered
            sql = "UPDATE global_inventory SET num_red_potions = num_red_potions + " + str(potions.quantity)
            connection.execute(sqlalchemy.text(sql))
            # decrementing numredml by quantity of potions_delivered times 100 (100 ml in potion)
            sql2 = "UPDATE global_inventory SET num_red_ml = num_red_ml - " + str(potions.quantity * 100)
            connection.execute(sqlalchemy.text(sql2))

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
     # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        sql = "SELECT num_red_ml FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()

    # find largest amount of potions that can be created as a whole number
    numPotions = first_row.num_red_ml // 100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": numPotions,
            }
        ]

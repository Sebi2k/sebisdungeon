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
        for potion in potions_delivered:
            quantity = potion.quantity
            r, g, b, d = potion.potion_type
            connection.execute(sqlalchemy.text(
                    """
                    UPDATE catalog 
                    SET quantity = quantity + :quantity
                    WHERE 
                    num_red_ml = :num_red_ml AND
                    num_green_ml = :num_green_ml AND
                    num_blue_ml = :num_blue_ml AND
                    num_dark_ml = :num_dark_ml
                    """
                ), [{"quantity": quantity, "num_red_ml": r, "num_green_ml": g, "num_blue_ml": b, "num_dark_ml": d}])
            
            connection.execute(sqlalchemy.text(
                    """
                    UPDATE global_inventory 
                    SET num_red_ml = num_red_ml - :num_red_ml, 
                    num_green_ml = num_green_ml - :num_green_ml, 
                    num_blue_ml = num_blue_ml - :num_blue_ml, 
                    num_dark_ml = num_dark_ml - :num_dark_ml
                    """
                ), [{"num_red_ml": r*quantity, "num_green_ml": g*quantity, "num_blue_ml": b*quantity, "num_dark_ml": d*quantity}])


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
        sql = "SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()
        # find largest amount of potions that can be created as a whole number
        numR = first_row.num_red_ml // 100
        numG = first_row.num_green_ml // 100
        numB = first_row.num_blue_ml // 100

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": numR,
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": numG,
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": numB,
            }
        ]

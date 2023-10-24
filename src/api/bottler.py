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

            print(r,g,b,d,quantity)

            result = connection.execute(sqlalchemy.text("SELECT id, sku, name FROM catalog WHERE num_red_ml = :red_ml AND num_green_ml = :green_ml AND num_blue_ml = :blue_ml AND num_dark_ml = :dark_ml "),
                     [{"red_ml": r, "green_ml": g, "blue_ml": b, "dark_ml": d}])
            id, sku, name = result.first()
            print(id, sku, name)

            result = connection.execute(sqlalchemy.text("INSERT INTO transactions (description) VALUES (:description) RETURNING id"),
                     [{"description": f"Bottled [{quantity}] {name} with sku: {sku} of type {r,g,b,d}"}])
            t_id = result.first().id
            print(t_id)

            connection.execute(sqlalchemy.text("INSERT INTO catalog_ledger (transaction_id, catalog_id, delta) VALUES (:transaction_id, :catalog_id, :delta)"),
                 [{"transaction_id": t_id, "catalog_id": id, "delta": quantity}])

            if r > 0:
                connection.execute(sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta) VALUES (:transaction_id, :type, :delta)"),
                    {"transaction_id": t_id, "type": "num_red_ml", "delta": -(r * quantity)})
            if g > 0:
                connection.execute(sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta) VALUES (:transaction_id, :type, :delta)"),
                    {"transaction_id": t_id, "type": "num_green_ml", "delta": -(g * quantity)})
            if b > 0:
                connection.execute(sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta) VALUES (:transaction_id, :type, :delta)"),
                    {"transaction_id": t_id, "type": "num_blue_ml", "delta": -(b * quantity)})
            if d > 0:
                connection.execute(sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta) VALUES (:transaction_id, :type, :delta)"),
                    {"transaction_id": t_id, "type": "num_dark_ml", "delta": -(d * quantity)})

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
    plan = []

    with db.engine.begin() as connection:
        sql = "SELECT type, SUM(delta) AS sum FROM global_ledger GROUP BY type"
        result = connection.execute(sqlalchemy.text(sql))
        r = g = b = d = None

        for type, sum in result:
            print(type,sum)
            if type == 'num_red_ml':
                r = sum
            elif type == 'num_green_ml':
                g = sum
            elif type == 'num_blue_ml':
                b = sum
            elif type == 'num_dark_ml':
                d = sum

        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml, num_dark_ml FROM catalog"))
        
        for red_ml, green_ml, blue_ml, dark_ml in result:
            print(f'red:{red_ml} green:{green_ml} blue: {blue_ml} dark: {dark_ml}')

            if red_ml <= r and green_ml <= g and blue_ml <= b and dark_ml <= d:
                r -= red_ml
                g -= green_ml
                b -= blue_ml
                d -= dark_ml
                plan.append({"potion_type": [red_ml, green_ml, blue_ml, dark_ml], "quantity": 1,})

    return plan
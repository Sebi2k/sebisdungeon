from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    try:
        with db.engine.begin() as connection:
            # clear everything
            connection.execute(sqlalchemy.text("TRUNCATE transactions CASCADE"))
            connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))
            
            result = connection.execute(sqlalchemy.text("INSERT INTO transactions (description)VALUES ('Reset the game state')RETURNING id"))
            t_id = result.first().id

        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO global_ledger (transaction_id, type, delta)
                    VALUES (:transaction_id, :type, :delta)"""
                ), [{"transaction_id": t_id, "type": "gold", "delta": 100},{"transaction_id": t_id, "type": "num_red_ml", "delta": 0},{"transaction_id": t_id, "type": "num_green_ml", "delta": 0},{"transaction_id": t_id, "type": "num_blue_ml", "delta": 0},{"transaction_id": t_id, "type": "num_dark_ml", "delta": 0}])
            
            connection.execute(
                sqlalchemy.text("INSERT INTO catalog_ledger (transaction_id, catalog_id, delta) VALUES (:transaction_id, Null, 0)"  
                ), [{"transaction_id": t_id}])
            
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "SebisDungeon",
        "shop_owner": "Sebastian Thau",
    }


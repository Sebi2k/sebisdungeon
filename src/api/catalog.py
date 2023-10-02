from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    with db.engine.begin() as connection:
        sql = "SELECT num_red_potions from global_inventory"
        result = connection.execute(sqlalchemy.text(sql))  
        first_row = result.first()

    if first_row.num_red_potions > 0:
        return [
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
            ]
    else:
        return []
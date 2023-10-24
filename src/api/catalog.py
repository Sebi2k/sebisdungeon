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
    catalog = []

    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                    """SELECT cat.sku, cat.name, l_c.quantity, cat.price, ARRAY[cat.num_red_ml, cat.num_green_ml, cat.num_blue_ml, cat.num_dark_ml] AS potion_type
                    FROM catalog AS cat
                    JOIN (SELECT catalog_id, SUM(delta) AS quantity
                          FROM catalog_ledger
                          GROUP BY catalog_id) 
                          AS l_c ON cat.id = l_c.catalog_id
                    WHERE l_c.quantity > 0
                    ORDER BY l_c.quantity DESC LIMIT 5"""))
            
            for sku, name, quantity, price, potion_type in result:
                potion = {
                    "sku": sku,
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "potion_type": potion_type
                }
                catalog.append(potion)

    return catalog
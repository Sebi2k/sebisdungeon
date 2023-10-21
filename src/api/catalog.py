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
        # query catalog for items in stock
        result = connection.execute(sqlalchemy.text("""SELECT sku, name, quantity, price, ARRAY[num_red_ml, num_green_ml, num_blue_ml, num_dark_ml] AS potion_type
                FROM catalog
                WHERE quantity > 0
                ORDER BY quantity DESC
                LIMIT 6"""))
        
        for sku, name, quantity, price, potion_type in result:
            item = {"sku": sku,
                    "name": name,
                    "quantity": quantity,
                    "price": price,
                    "potion_type": potion_type}
            catalog.append(item)

    return catalog
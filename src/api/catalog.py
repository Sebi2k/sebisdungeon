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
        sql = "SELECT num_red_potions, num_green_potions, num_blue_potions from global_inventory"
        result = connection.execute(sqlalchemy.text(sql))  
        first_row = result.first()

    if (first_row.num_red_potions <= 0 and first_row.num_green_potions <= 0 and first_row.num_blue_potions <= 0):
        return []

    if (first_row.num_red_potions > 0):
        catalog.append([
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                }
            ])
        
    if (first_row.num_green_potions > 0):
        catalog.append([
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                }
            ])
    
    if (first_row.num_blue_potions > 0):
        catalog.append([
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": 1,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                }
            ])
    
    return catalog
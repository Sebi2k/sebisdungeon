from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

carts = {}
id = 0

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    global id
    global carts

    id += 1
    carts[id] = {}

    return {"cart_id": id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    string = ''
    s = ''
    for i, k in carts[cart_id].items():
        string = string + str(i)
        s = s + str(k)
    return {f"cart:   sku: {string}   quantity: {s}"}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    global carts
    carts[id][item_sku] = cart_item.quantity
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    if cart_id not in carts:
        return {"total_potions_bought": 0, "total_gold_paid": 0}
    colorDict = {"RED_POTION_0":"num_red_", "GREEN_POTION_0":"num_green_", "BLUE_POTION_0":"num_blue_"}
    
    sql_updates = [] 
    
    allgold = 0
    allpotions = 0

    with db.engine.begin() as connection:
        for sku, quantity in carts[cart_id].items():
            sql_query = f"SELECT {colorDict[sku]}potions FROM global_inventory"
            result = connection.execute(sqlalchemy.text(sql_query))
            first_row = result.first()

            if not getattr(first_row, f'{colorDict[sku]}potions'):
                return {"total_potions_bought": 0, "total_gold_paid": 0}
            
            sql_update = f"UPDATE global_inventory SET {colorDict[sku]}potions = {colorDict[sku]}potions - {quantity}, gold = gold + {quantity * 50}"
            sql_updates.append(sql_update)

            allgold += quantity * 50
            allpotions += quantity

        for sql_update in sql_updates:
            connection.execute(sqlalchemy.text(sql_update))
    
    carts[cart_id] = {}

    return {"total_potions_bought": allpotions, "total_gold_paid": allgold}
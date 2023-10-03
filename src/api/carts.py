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

    return {}


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
    # not buying potions if we dont have the inventory
    with db.engine.begin() as connection:
        sql = "SELECT num_red_potions FROM global_inventory"
        result = connection.execute(sqlalchemy.text(sql))
        first_row = result.first()

        if not first_row.num_red_potions:
            return {"total_potions_bought": 0, "total_gold_paid": 0}


    # buying the potion
    with db.engine.begin() as connection:

        sql = "UPDATE global_inventory SET gold = gold + 50"
        connection.execute(sqlalchemy.text(sql))

        sql2 = "UPDATE global_inventory SET num_red_potions = num_red_potions - 1"
        connection.execute(sqlalchemy.text(sql2))

    return {"total_potions_bought": 1, "total_gold_paid": 50}

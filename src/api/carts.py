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


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("INSERT INTO carts (customer_name) VALUES (:name) RETURNING id"), [{"name": new_cart.customer}])
        id = result.first().id
    
    return {"cart_id": id}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM carts WHERE id = :id"), [{"id": cart_id}])

    return {"Cart's Customer Name: " + result.first().customer_name}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("SELECT id FROM catalog WHERE catalog.sku = :item_sku"), 
        [{"item_sku": item_sku}])

        catalog_id = results.first().id

        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, catalog_id, quantity) VALUES (:cart_id, :catalog_id, :quantity)"), 
        [{"cart_id": cart_id,  "catalog_id": catalog_id, "quantity": cart_item.quantity}])
    

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    all_potions = 0
    all_gold = 0
    with db.engine.begin() as connection:
        
        result = connection.execute(sqlalchemy.text(
                """SELECT catalog.id, cart_items.quantity, catalog.price, catalog.sku, carts.customer_name
                FROM cart_items
                    JOIN catalog ON cart_items.catalog_id = catalog.id
                    JOIN carts ON cart_items.cart_id = carts.id
                WHERE cart_items.cart_id = :cart_id """),
                [{"cart_id": cart_id}])

        for catalog_id, quantity, price, sku, customer_name in result:
            all_gold += price * quantity
            all_potions += quantity

            result = connection.execute(sqlalchemy.text("INSERT INTO transactions (description, cart_id) VALUES (:description, :cart_id) RETURNING id"), 
                                        [{"description": f"Sold {quantity} {sku} to {customer_name} for {price} gold each", "cart_id": cart_id}])
            
            transaction_id = result.scalar_one()

            connection.execute(sqlalchemy.text("INSERT INTO catalog_ledger (transaction_id, catalog_id, delta)VALUES (:transaction_id, :catalog_id, :delta) "),
                                [{"transaction_id": transaction_id, "catalog_id": catalog_id, "delta": -quantity}])
            
            connection.execute(sqlalchemy.text("INSERT INTO global_ledger (transaction_id, type, delta)VALUES (:transaction_id, :type, :delta)"),
                    [{"transaction_id": transaction_id, "type": "gold", "delta": price*quantity}])


    return {"total_potions_bought": all_potions, "total_gold_paid": all_gold}
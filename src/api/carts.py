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
    total_gold = 0
    total_potions = 0

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""
                SELECT cart_items.quantity, catalog.quantity, catalog.price
                FROM cart_items
                JOIN catalog ON cart_items.catalog_id = catalog.id
                WHERE cart_items.cart_id = :cart_id"""), [{"cart_id": cart_id}])

        for quantity, quant, price in result:
            if quant < quantity:
                return {"total_potions_bought": 0, "total_gold_paid": 0}
            
            total_gold += price * quantity
            total_potions += quantity

        
        connection.execute(sqlalchemy.text("""
                UPDATE catalog
                SET quantity = catalog.quantity - cart_items.quantity
                FROM cart_items
                WHERE catalog.id = cart_items.catalog_id AND cart_items.cart_id = :cart_id"""), [{"cart_id": cart_id}])

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold + :total_gold"), [{"total_gold": total_gold}])

    return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}
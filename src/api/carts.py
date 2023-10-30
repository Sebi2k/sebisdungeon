from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
<<<<<<< HEAD
import sqlalchemy
from src import database as db
=======
from enum import Enum
>>>>>>> upstream/main

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


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
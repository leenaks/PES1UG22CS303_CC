import json
from typing import List, Optional
import products
from cart import dao
from products import Product


class Cart:
    def _init_(self, id: int, username: str, contents: List[Product], cost: float):
        self.id = id
        self.username = username
        self.contents = contents
        self.cost = cost

    @classmethod
    def load(cls, data: dict) -> "Cart":
        return cls(
            id=data['id'],
            username=data['username'],
            contents=data['contents'],
            cost=data['cost']
        )


def get_cart_items(username: str) -> List[Product]:
    """
    Retrieve cart items for a given username.

    Args:
        username (str): The username whose cart is to be retrieved.

    Returns:
        List[Product]: List of Product objects in the user's cart.
    """
    cart_details = dao.get_cart(username)
    if not cart_details:
        return []

    items = []
    for cart_detail in cart_details:
        try:
            # Parse contents safely using JSON
            contents = json.loads(cart_detail['contents'])
            for product_id in contents:
                product = products.get_product(product_id)
                if product:
                    items.append(product)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing cart contents: {e}")
    return items


def add_product_to_cart(username: str, product_id: int):
    """
    Add a product to the cart.

    Args:
        username (str): The username to add the product to.
        product_id (int): The ID of the product to add.
    """
    dao.add_to_cart(username, product_id)


def remove_product_from_cart(username: str, product_id: int):
    """
    Remove a product from the cart.

    Args:
        username (str): The username to remove the product from.
        product_id (int): The ID of the product to remove.
    """
    dao.remove_from_cart(username, product_id)


def clear_cart(username: str):
    """
    Clear all items from the user's cart.

    Args:
        username (str): The username whose cart is to be cleared.
    """
    dao.delete_cart(username)
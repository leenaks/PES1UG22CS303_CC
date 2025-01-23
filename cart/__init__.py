import json
import os
import sqlite3
from typing import Optional, List


def connect(path: str) -> sqlite3.Connection:
    """
    Connect to the SQLite database. Create tables if the database doesn't exist.

    Args:
        path (str): Path to the SQLite database file.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    database_exists = os.path.exists(path)
    conn = sqlite3.connect(path)
    if not database_exists:
        create_tables(conn)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables(conn: sqlite3.Connection):
    """
    Create necessary tables in the database.

    Args:
        conn (sqlite3.Connection): Database connection object.
    """
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            contents TEXT DEFAULT '[]',
            cost REAL DEFAULT 0
        )
    ''')
    conn.commit()


def fetch_cart_contents(conn: sqlite3.Connection, username: str) -> Optional[List[int]]:
    """
    Fetch the contents of a user's cart.

    Args:
        conn (sqlite3.Connection): Database connection object.
        username (str): Username whose cart is to be fetched.

    Returns:
        Optional[List[int]]: List of product IDs in the cart, or None if the cart does not exist.
    """
    cursor = conn.execute('SELECT contents FROM carts WHERE username = ?', (username,))
    result = cursor.fetchone()
    return json.loads(result['contents']) if result and result['contents'] else []


def get_cart(username: str) -> List[dict]:
    """
    Retrieve the cart details for a given username.

    Args:
        username (str): Username whose cart is to be retrieved.

    Returns:
        List[dict]: List of cart items.
    """
    with connect('carts.db') as conn:
        cursor = conn.execute('SELECT * FROM carts WHERE username = ?', (username,))
        return [dict(row) for row in cursor.fetchall()]


def add_to_cart(username: str, product_id: int):
    """
    Add a product to a user's cart.

    Args:
        username (str): Username to add the product to.
        product_id (int): Product ID to add.
    """
    with connect('carts.db') as conn:
        contents = fetch_cart_contents(conn, username)
        contents.append(product_id)
        conn.execute('''
            INSERT INTO carts (username, contents, cost)
            VALUES (?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
            contents = ?, cost = cost
        ''', (username, json.dumps(contents), 0, json.dumps(contents)))
        conn.commit()


def remove_from_cart(username: str, product_id: int):
    """
    Remove a product from a user's cart.

    Args:
        username (str): Username whose cart is to be updated.
        product_id (int): Product ID to remove.
    """
    with connect('carts.db') as conn:
        contents = fetch_cart_contents(conn, username)
        if product_id in contents:
            contents.remove(product_id)
            conn.execute('''
                INSERT INTO carts (username, contents, cost)
                VALUES (?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                contents = ?, cost = cost
            ''', (username, json.dumps(contents), 0, json.dumps(contents)))
            conn.commit()


def delete_cart(username: str):
    """
    Delete a user's cart.

    Args:
        username (str): Username whose cart is to be deleted.
    """
    with connect('carts.db') as conn:
        conn.execute('DELETE FROM carts WHERE username = ?', (username,))
        conn.commit()
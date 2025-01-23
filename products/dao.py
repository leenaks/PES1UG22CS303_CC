import json
import os.path
import sqlite3

def connect(path):
    """Connect to the SQLite database. Create tables if they don't exist."""
    exists = os.path.exists(path)
    __conn = sqlite3.connect(path)
    if not exists:
        create_tables(__conn)
    __conn.row_factory = sqlite3.Row
    return __conn

def create_tables(conn):
    """Create the carts table if it doesn't exist."""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            contents TEXT DEFAULT '[]',
            cost REAL DEFAULT 0.0
        )
    ''')
    conn.commit()

def get_cart(username: str) -> list:
    """Retrieve the cart for the specified user."""
    with connect('carts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM carts WHERE username = ?', (username,))
        cart = cursor.fetchone()
        if not cart:
            return []
        contents = json.loads(cart['contents'])
        return contents

def add_to_cart(username: str, product_id: int):
    """Add a product to the user's cart."""
    with connect('carts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        row = cursor.fetchone()
        contents = json.loads(row['contents']) if row else []
        contents.append(product_id)
        cursor.execute('INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                       (username, json.dumps(contents), 0))
        conn.commit()

def remove_from_cart(username: str, product_id: int):
    """Remove a product from the user's cart."""
    with connect('carts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT contents FROM carts WHERE username = ?', (username,))
        row = cursor.fetchone()
        if not row:
            return
        contents = json.loads(row['contents'])
        if product_id in contents:
            contents.remove(product_id)
            cursor.execute('INSERT OR REPLACE INTO carts (username, contents, cost) VALUES (?, ?, ?)',
                           (username, json.dumps(contents), 0))
            conn.commit()

def delete_cart(username: str):
    """Delete the user's cart."""
    with connect('carts.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM carts WHERE username = ?', (username,))
        conn.commit()
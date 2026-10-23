
import sqlite3
from pathlib import Path

# Store the database in the same folder as this script.
DB_PATH = Path(__file__).resolve().parent / "supportpilot.db"


def initialize_database():
    connection = sqlite3.connect(DB_PATH)

    try:
        # Enforce foreign-key relationships.
        connection.execute("PRAGMA foreign_keys = ON")

        cursor = connection.cursor()

        # 1. Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

        # 2. Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                order_status TEXT NOT NULL
                    CHECK (order_status IN (
                        'placed', 'shipped', 'delivered',
                        'delayed', 'cancelled'
                    )),
                order_date TEXT NOT NULL,
                expected_delivery_date TEXT,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
        """)

        # 3. Support tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_id TEXT,
                issue TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'medium'
                    CHECK (priority IN (
                        'low', 'medium', 'high', 'urgent'
                    )),
                status TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN (
                        'open', 'in_progress',
                        'resolved', 'closed'
                    )),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id),
                FOREIGN KEY (order_id)
                    REFERENCES orders(order_id)
            )
        """)

        # Sample customers
        customers = [
            (1, "Aarav Sharma", "aarav@example.com"),
            (2, "Priya Patel", "priya@example.com"),
            (3, "Rohan Mehta", "rohan@example.com"),
            (4, "Ananya Singh", "ananya@example.com"),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO customers
                (customer_id, name, email)
            VALUES (?, ?, ?)
        """, customers)

        # Sample orders
        orders = [
            ("ORD1001", 1, "Wireless Headphones", "shipped",
             "2026-10-15", "2026-10-24"),
            ("ORD1002", 2, "Laptop Stand", "delivered",
             "2026-10-10", "2026-10-16"),
            ("ORD1003", 3, "Mechanical Keyboard", "delayed",
             "2026-10-14", "2026-10-23"),
            ("ORD1004", 1, "USB-C Hub", "placed",
             "2026-10-20", "2026-10-27"),
            ("ORD1005", 4, "Wireless Mouse", "cancelled",
             "2026-10-12", "2026-10-19"),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO orders (
                order_id, customer_id, product_name,
                order_status, order_date, expected_delivery_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, orders)

        # Sample support tickets
        tickets = [
            ("TKT1001", 2, "ORD1002",
             "Customer has a question about the delivered item.",
             "low", "open"),
            ("TKT1002", 3, "ORD1003",
             "Customer reports a delayed delivery.",
             "high", "open"),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO tickets (
                ticket_id, customer_id, order_id,
                issue, priority, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, tickets)

        connection.commit()

        print("Database initialized successfully!")
        print(f"Database location: {DB_PATH}")

        for table in ("customers", "orders", "tickets"):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()


import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "supportpilot.db"


def get_connection():
    """Create a database connection with foreign keys enabled."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_order(order_id):
    """Retrieve one order along with its customer's name and email."""
    with closing(get_connection()) as connection:
        row = connection.execute("""
            SELECT
                o.order_id,
                o.customer_id,
                c.name AS customer_name,
                c.email AS customer_email,
                o.product_name,
                o.order_status,
                o.order_date,
                o.expected_delivery_date
            FROM orders o
            JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
        """, (order_id,)).fetchone()

        return dict(row) if row else None


def get_customer_orders(customer_id):
    """Retrieve all orders belonging to a customer."""
    with closing(get_connection()) as connection:
        rows = connection.execute("""
            SELECT order_id, product_name, order_status,
                   order_date, expected_delivery_date
            FROM orders
            WHERE customer_id = ?
            ORDER BY order_date DESC
        """, (customer_id,)).fetchall()

        return [dict(row) for row in rows]


def create_ticket(customer_id, issue, priority="medium", order_id=None):
    """Create a persistent support ticket and return its ID."""
    if not isinstance(issue, str) or not issue.strip():
        raise ValueError("Issue description cannot be empty.")

    if priority not in {"low", "medium", "high", "urgent"}:
        raise ValueError("Invalid ticket priority.")

    ticket_id = f"TKT{uuid.uuid4().hex[:8].upper()}"

    with closing(get_connection()) as connection:
        try:
            # If an order is supplied, make sure it belongs
            # to the customer raising the ticket.
            if order_id is not None:
                order = connection.execute("""
                    SELECT customer_id
                    FROM orders
                    WHERE order_id = ?
                """, (order_id,)).fetchone()

                if order is None:
                    raise ValueError("Order not found.")

                if order["customer_id"] != customer_id:
                    raise ValueError(
                        "This order does not belong to this customer."
                    )

            connection.execute("""
                INSERT INTO tickets (
                    ticket_id, customer_id, order_id,
                    issue, priority, status
                )
                VALUES (?, ?, ?, ?, ?, 'open')
            """, (
                ticket_id,
                customer_id,
                order_id,
                issue.strip(),
                priority
            ))

            connection.commit()

        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError(
                "Could not create ticket. Check the customer ID, "
                "order ID, and ticket fields."
            ) from error

    return get_ticket(ticket_id)


def get_ticket(ticket_id):
    """Retrieve a ticket along with its customer's name."""
    with closing(get_connection()) as connection:
        row = connection.execute("""
            SELECT
                t.ticket_id,
                t.customer_id,
                c.name AS customer_name,
                t.order_id,
                t.issue,
                t.priority,
                t.status,
                t.created_at
            FROM tickets t
            JOIN customers c
                ON t.customer_id = c.customer_id
            WHERE t.ticket_id = ?
        """, (ticket_id,)).fetchone()

        return dict(row) if row else None

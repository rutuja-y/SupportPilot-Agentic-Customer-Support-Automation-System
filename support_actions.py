
import re

import db


VALID_PRIORITIES = {"low", "medium", "high", "urgent"}


def lookup_order_for_customer(order_id: str, customer_id: int) -> dict:
    """
    Look up an order only when it belongs to the supplied customer.

    Returns a generic not-found response for nonexistent orders and
    orders belonging to another customer.
    """
    if not isinstance(customer_id, int) or isinstance(customer_id, bool):
        raise ValueError("A valid customer ID is required.")

    if customer_id <= 0:
        raise ValueError("A valid customer ID is required.")

    if not isinstance(order_id, str) or not re.fullmatch(
        r"[A-Za-z0-9_-]{1,50}", order_id.strip()
    ):
        raise ValueError("A valid order ID is required.")

    order = db.get_order(order_id.strip())

    # Do not reveal whether another customer's order exists.
    if order is None or order["customer_id"] != customer_id:
        return {
            "success": False,
            "message": "Order not found for this customer.",
            "order": None,
        }

    return {
        "success": True,
        "message": "Order retrieved successfully.",
        "order": dict(order),
    }


def create_support_ticket(
    customer_id: int,
    issue: str,
    priority: str = "medium",
    order_id: str | None = None,
) -> dict:
    """Create a ticket through the existing validated database function."""
    if not isinstance(customer_id, int) or isinstance(customer_id, bool):
        raise ValueError("A valid customer ID is required.")

    if customer_id <= 0:
        raise ValueError("A valid customer ID is required.")

    if not isinstance(issue, str) or not issue.strip():
        raise ValueError("Ticket issue cannot be empty.")

    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}."
        )

    if order_id is not None:
        if not isinstance(order_id, str) or not re.fullmatch(
            r"[A-Za-z0-9_-]{1,50}", order_id.strip()
        ):
            raise ValueError("A valid order ID is required.")
        order_id = order_id.strip()

    ticket = db.create_ticket(
        customer_id=customer_id,
        issue=issue.strip(),
        priority=priority,
        order_id=order_id,
    )

    return {
        "success": True,
        "message": "Support ticket created successfully.",
        "ticket": dict(ticket),
    }


def confirm_ticket_creation(
    customer_id: int,
    issue: str,
    priority: str = "medium",
    order_id: str | None = None,
    confirmed: bool = False,
) -> dict:
    """Create a ticket only after an explicit confirmation."""
    if confirmed is not True:
        return {
            "success": False,
            "requires_confirmation": True,
            "message": "Please confirm before creating this ticket.",
        }

    result = create_support_ticket(
        customer_id=customer_id,
        issue=issue,
        priority=priority,
        order_id=order_id,
    )

    result["requires_confirmation"] = False
    return result

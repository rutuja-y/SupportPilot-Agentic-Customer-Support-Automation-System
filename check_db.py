
from db import (
    get_order,
    get_customer_orders,
    create_ticket,
    get_ticket,
)

# Test 1: Retrieve an existing order
order = get_order("ORD1003")
print("ORDER LOOKUP:", order)

# Test 2: Retrieve a nonexistent order
missing_order = get_order("ORD9999")
print("MISSING ORDER:", missing_order)

# Test 3: Retrieve a customer's orders
orders = get_customer_orders(1)
print("CUSTOMER 1 ORDERS:", orders)

# Test 4: Create a ticket linked to a valid order
ticket = create_ticket(
    customer_id=3,
    order_id="ORD1003",
    issue="My order is delayed. Please investigate.",
    priority="high",
)

print("CREATED TICKET:", ticket)

# Test 5: Retrieve the saved ticket
saved_ticket = get_ticket(ticket["ticket_id"])
print("RETRIEVED TICKET:", saved_ticket)

# Test 6: Check that an invalid order/customer pairing is rejected
try:
    create_ticket(
        customer_id=2,
        order_id="ORD1003",
        issue="Checking order ownership validation",
    )
except ValueError as error:
    print("EXPECTED VALIDATION ERROR:", error)

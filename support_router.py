
import re
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from support_actions import (
    confirm_ticket_creation,
    lookup_order_for_customer,
)
from support_graph import (
    classify_request,
    generate_answer,
    retrieve_knowledge,
)


class RoutedSupportState(TypedDict):
    query: str
    customer_id: int | None
    order_id: str | None
    ticket_issue: str | None
    ticket_priority: str
    ticket_confirmed: bool
    intent: str
    category: str
    retrieved_chunks: list[dict]
    answer: str
    sources: list[str]
    action_result: dict


def classify_intent(state: RoutedSupportState) -> dict:
    """Route using simple, inspectable rules rather than free-form SQL."""
    query = state["query"].lower()

    ticket_patterns = (
        "create a ticket",
        "raise a ticket",
        "open a ticket",
        "create a support ticket",
        "raise a complaint",
    )
    order_patterns = (
        "where is my order",
        "track my order",
        "order status",
        "check my order",
        "track order",
    )

    if any(pattern in query for pattern in ticket_patterns):
        intent = "ticket"
    elif any(pattern in query for pattern in order_patterns):
        intent = "order_lookup"
    else:
        intent = "knowledge"

    return {"intent": intent}


def route_intent(
    state: RoutedSupportState,
) -> Literal["knowledge", "order_lookup", "ticket"]:
    intent = state["intent"]
    if intent in {"knowledge", "order_lookup", "ticket"}:
        return intent
    return "knowledge"


def handle_order_lookup(state: RoutedSupportState) -> dict:
    customer_id = state.get("customer_id")
    order_id = state.get("order_id")

    if customer_id is None or not order_id:
        return {
            "answer": (
                "To check an order, please provide your customer ID and "
                "order ID. In a real deployment, the customer ID should "
                "come from an authenticated session."
            ),
            "action_result": {
                "success": False,
                "message": "Customer ID and order ID are required.",
            },
        }

    result = lookup_order_for_customer(order_id, customer_id)

    if not result["success"]:
        answer = "I couldn't find that order for this customer."
    else:
        order = result["order"]
        answer = (
            f"Order {order['order_id']} is currently "
            f"{order['order_status']}."
        )

        if order.get("expected_delivery_date"):
            answer += (
                f" The current estimated delivery date is "
                f"{order['expected_delivery_date']}."
            )

    return {"answer": answer, "action_result": result}


def handle_ticket_request(state: RoutedSupportState) -> dict:
    customer_id = state.get("customer_id")
    issue = state.get("ticket_issue") or state["query"]
    priority = state.get("ticket_priority", "medium")
    order_id = state.get("order_id")
    confirmed = state.get("ticket_confirmed", False)

    if customer_id is None:
        return {
            "answer": (
                "I can help prepare a support ticket, but I need a customer "
                "ID. In a real deployment, this should come from your "
                "authenticated session."
            ),
            "action_result": {
                "success": False,
                "requires_confirmation": False,
                "message": "Customer ID is required.",
            },
        }

    if not confirmed:
        return {
            "answer": (
                "Please confirm that you want me to create a support ticket "
                f"for this issue: {issue.strip()}"
            ),
            "action_result": {
                "success": False,
                "requires_confirmation": True,
                "message": "Ticket has not been created.",
            },
        }

    result = confirm_ticket_creation(
        customer_id=customer_id,
        issue=issue,
        priority=priority,
        order_id=order_id,
        confirmed=True,
    )

    if result["success"]:
        ticket = result["ticket"]
        answer = (
            f"Your support ticket {ticket['ticket_id']} has been created."
        )
    else:
        answer = result["message"]

    return {"answer": answer, "action_result": result}

def classify_category(state: RoutedSupportState) -> dict:
    return classify_request(state)

def build_routed_support_graph():
    builder = StateGraph(RoutedSupportState)

    builder.add_node("classify_intent", classify_intent)
    builder.add_node("classify_category", classify_category)
    builder.add_node("retrieve", retrieve_knowledge)
    builder.add_node("answer_knowledge", generate_answer)
    builder.add_node("order_lookup", handle_order_lookup)
    builder.add_node("ticket", handle_ticket_request)

    builder.add_edge(START, "classify_intent")

    builder.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "knowledge": "classify_category",
            "order_lookup": "order_lookup",
            "ticket": "ticket",
        },
    )

    builder.add_edge("classify_category", "retrieve")
    builder.add_edge("retrieve", "answer_knowledge")
    builder.add_edge("answer_knowledge", END)
    builder.add_edge("order_lookup", END)
    builder.add_edge("ticket", END)

    return builder.compile()


routed_support_graph = build_routed_support_graph()


def run_routed_support(
    query: str,
    customer_id: int | None = None,
    order_id: str | None = None,
    ticket_issue: str | None = None,
    ticket_priority: str = "medium",
    ticket_confirmed: bool = False,
) -> dict:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Customer question cannot be empty.")

    initial_state: RoutedSupportState = {
        "query": query.strip(),
        "customer_id": customer_id,
        "order_id": order_id,
        "ticket_issue": ticket_issue,
        "ticket_priority": ticket_priority,
        "ticket_confirmed": ticket_confirmed,
        "intent": "knowledge",
        "category": "other",
        "retrieved_chunks": [],
        "answer": "",
        "sources": [],
        "action_result": {},
    }

    result = routed_support_graph.invoke(initial_state)

    return {
        "query": result["query"],
        "intent": result["intent"],
        "category": result["category"],
        "answer": result["answer"],
        "sources": result["sources"],
        "action_result": result["action_result"],
    }

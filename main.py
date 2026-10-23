
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import db


app = FastAPI(
    title="SupportPilot API",
    description="Backend API for customer support automation.",
    version="1.0.0",
)


# ---------- Request and response schemas ----------

class OrderResponse(BaseModel):
    order_id: str
    customer_id: int
    customer_name: str
    customer_email: str
    product_name: str
    order_status: str
    order_date: str
    expected_delivery_date: str | None


class TicketCreate(BaseModel):
    customer_id: int = Field(gt=0)
    issue: str = Field(min_length=1, max_length=1000)
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    order_id: str | None = None


class TicketResponse(BaseModel):
    ticket_id: str
    customer_id: int
    customer_name: str
    order_id: str | None
    issue: str
    priority: str
    status: str
    created_at: str


# ---------- Endpoints ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: str):
    order = db.get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found.",
        )

    return order


@app.post("/tickets", response_model=TicketResponse, status_code=201)
def create_support_ticket(ticket: TicketCreate):
    try:
        created_ticket = db.create_ticket(
            customer_id=ticket.customer_id,
            order_id=ticket.order_id,
            issue=ticket.issue,
            priority=ticket.priority,
        )

        return created_ticket

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

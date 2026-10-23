
import streamlit as st
from support_router import run_routed_support

st.set_page_config(
    page_title="SupportPilot",
    page_icon="🎧",
    layout="centered",
)

st.title("🎧 SupportPilot")
st.caption("AI-powered customer support assistant")

st.info(
    "Ask about shipping, returns, refunds, warranty, "
    "troubleshooting, or your order."
)

with st.sidebar:
    st.header("Customer Details")
    customer_id = st.number_input(
        "Customer ID",
        min_value=1,
        value=1,
        step=1,
    )
    order_id = st.text_input(
        "Order ID (optional)",
        placeholder="e.g. ORD1001",
    )

    st.caption("Demo application using synthetic customer data.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_ticket" not in st.session_state:
    st.session_state.pending_ticket = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("How can I help you today?")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_routed_support(
                    query=prompt,
                    customer_id=int(customer_id),
                    order_id=order_id.strip() or None,
                )

                st.markdown(result["answer"])

                if result.get("sources"):
                    with st.expander("Knowledge sources"):
                        for source in result["sources"]:
                            st.write(f"- {source}")

                if result["action_result"].get(
                    "requires_confirmation"
                ):
                    st.session_state.pending_ticket = {
                        "query": prompt,
                        "customer_id": int(customer_id),
                        "order_id": order_id.strip() or None,
                    }

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                    }
                )

            except Exception as exc:
                error_message = (
                    "Sorry, something went wrong while processing "
                    "your request. Please try again."
                )
                st.error(error_message)
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

if st.session_state.pending_ticket:
    st.divider()
    st.subheader("Confirm Support Ticket")

    pending = st.session_state.pending_ticket
    st.write("Create a ticket for the following issue?")
    st.write(f"**Issue:** {pending['query']}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Confirm and Create Ticket", type="primary"):
            try:
                result = run_routed_support(
                    query="Create a support ticket",
                    customer_id=pending["customer_id"],
                    order_id=pending["order_id"],
                    ticket_issue=pending["query"],
                    ticket_confirmed=True,
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                    }
                )
                st.session_state.pending_ticket = None
                st.rerun()

            except Exception:
                st.error(
                    "Ticket creation failed. Please try again."
                )

    with col2:
        if st.button("Cancel"):
            st.session_state.pending_ticket = None
            st.rerun()

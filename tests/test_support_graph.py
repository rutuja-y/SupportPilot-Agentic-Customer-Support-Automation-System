
from types import SimpleNamespace

import pytest

import support_graph


class FakeGroqClient:
    """Return predictable responses without calling the real Groq API."""

    def __init__(self):
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self.create)
        )

    def create(self, **kwargs):
        system_message = kwargs["messages"][0]["content"]

        if "Classify the customer's support question" in system_message:
            content = "shipping"
        else:
            content = (
                "Standard delivery usually takes 3–5 business days "
                "after an order is shipped."
            )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )
            ]
        )


def test_workflow_returns_structured_answer(monkeypatch):
    monkeypatch.setattr(
        support_graph,
        "get_groq_client",
        lambda: FakeGroqClient(),
    )
    monkeypatch.setattr(
        support_graph,
        "search_knowledge",
        lambda query, top_k=3: [
            {
                "text": "Standard delivery usually takes 3–5 business days.",
                "metadata": {
                    "source": "shipping.md",
                    "title": "Shipping and Delivery Policy",
                    "category": "shipping",
                },
                "distance": 0.2,
            }
        ],
    )

    result = support_graph.run_support_workflow(
        "How long does shipping take?"
    )

    assert result["category"] == "shipping"
    assert "3–5 business days" in result["answer"]
    assert result["sources"] == ["shipping.md"]
    assert result["query"] == "How long does shipping take?"


def test_empty_question_is_rejected():
    with pytest.raises(ValueError):
        support_graph.run_support_workflow("   ")


def test_unknown_category_is_normalized(monkeypatch):
    class UnknownCategoryClient:
        def __init__(self):
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create)
            )

        def create(self, **kwargs):
            system_message = kwargs["messages"][0]["content"]

            if "Classify the customer's support question" in system_message:
                content = "something unexpected"
            else:
                content = "I cannot confirm that from the available policy."

            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=content)
                    )
                ]
            )

    monkeypatch.setattr(
        support_graph,
        "get_groq_client",
        lambda: UnknownCategoryClient(),
    )
    monkeypatch.setattr(
        support_graph,
        "search_knowledge",
        lambda query, top_k=3: [],
    )

    result = support_graph.run_support_workflow(
        "Can you help me with something unusual?"
    )

    assert result["category"] == "other"
    assert result["sources"] == []

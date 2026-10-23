# SupportPilot — Evaluation Report

## 1. Project Overview

SupportPilot is an AI-powered customer support automation system built with Python, LangGraph, retrieval-augmented generation (RAG), ChromaDB, SQLite, FastAPI, and Streamlit.

## 2. Testing Results

| Evaluation                                   | Result                                      |
| -------------------------------------------- | ------------------------------------------- |
| Automated test suite                         | 52 tests passed                             |
| Knowledge retrieval source hit rate at top 3 | 5/5 (100%)                                  |
| Generated-answer checks                      | Reviewed manually; answers appeared correct |
| Order lookup                                 | Verified with integration tests             |
| Ticket creation                              | Verified with integration tests             |
| Ticket confirmation                          | Tested before ticket creation               |

## 3. Evaluation Method

The retrieval evaluation used five representative questions covering shipping, returns, warranty, and troubleshooting. A case passed when its expected knowledge-base source appeared among the top three retrieved chunks.

Integration tests checked the routed workflow, local database lookups, and confirmed ticket creation. Unit tests used mocks where appropriate to keep tests repeatable.

## 4. Limitations

- The retrieval evaluation dataset is small and does not represent all customer questions.
- Source hit rate does not guarantee that every retrieved chunk is relevant or that the final answer is factually correct.
- Generated answers were checked manually and with basic automated sanity checks.
- Customer authentication and production-grade authorization are not implemented.
- The system has not been evaluated under production traffic or load.

## 5. Conclusion

The initial tests indicate that SupportPilot's core workflow operates as expected on the evaluated scenarios. Broader evaluation, security improvements, and deployment testing would be required before production use.

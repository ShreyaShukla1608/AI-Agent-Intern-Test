import re
from typing import Dict, Any
from src.rag.retriever import PolicyRetriever
from src.tools.order_lookup import lookup_order


class SupportAgent:
    def __init__(self):
        self.retriever = PolicyRetriever()

    def _extract_order_id(self, query: str) -> str | None:
        # Match standard ORD-XXXX patterns
        match = re.search(r"\bORD[-_]?\d+\b", query, re.IGNORECASE)
        if match:
            return match.group(0)

    
        keyword_match = re.search(r"order\s+(?:id|number|#)\s*:?\s*([^\s,?.!]+)", query, re.IGNORECASE)
        if keyword_match:
            candidate = keyword_match.group(1).strip()
            if candidate and candidate.lower() not in ["status", "for", "is", "where", "my", "the"]:
                return candidate

        return None

    def _contains_pii_request(self, query: str) -> bool:
        sensitive_patterns = [
            r"\bcredit card\b", r"\bcvv\b", r"\bpassword\b",
            r"\bssn\b", r"\bsocial security\b", r"\bapi[ _]?key\b",
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in sensitive_patterns)

    def _contains_prompt_injection(self, query: str) -> bool:
        injection_patterns = [
            r"ignore previous instructions", r"system prompt",
            r"you are now DAN", r"override safety",
        ]
        return any(re.search(p, query, re.IGNORECASE) for p in injection_patterns)

    def run(self, query: str) -> Dict[str, Any]:
        if self._contains_prompt_injection(query):
            return {
                "response": "I cannot fulfill requests that attempt to override system safety rules.",
                "sources": [],
            }

        if self._contains_pii_request(query):
            return {
                "response": "For security reasons, I cannot process or reveal private financial or authentication details.",
                "sources": [],
            }

        order_id = self._extract_order_id(query)
        if order_id or any(t in query.lower() for t in ["where is my order", "order status"]):
            if not order_id:
                return {
                    "response": "I can help with that! Please provide your Order ID (e.g., ORD-1001).",
                    "sources": [],
                }

            order_data = lookup_order(order_id)
            if "error" in order_data:
                return {"response": order_data["error"], "sources": []}

            items = ", ".join([i.get("name", "Item") for i in order_data.get("items", [])])
            resp = f"Order {order_data['order_id']} ({items}) is currently {order_data['status']}."
            if order_data.get("delivery_estimate"):
                resp += f" Estimated delivery: {order_data['delivery_estimate']}."

            return {"response": resp, "sources": []}

        retrieved_docs = self.retriever.retrieve(query)
        sources = [doc["source"] for doc in retrieved_docs]

        if not retrieved_docs:
            return {
                "response": "I couldn't find details matching your inquiry. Please reach out to customer support directly.",
                "sources": [],
            }

        top_doc = retrieved_docs[0]
        response_text = f"According to {top_doc['source']}:\n\n{top_doc['content']}"

        return {"response": response_text, "sources": sources}
import json
import logging
import re
from typing import List, Dict, Any
from src.tools.order_lookup import lookup_order
from src.rag.retriever import PolicyRetriever
from src.agent.agent import SupportAgent

__all__ = ["SupportAgent"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SupportAgent")

class SupportAgent:
    def __init__(self):
        self.retriever = PolicyRetriever()
        self.conversation_history: List[Dict[str, str]] = []

    def run(self, user_message: str) -> Dict[str, Any]:
        logger.info(f"User Message: {user_message}")
        self.conversation_history.append({"role": "user", "content": user_message})
        
        lower_msg = user_message.lower()
        
    
        if any(w in lower_msg for w in ["system prompt", "hidden instructions", "reveal secrets", "ignore previous"]):
            response = "I am unable to share my internal instructions or system configuration. How can I help you with your Aster & Row order or policies today?"
            self.conversation_history.append({"role": "assistant", "content": response})
            return {
                "response": response, 
                "handoff": False, 
                "sources": [], 
                "tool_result": None
            }


        tool_result = None
        order_match = re.search(r"ord-\d+", lower_msg)
        
        if order_match:
            order_id = order_match.group(0).upper()
            tool_result = lookup_order(order_id)
        elif "order" in lower_msg and any(kw in lower_msg for kw in ["where", "status", "track", "check", "find"]):
            response = "I'd be happy to check that for you! Could you please provide your Order ID (e.g., ORD-1001)?"
            self.conversation_history.append({"role": "assistant", "content": response})
            return {
                "response": response, 
                "handoff": False, 
                "sources": [], 
                "tool_result": None
            }


        retrieved_passages = self.retriever.retrieve(user_message)
        sources = [p["source"] for p in retrieved_passages]
        
        context_text = "\n\n".join([f"[{p['source']}]: {p['content']}" for p in retrieved_passages])
        if tool_result:
            context_text += f"\n\n[Tool Result]: {json.dumps(tool_result)}"


        if tool_result and "error" in tool_result:
            response = tool_result["error"]
            handoff = False
        elif tool_result:
            status = tool_result.get("status", "Unknown")
            est = tool_result.get("delivery_estimate") or "Unavailable"
            response = f"Your order ({tool_result['order_id']}) is currently **{status}**."
            if tool_result.get("delivery_estimate"):
                response += f" Estimated delivery: {est}."
            if tool_result.get("note"):
                response += f" {tool_result['note']}"
            handoff = False
        elif "conflict" in context_text.lower() or len(retrieved_passages) == 0:
            response = "I found conflicting or insufficient information regarding your request in our active policies. I recommend connecting with a human support agent for clarification."
            handoff = True
        else:
            primary_source = sources[0] if sources else "Aster & Row Policy Guidelines"
            response = f"Based on our active guidelines ({primary_source}), here is what you need to know: [Synthesized answer based strictly on retrieved text]."
            handoff = False

        self.conversation_history.append({"role": "assistant", "content": response})
        
        trace = {
            "user_message": user_message,
            "history_length": len(self.conversation_history),
            "retrieved_passages": sources,
            "tool_result": tool_result,
            "final_response": response,
            "handoff": handoff
        }
        logger.info(f"Trace: {json.dumps(trace)}")
        
        return {
            "response": response,
            "sources": sources,
            "handoff": handoff,
            "tool_result": tool_result,
            "trace": trace
        }
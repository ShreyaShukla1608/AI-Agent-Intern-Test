# cli.py
import json
from src.agent.support_agent import SupportAgent

def main():
    agent = SupportAgent()
    print("--- Aster & Row Support Agent CLI ---")
    print("Type 'exit' or 'quit' to end the session.\n")

    while True:
        try:
            user_input = input("Customer: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break

            result = agent.run(user_input)

            print("\nAgent Response:")
            print(result["response"])

            if result.get("sources"):
                print(f"\nSources: {', '.join(result['sources'])}")
            if result.get("handoff"):
                print("\n[Flag: Human Handoff Recommended]")

            print("\n" + "-" * 50 + "\n")

        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
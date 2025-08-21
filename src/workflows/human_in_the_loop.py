# src/pantheon/workflows/human_in_the_loop.py
import sys

from src.observability import logger


class HITLManager:
    """
    Manages the human-in-the-loop approval process.
    """
    def request_approval(self, prompt: str) -> bool:
        """
        Pauses the workflow and requests human approval from the console.
        In non-interactive environments, it defaults to 'no'.
        """
        print("--- [HITL] Approval Required ---")
        print(f"PROMPT: {prompt}")

        if not sys.stdout.isatty():
            logger.warning("Non-interactive environment detected. Defaulting to 'no'.")
            return False

        while True:
            response = input("Approve? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                approved = True
                break
            elif response in ['n', 'no']:
                approved = False
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        print(f"RESPONSE: {'Approved' if approved else 'Rejected'}")
        print("--- [HITL] Resuming Workflow ---")
        return approved

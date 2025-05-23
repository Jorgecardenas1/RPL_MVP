import os


from intent_detector import IntentDetector  # your working Groq detector
from orchestrator import Orchestrator
from knowledge.store import KnowledgeStore

if __name__ == "__main__":


    intent_detector = IntentDetector()
    store = KnowledgeStore()

    orchestrator = Orchestrator(store)

    while True:
        user_input = input("\nUser: ")
        result = intent_detector.detect(user_input)
        response = orchestrator.process_intent(result)
        print("Ripple Copilot:", response)

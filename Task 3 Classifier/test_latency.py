# test_latency.py
# tests 20 tickets and asserts each prediction is valid and under 500ms

import time
from classifier import TicketClassifier
import os
import warnings
warnings.filterwarnings("ignore")

VALID_LABELS = {"billing", "technical_issue", "feature_request", "complaint", "other"}
MAX_LATENCY_MS = 500

tickets = [
    "I was charged twice this month and need a refund.",
    "The app crashes every time I try to open a project.",
    "Can you please add a dark mode option?",
    "Your support team has been completely unhelpful.",
    "How do I reset my password?",
    "My invoice shows the wrong amount.",
    "The export button does nothing when I click it.",
    "It would be great to have Slack integration.",
    "I have been waiting a week with no response.",
    "Where can I find the API documentation?",
    "I was billed for a plan I never selected.",
    "The mobile app is stuck on the loading screen.",
    "Please add support for bulk CSV import.",
    "This product is not worth the price I am paying.",
    "What are your business hours?",
    "My payment failed but money was deducted from my account.",
    "Two factor authentication codes are not arriving.",
    "Can you add keyboard shortcuts to the editor?",
    "I am extremely frustrated with the lack of support.",
    "How do I invite a team member to my workspace?"
]

def test_latency():
    classifier = TicketClassifier()
    print(f"Running latency test on {len(tickets)} tickets...\n")

    all_passed = True

    for ticket in tickets:
        start = time.time()
        prediction = classifier.predict(ticket)
        elapsed_ms = (time.time() - start) * 1000

        valid = prediction in VALID_LABELS
        fast = elapsed_ms < MAX_LATENCY_MS

        status = "PASS" if valid and fast else "FAIL"
        if not (valid and fast):
            all_passed = False

        print(f"[{status}] {elapsed_ms:6.1f}ms | {prediction:20s} | {ticket[:50]}")

    print(f"\n{'All tests passed' if all_passed else 'Some tests failed'}")
    assert all_passed, "One or more tickets failed the latency or label validity check"

if __name__ == "__main__":
    test_latency()
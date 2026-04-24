# evaluate.py
# loads test.json, runs classifier on all 200 examples
# reports accuracy, per-class F1, confusion matrix

import json
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
from classifier import TicketClassifier
import os
import warnings
warnings.filterwarnings("ignore")

LABELS = ["billing", "technical_issue", "feature_request", "complaint", "other"]

def evaluate():
    with open("data/test.json") as f:
        test_data = json.load(f)

    classifier = TicketClassifier()

    true_labels = [d["label"] for d in test_data]
    pred_labels = [classifier.predict(d["text"]) for d in test_data]

    accuracy = accuracy_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels, average=None, labels=LABELS)
    cm = confusion_matrix(true_labels, pred_labels, labels=LABELS)

    print(f"\nAccuracy: {accuracy:.2f}")
    print(f"\nPer-class F1:")
    for label, score in zip(LABELS, f1):
        print(f"  {label:20s}: {score:.2f}")



    print(f"\nConfusion Matrix:")
    print(f"{'':20s}", end="")
    for l in LABELS:
        print(f"{l[:8]:>10s}", end="")
    print()
    for i, row in enumerate(cm):
        print(f"{LABELS[i]:20s}", end="")
        for val in row:
            print(f"{val:>10d}", end="")
        print()

if __name__ == "__main__":
    evaluate()
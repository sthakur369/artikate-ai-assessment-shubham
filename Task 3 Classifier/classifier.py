# classifier.py
# loads trained model and predicts label for a given ticket text

from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import os
import warnings
warnings.filterwarnings("ignore")


class TicketClassifier:
    def __init__(self, model_path="./model"):
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def predict(self, text):
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        predicted_id = outputs.logits.argmax(dim=1).item()
        return self.model.config.id2label[predicted_id]


if __name__ == "__main__":
    classifier = TicketClassifier()
    tests = [
        "I was charged twice this month",
        "The app crashes on startup",
        "Can you add dark mode please",
        "Your support is terrible",
        "How do I reset my password"
    ]
    for t in tests:
        print(f"{classifier.predict(t):20s} | {t}")
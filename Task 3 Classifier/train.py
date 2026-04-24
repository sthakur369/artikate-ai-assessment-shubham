# fine-tunes DistilBERT on our 800 training examples

import json
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import torch

LABELS = ["billing", "technical_issue", "feature_request", "complaint", "other"]
label2id = {l: i for i, l in enumerate(LABELS)}
id2label = {i: l for i, l in enumerate(LABELS)}

class TicketDataset(Dataset):
    def __init__(self, data, tokenizer):
        self.encodings = tokenizer(
            [d["text"] for d in data],
            truncation=True,
            padding=True,
            max_length=128
        )
        self.labels = [label2id[d["label"]] for d in data]

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item


def train():
    with open("data/train.json") as f:
        train_data = json.load(f)

    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(LABELS),
        id2label=id2label,
        label2id=label2id
    )

    dataset = TicketDataset(train_data, tokenizer)

    args = TrainingArguments(
        output_dir="./model",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        save_strategy="epoch",
        logging_steps=50,
            no_cuda=True    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset
    )

    trainer.train()
    model.save_pretrained("./model")
    tokenizer.save_pretrained("./model")
    print("Model saved to ./model")


if __name__ == "__main__":
    train()
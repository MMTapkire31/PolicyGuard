import pandas as pd
from datasets import Dataset
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer
)
import torch

# Step 1 — Load our CSV dataset
df = pd.read_csv('../data/privacy_dataset.csv')
# Basic cleaning
df['sentence'] = df['sentence'].str.strip()    # Remove extra spaces
df['sentence'] = df['sentence'].dropna()       # Remove empty rows
df = df[df['sentence'].str.len() > 10]         # Remove very short sentences

# Convert to HuggingFace Dataset format
dataset = Dataset.from_pandas(df)

# Split into train (80%) and test (20%)
dataset = dataset.train_test_split(test_size=0.2)

# Step 2 — Load DistilBERT tokenizer
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

def tokenize(batch):
    return tokenizer(
        batch['sentence'],
        truncation=True,      # Cut off at 512 tokens
        padding='max_length', # Pad shorter sentences to 512
        max_length=512
    )

# Apply tokenization to entire dataset
dataset = dataset.map(tokenize, batched=True)

# Step 3 — Load DistilBERT model
# num_labels=2 because we have 2 classes: risky(1) and safe(0)
model = DistilBertForSequenceClassification.from_pretrained(
    'distilbert-base-uncased',
    num_labels=2
)

# Step 4 — Define training settings
training_args = TrainingArguments(
    output_dir='./model',               # Where to save model checkpoints
    num_train_epochs=3,                 # 3 passes over entire training dataset
    per_device_train_batch_size=16,     # Process 16 sentences at once during training
    per_device_eval_batch_size=16,      # Process 16 sentences at once during evaluation
    eval_strategy='epoch',              # Evaluate model performance after each epoch
    save_strategy='epoch',              # Save model checkpoint after each epoch
    load_best_model_at_end=True,        # After all epochs keep the best performing one
)

# Step 5 — Trainer handles the training loop for us
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['test']
)

# Step 6 — Train
trainer.train()

# Step 7 — Save fine-tuned model so analyzer.py can load it
model.save_pretrained('./model/policyguard')
tokenizer.save_pretrained('./model/policyguard')
print("Model saved to ./model/policyguard")
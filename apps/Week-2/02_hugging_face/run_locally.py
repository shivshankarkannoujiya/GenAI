"""
Text generation using Hugging Face Transformers
"""

# Install dependencies (run once in Colab / notebook)
# !pip install transformers

import os
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# --------------------------------------------------
# Configuration
# --------------------------------------------------
MODEL_NAME = "google/gemma-3-1b-it"

# Read token from environment (DO NOT hardcode)
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise RuntimeError(
        "HF_TOKEN is not set. " "Please export it as an environment variable."
    )

# --------------------------------------------------
# Load tokenizer & model
# --------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=HF_TOKEN)

model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, token=HF_TOKEN)

# --------------------------------------------------
# Text generation pipeline
# --------------------------------------------------
gen_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

# --------------------------------------------------
# Run inference
# --------------------------------------------------
output = gen_pipeline("hey there", max_new_tokens=256)

print(output)

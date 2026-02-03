import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def main():
    # 1. Configuration and Model Setup
    # Using the Gemma 2b model as specified in the notebook
    model_id = "google/gemma-2b"
    dtype = torch.bfloat16

    # 2. Initialize Tokenizer
    # Loads the tokenizer associated with the Gemma model
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    # 3. Load the Model
    # Loads the model onto the GPU (cuda) with specified precision
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=dtype,
        device_map="cuda",
    )

    # 4. Prepare Input
    # The prompt used for generation
    chat = [
        {"role": "user", "content": "Write a hello world program in C++"},
    ]

    # Formatting the chat into a template the model understands
    prompt = tokenizer.apply_chat_template(
        chat, tokenize=False, add_generation_prompt=True
    )
    inputs = tokenizer.encode(prompt, add_special_tokens=True, return_tensors="pt")
    inputs = inputs.to("cuda")

    # 5. Generate Output
    # The model generates a response based on the encoded inputs
    gen_result = model.generate(input_ids=inputs, max_new_tokens=150)

    # 6. Decode and Display
    # Converts the generated token IDs back into human-readable text
    output = tokenizer.batch_decode(gen_result)
    print(output)


if __name__ == "__main__":
    main()

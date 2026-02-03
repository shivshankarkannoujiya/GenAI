import asyncio
from fastapi import FastAPI
from ollama import Client

app = FastAPI()

client = Client(
    host="http://localhost:11434"
)

client.pull("llama3.2:1b")

# @app.post("/chat")
# async def chat():
#     response = client.chat(
#         model="gemma3:1b",
#         messages=[
#             {"role": "user", "content": "Hey there"}
#         ]
#     )

#     return response["message"]["content"]

@app.post("/chat")
async def chat():
    response = await asyncio.to_thread(
        client.chat,
        model="llama3.2:1b",
        messages=[{"role": "user", "content": "Hello"}],
    )

    return response

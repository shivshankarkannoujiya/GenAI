import os
from dotenv import load_dotenv
from mem0 import Memory
from openai import OpenAI

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "text-embeddings-3-small"},
    },
    "llm": {
        "provider": "openai",
        "config": {"api_key": OPENAI_API_KEY, "model": "gpt-4o-mini"},
    },
    # 🔹 Vector Memory (Semantic Recall)
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": "6333"},
    },
    # 🔹 Graph Memory (Relationships & Facts)
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
        },
    },
}

mem_client = Memory.from_config(config)
openai_clinet = OpenAI(api_key=OPENAI_API_KEY)


def chat(message):

    relevant_memories = mem_client.search(query=message, user_id="xyz")
    print(relevant_memories)
    print(relevant_memories.get("results"))

    # Build Context
    memories = "\n".join([m["memory"] for m in relevant_memories.get("results")])

    print(memories)

    SYSTEM_PROMPT = f"""
    You are a Memory-Aware Fact Extraction Agent.
    An advance AI desing to systematically analyze input content,
    extract structured knowledge and maintain an optimized memory store.
    Your primary function is information distillation and knowledge preservation
    with contextual awareness

    Tone: Professional analytical, precision focused, with clear uncertainity signaling

    Memory and Score
    {memories}
    """

    messages = [
        {"role": "user", "content": message},
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    result = openai_clinet.chat.completions.create(
        model="gpt-4o-mini", messages=messages
    )

    messages.append({"role": "assistant", "content": result.choices[0].message.content})

    mem_client.add(messages, user_id="xyz")

    return result.choices[0].message.content


while True:
    message = input("ASK: ")
    print("RES:", chat(message=message))

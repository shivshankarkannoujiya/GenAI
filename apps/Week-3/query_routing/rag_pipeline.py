"""
TODO:
RAG Pipeline — Multi-Query + Query Routing + RRF
Stack   : OpenAI · Pinecone · PostgreSQL · Tavily
"""

import os
import re
import json
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

from openai import AsyncOpenAI
from pinecone import Pinecone
import asyncpg
from tavily import TavilyClient


class DataStore(str, Enum):
    VECTOR_DB = "vector_db"
    SQL_DB = "sql_db"
    WEB_SEARCH = "web_search"


@dataclass
class Document:
    content: str
    source: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class RouteDecision:
    query: str
    datastore: DataStore
    reasoning: str


openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

PINECONE_INDEX = pinecone_client.Index(os.getenv("PINECONE_INDEX_NAME", "rag-index"))


# MULTI-QUERY GENERATOR
async def generate_multi_queries(query: str, n: int = 3) -> list[str]:
    """
    Rewrites the original query into N semantically distinct variations
    More coverage: better recall from retrievers.
    """

    prompt = f"""
    You are an expert in reformulating search queries.
    Given the user query below, generate {n} different version that capture different angle of 
    the same information need.

    Rules:
    - Each variation must be semantically distinct.
    - Preserve the original intent.
    - Do NOT explain.
    - Do NOT include numbering or bullet points.
    - Only output the queries, each on a new line
    


    User query: {query}    
    """
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    raw = response.choices[0].message.content.strip()

    generated = []
    for line in raw.split("\n"):
        line = line.strip()

    # remove numbering like "1. ", "- ", "* "
    line = re.sub(r"^(\d+[\).\-\s]+|[-*\s]+)", "", line)

    if 5 < len(line) < 200:
        generated.append(line)

    final_queries = [query] + generated

    # Deduplicate while preserving order
    seen = set()
    unique_queries = []

    for q in final_queries:
        q_lower = q.lower()
        if q_lower not in seen:
            unique_queries.append(q)
            seen.add(q_lower)

    return unique_queries[: n + 1]


# QUERY ROUTER
async def route_query(query: str) -> RouteDecision:
    """
    Single router — called independently for each query.
    Classifies which datastore is best suited for the given query.
    """

    prompt = f"""
    You are query routing expert for a RAG system with three datastores:

    1. vector_db: Conceptual, semantic, or document-based questions
    2. sql_db: Structured, numerical, aggregation or tabular questions
    3. web_search: Real-time, current events, or live data questions   

    Analyze this query and return JSON only:
    {{"datastore": "<on of:  vector_db | sql_db | web_search>", "reasoning": "<one sentence>"}}  
      
    Query: {query} 
    """

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return RouteDecision(
        query=query,
        datastore=DataStore(result["datastore"]),
        reasoning=result["reasoning"],
    )


# RETRIEVERS (one per datastore)
async def _embed(text: str) -> list[float]:
    """Shared embedding utility."""
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )

    return response.data[0].embedding


async def retrieve_from_vector_db(query: str, top_k: int = 5) -> list[Document]:
    """Semantic search via Pinecone."""
    vector = await _embed(query)

    results = PINECONE_INDEX.query(vector=vector, top_k=top_k, include_metadata=True)

    return [
        Document(
            content=match.metadata.get("text", ""),
            source="vector_db",
            score=match.score,
            metadata=match.metadata,
        )
        for match in results.matches
    ]


async def retrieve_from_sql(query: str) -> list[Document]:
    """
    LLM generates SQL → executes against PostgreSQL.
    Adapt the schema description to your actual tables.
    """
    schema_desc = """
    Tables:
    - products(id, name, category, price, stock)
    - orders(id, product_id, quantity, created_at)
    - customers(id, name, email, region)
    """

    sql_prompt = """
    Convert this natural language query to SQL.
    Schema: {schema_desc}
    Query: {query}
    Return ONLY the SQL statement, no explanation.
    """

    sql_resp = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": sql_prompt}],
        temperature=0,
    )

    sql = sql_resp.choices[0].message.content.strip().strip("```sql").strip("```")

    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    try:
        rows = await conn.fetch(sql)
        return [
            Document(
                content=str(dict(row)),
                source="sql_db",
                score=1.0,
                metadata={"sql": sql},
            )
            for row in rows
        ]
    finally:
        await conn.close()


async def retrieve_from_web(query: str, max_results: int = 5) -> list[Document]:
    """Real-time retrieval via Tavily Search API."""
    results = tavily_client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced",
    )

    return [
        Document(
            content=r.get("content", ""),
            source="web_search",
            score=r.get("score", 0.5),
            metadata={"url": r.get("url"), "title": r.get("title")},
        )
        for r in results.get("results", [])
    ]


RETRIEVER_MAP = {
    DataStore.VECTOR_DB: retrieve_from_vector_db,
    DataStore.SQL_DB: retrieve_from_sql,
    DataStore.WEB_SEARCH: retrieve_from_web,
}


# PARALLEL ROUTE + RETRIEVE
async def route_and_retrieve(queries: list[str]) -> dict[str, list[Document]]:
    """
    Routes each query independently (same single router, parallel calls).
    Then retrieves from the assigned datastore in parallel.
    """

    # Route all queries in parallel
    route_tasks = [route_query(q) for q in queries]
    route_results = await asyncio.gather(*route_tasks)

    print("\n📍 Routing Decisions:")
    for r in route_results:
        print(f"   [{r.datastore.value:12s}] {r.query[:60]}...")

    # Retrieve from each assigned datastore in parallel
    retrieve_tasks = [RETRIEVER_MAP[r.datastore](r.query) for r in route_results]

    retrieved_lists = await asyncio.gather(*retrieve_tasks, return_exceptions=True)

    results = {}
    for route, docs in zip(route_results, retrieved_lists):
        if isinstance(docs, Exception):
            print(f"Retrieval failed for '{route.query}': {docs}")
            results[route.query] = []
        else:
            results[route.query] = docs

    return results


# RECIPROCAL RANK FUSION  (RRF)
def reciprocal_rank_fusion(
    result_lists: list[list[Document]],
    k: int = 60,
    top_n: int = 10,
) -> list[Document]:
    """
    Merges multiple ranked lists into one via RRF scoring.
    RRF(d) = Σ 1 / (k + rank(d))
    Documents appearing in more lists rank higher naturally.
    """
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for result_list in result_lists:
        for rank, doc in enumerate(result_list, start=1):
            key = doc.content[:120]
            scores[key] = scores.get(key, 0) + 1 / (k + rank)
            doc_map[key] = doc

    # Sort by RRF score descending
    ranked_keys = sorted(scores, key=lambda x: scores[x], reverse=True)

    fused = []
    for key in ranked_keys[:top_n]:
        doc = doc_map[key]
        doc.score = scores[key]
        fused.append(doc)

    return fused


def assemble_context(docs: list[Document], token_budget: int = 3000) -> str:
    """
    Builds a structured context string from ranked documents.
    Builds a structured context string from ranked documents.
    """
    char_budget = token_budget * 4
    context_parts = []
    used = 0

    for i, doc in enumerate(docs, start=1):
        entry = (
            f"[SOURCE {i} | {doc.source.upper()} | score={doc.score:.4f}]\n"
            f"{doc.content}\n"
        )
        if used + len(entry) > char_budget:
            break
        context_parts.append(entry)
        used += len(entry)

    return "\n---\n".join(context_parts)


# PROMPT BUILDER
def build_prompt(original_query: str, context: str) -> list[dict]:
    """Constructs the final prompt: System + Context + Original Query."""

    SYSTEM_PROMPT = f"""
    You are a precise and reliable AI assistant.
    Answer the user's question using ONLY the provided context.
    If the context is insufficient, say so clearly.
    Always cite your sources using [SOURCE N] notation.
    """

    user_message = f"""
    Context:
    {context}

    Question: {original_query}
    Answer:
    """

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


async def generate_answer(messages: list[dict]) -> str:
    """Calls the LLM with the fully assembled prompt."""
    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content.strip()


#  MAIN PIPELINE ORCHESTRATOR
async def run_rag_pipeline(user_query: str) -> dict:
    """
    Full pipeline:
    User Query
      → Multi-Query Generator
      → Query Router (per query, parallel)
      → Retriever (per route, parallel)
      → RRF
      → Context Assembler
      → Prompt Builder
      → Answer Generator
      → Final Response
    """

    print(f"\n{'═'*60}")
    print(f"  USER QUERY: {user_query}")
    print(f"{'═'*60}")

    # Generate query variations
    print("\n[1/6]: Generating multi-queries...")
    queries = await generate_multi_queries(user_query, n=3)
    for i, q in enumerate(queries, 1):
        print(f"   Q{i}: {q}")

    # Route each query + retrieve in parallel
    print("\n[2/6]: Routing & retrieving in parallel...")
    retrieval_map = await route_and_retrieve(queries)

    # RRF merge
    print("\n[3/6]: Applying Reciprocal Rank Fusion...")
    all_result_lists = list(retrieval_map.values())
    fused_docs = reciprocal_rank_fusion(all_result_lists, top_n=8)
    print(f"Fused {sum(len(r) for r in all_result_lists)} docs → top {len(fused_docs)}")

    # Assemble context
    print("\n[4/6]: Assembling context...")
    context = assemble_context(fused_docs, token_budget=3000)

    # Build prompt
    print("\n[5/6]: Building prompt...")
    messages = build_prompt(user_query, context)

    # Generate answer
    print("\n[6/6] 🧠 Generating answer...")
    answer = await generate_answer(messages)

    print(f"\n{'═'*60}")
    print("  FINAL RESPONSE")
    print(f"{'═'*60}")
    print(answer)

    return {
        "query": user_query,
        "sub_queries": queries,
        "fused_docs": fused_docs,
        "answer": answer,
    }


if __name__ == "main":
    asyncio.run(run_rag_pipeline("What is the impact of LLMs on the finance industry?"))

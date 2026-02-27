from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from typing import Literal
from langsmith.wrappers import wrap_openai
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

client = wrap_openai(OpenAI())
# client = OpenAI()


# Schemas
class DetectCallResponse(BaseModel):
    is_question_ai: bool


class AICodingResponse(BaseModel):
    answer: str


class AIChatResponse(BaseModel):
    answer: str


class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool


def detect_query(state: State):
    user_message = state["user_message"].lower()

    SYSTEM_PROMPT = f"""
    You are an AI Assistant.
    Your job is to detect if the user query is related to coding question or not.
    Return the response in specified JSON boolean only. 
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=DetectCallResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    print(response.choices[0].message.parsed.is_question_ai)

    state["is_coding_question"] = response.choices[0].message.parsed.is_question_ai
    return state


def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_query"]:
    is_coding_question = state.get("is_coding_question")

    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_query"


def solve_coding_question(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = f"""
    You are an AI Assistant.
    Your job is to resolve the user query based on coding problem he is facing
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=AICodingResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    state["ai_message"] = response.choices[0].message.parsed.answer
    return state


# NOTE: not a coding question
def solve_simple_query(state: State):
    user_message = state.get("user_message")

    SYSTEM_PROMPT = f"""
    You are an AI Assistant.
    Your job is to chat with user in love language 🥰
    """

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        response_format=AICodingResponse,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    state["ai_message"] = response.choices[0].message.parsed.answer
    return state


graph_builder = StateGraph(State)

# Nodes
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_query", solve_simple_query)


# Start
graph_builder.add_edge(START, "detect_query")

# Router
graph_builder.add_conditional_edges(
    "detect_query",
    route_edge,
    {
        "solve_coding_question": "solve_coding_question",
        "solve_simple_query": "solve_simple_query",
    },
)

# End
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_query", END)

graph = graph_builder.compile()


# use
def call_graph():
    initial_state = {
        "user_message": "Hello Ji ?",
        "ai_message": "",
        "is_coding_question": False,
    }
    result = graph.invoke(initial_state)
    print(f"Final result: {result} ")


call_graph()

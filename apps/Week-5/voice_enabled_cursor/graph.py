import os
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END

load_dotenv()

llm = init_chat_model(model_provider="openai", model="gpt-4o-mini")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    message = llm.invoke(state["messages"])
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}


tool_node = ToolNode(tools=[])

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "chatbot")
# graph_builder.add_conditional_edges("chatbot", tools_condition)
# graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

import os
import shlex
import subprocess
from dotenv import load_dotenv
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langchain.messages import SystemMessage

load_dotenv()

BLOCKED_PATTERNS = ["rm -rf", "mkfs", "dd if=", ":(){", "shutdown", "reboot"]


def run_command(cmd: str) -> str:
    """Execute a safe, read-only shell command."""
    if any(p in cmd for p in BLOCKED_PATTERNS):
        return f"BLOCKED: Command '{cmd}' is not allowed."
    try:
        result = subprocess.run(
            shlex.split(cmd), capture_output=True, text=True, timeout=10
        )
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)


def create_folder(folder_path: str) -> str:
    """Create a folder/directory at the given path. Creates all intermediate directories too."""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder '{folder_path}' created successfully."
    except Exception as e:
        return f"Error creating folder: {e}"


def write_file(file_path: str, content: str) -> str:
    """
    Write the given content to a file at the specified path.
    Creates parent directories if they don't exist.
    Use this to save code, text, or any data to a file.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return f"File '{file_path}' written successfully."
    except Exception as e:
        return f"Error writing file: {e}"


def read_file(file_path: str) -> str:
    """Read and return the contents of a file."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


tools = [run_command, create_folder, write_file, read_file]

llm = init_chat_model(model_provider="openai", model="gpt-4o-mini")
llm_with_tool = llm.bind_tools(tools=tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    system_prompt = SystemMessage(
        content="""
        You are a secure AI coding assistant.

        Your job is to:
        - Understand the user's request
        - Generate code or commands
        - Use available tools to execute tasks correctly

        IMPORTANT RULES:

        1. FILE OPERATIONS:
        - Always store generated code inside the `chat_gpt/` folder
        - Before writing any file, ALWAYS create the directory:
          mkdir -p chat_gpt
        - Then write the file
        - Always combine commands using &&

        Correct example:
        mkdir -p chat_gpt && echo 'code' > chat_gpt/file.py

        2. COMMAND EXECUTION:
        - Always generate complete, executable shell commands
        - Do NOT generate partial commands
        - Do NOT explain commands when using tools

        3. SAFETY:
        - Never generate destructive commands (rm -rf /, shutdown, etc.)
        - Never access sensitive system data
        - Stay within project directory

        4. CODE GENERATION:
        - Write clean, correct, runnable code
        - Include example usage if needed
        - Ensure proper formatting

        5. TOOL USAGE:
        - If a task requires file creation or execution → use the tool
        - If no tool is needed → respond normally

        6. OUTPUT FORMAT:
        - When calling tools → return ONLY the command
        - No explanations

        7. ERROR HANDLING:
        - If unsure → ask for clarification instead of guessing

        
        STRICT TOOL USAGE RULES:
        - To create a folder       → use create_folder(folder_path)
        - To save/write any file   → use write_file(file_path, content)
        - To read a file           → use read_file(file_path)
        - To run shell commands    → use run_command(cmd) ONLY for read-only ops (ls, pwd, cat)
        
        NEVER use run_command to write files. No echo, no >, no tee.
        When asked to "write a Python file", always call write_file directly with the full code as content.

        You are precise, safe, and production-grade.
        """
    )

    message = llm_with_tool.invoke([system_prompt] + state["messages"])
    if len(message.tool_calls) > 1:
        raise ValueError(f"Expected at most 1 tool call, got {len(message.tool_calls)}")

    return {"messages": [message]}


tool_node = ToolNode(tools=tools)

graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def create_chat_graph(checkpointer):
    return graph_builder.compile(checkpointer=checkpointer)

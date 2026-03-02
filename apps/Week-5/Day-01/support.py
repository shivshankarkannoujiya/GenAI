# lets admin supports panel
import os
from dotenv import load_dotenv
from graph import create_chat_graph
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.types import Command

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
config = {"configurable": {"thread_id": "3"}}  # thread_id: user_id


def init():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)

        state = graph_with_mongo.get_state(config=config)
        # for message in state.values["messages"]:
        #     message.pretty_print()

        last_message = state.values["messages"][-1]

        user_query = None

        for call in last_message.tool_calls:
            if call["name"] == "human_assistance_tool":
                user_query = call["args"].get("query")
                break

        print("User is Trying to Ask: ", user_query)

        # Admin types a response
        admin_response = input("Admin Response: ")

        # NOTE: Intersting thinks we can do
        # TODO: OpenAI call to mimic the HUMAN -> AI in the Loop

        resume_command = Command(resume={"data": admin_response})

        # again graph ko invoke/stream kr do
        for event in graph_with_mongo.stream(
            resume_command, config=config, stream_mode="values"
        ):
            if "messages" in event:
                event["messages"][-1].pretty_print()


init()

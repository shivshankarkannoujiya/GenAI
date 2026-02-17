import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent


load_dotenv()


model = ChatOpenAI(model="gpt-4o-mini")
search = GoogleSerperAPIWrapper()

agent = create_agent(
    model=model,
    tools=[search.run],
    system_prompt="You are an agent that can serach any query on google",
)

while True:
    user_query = input("Ask: ")
    if user_query.lower() in ["quit", "exit"]:
        print("Good Bye👋🏻")
        break

    if not user_query.strip():
        continue

    response = agent.invoke({"messages": [{"role": "user", "content": user_query}]})
    print("AI:", response["messages"][-1].content)

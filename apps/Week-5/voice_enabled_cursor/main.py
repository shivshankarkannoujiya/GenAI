import os
from dotenv import load_dotenv
import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from graph import create_chat_graph

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
config = {"configurable": {"thread_id": "10"}}


def main():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph = create_chat_graph(checkpointer=checkpointer)

        r = sr.Recognizer()
        r.pause_threshold = 0.8

        try:
            with sr.Microphone() as source:
                print("Adjusting for noise...")
                r.adjust_for_ambient_noise(source, duration=1)

                print("Say something!")

                try:
                    audio = r.listen(source, timeout=5, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    print("You didn't start speaking in time")
                    return

                print("Processing audio...")

                try:
                    sst = r.recognize_google(audio)
                    print("You Said:", sst)

                    for event in graph.stream(
                        {"messages": [{"role": "user", "content": sst}]},
                        config=config,
                        stream_mode="values",
                    ):
                        if "messages" in event:
                            event["messages"][-1].pretty_print()

                except sr.UnknownValueError:
                    print("Sorry, could not understand audio")

                except sr.RequestError as e:
                    print(f"API error: {e}")

        except OSError as e:
            print(f"Microphone not found or not working: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()

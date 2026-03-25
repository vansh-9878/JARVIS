from typing import TypedDict,Annotated,Sequence
from langgraph.graph import START,END,StateGraph
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage,ToolMessage,BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from tools.application import openApp,closeApp,take_screenshot
from tools.search import speed_test,open_website,searchQuery
from tools.songs import play_youtube,pause_youtube
from tools.wordFile import storeFile
from tools.findFile import openFile,openProject
from tools.weather import get_weather
from tools.pcPerformance import monitor_system
from tools.outlookEmail import poll_outlook, draftemail
from tools.notificationsTask import add_to_list, delete_from_list, display_pending_tasks
import threading
from tools.taskNotifier import notify_tasks
from tools.reminder_func import remind_task
import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEYS = [
    os.getenv("GEMINI_API1"),
    os.getenv("GEMINI_API2"),
    os.getenv("GEMINI_API3"),
    os.getenv("GEMINI_API4"),
    os.getenv("GEMINI_API5"),
    os.getenv("GEMINI_API6"),
    os.getenv("GEMINI_API7"),
    os.getenv("GEMINI_API8"),
    os.getenv("GEMINI_API9"),
    os.getenv("GEMINI_API10"),
    os.getenv("GEMINI_API11"),
    os.getenv("GEMINI_API12"),
    os.getenv("GEMINI_API13"),
    os.getenv("GEMINI_API14"),
    os.getenv("GEMINI_API15"),
]

current_key_index = 0

conversation_memory = []

threading.Thread(target=notify_tasks, daemon=True).start()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]

tools=[open_website,searchQuery,speed_test,openApp,closeApp,take_screenshot,play_youtube,pause_youtube,storeFile,openFile,openProject,get_weather,monitor_system,poll_outlook,draftemail, add_to_list, delete_from_list, display_pending_tasks,remind_task]

# model=ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash-lite",
#     google_api_key=os.getenv("GEMINI_API1"),
#     temperature=0.2
# ).bind_tools(tools)

def get_model():
    global current_key_index
    
    key = GEMINI_KEYS[current_key_index]

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=key,
        temperature=0.2,
        max_retries=0
    ).bind_tools(tools)

def agent(state: AgentState) -> AgentState:

    global current_key_index

    print("Thinking..")

    prompt = SystemMessage("""You are an AI assistant that answers to users query while also using the tools whenever required
    - Use tools whenever required
    - If no tool solves the problem , use your intelligence to answer it
    - if you have to give a file path follow this format : D:/{file name}
    - always reply with a message stating whether the tool was successful or not
    - whenever the user says thank you or bye as a closing statement, return 'Bye!'
    - whenever an error occurs while using a tool, catch the error and reply with a message stating that the tool could not be used

    Task management tools:
    - add_to_list(task) → add a task
    - delete_from_list(task) → mark task completed
    - display_pending_tasks() → show pending tasks

    Reminder function:
    - Extract the task as one argument and the time as the other argument and return the task string and only the integer time value(converted to seconds)
    """)

    num_keys = len(GEMINI_KEYS)

    for _ in range(num_keys):

        try:

            print(f"Using API Key #{current_key_index+1}")

            model = get_model()

            response = model.invoke([prompt] + state["messages"])

            return {"messages": [response]}

        except Exception as e:

            error_msg = str(e)

            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"Key #{current_key_index+1} quota exhausted")

            else:
                print(f"Key #{current_key_index+1} failed:", e)

            current_key_index = (current_key_index + 1) % num_keys

            print(f"Switching to Key #{current_key_index+1}\n")

    raise Exception("All Gemini API keys exhausted")

def shouldContinue(state: AgentState)-> AgentState:
    print("Checking..")
    messages=state["messages"]
    last_message=messages[-1]
    # print(last_message.tools_message)
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


graph=StateGraph(AgentState)
graph.add_node("agent",agent)
graph.add_node("tools",ToolNode(tools))
graph.add_edge(START,"agent")
graph.add_edge("tools","agent")
graph.add_conditional_edges(
    "agent",
    shouldContinue,
    {
        "end":END,
        "continue":"tools"
    }
)

app=graph.compile()

def getAgent(inputs):
    global conversation_memory
    
    conversation_memory.append(HumanMessage(content=inputs))
    inp={"messages": conversation_memory}
    results=app.invoke(inp)

    conversation_memory = results['messages']
    conversation_memory = conversation_memory[-10:]
    print("-"*100)
    return results
    
# input="play sapphire"
# input="open spotify"
# input="open a file train which is in pdf format"
input="open my datachatbot project"
# input="create a word file and write a report about the lastest ai trends in the past week in 500 words"

# print(voiceInput())
# print(getAgent("what can you do")["messages"][-1].content)
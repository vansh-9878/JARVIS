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
from tools.findFile import openFile
import os
from dotenv import load_dotenv
load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]

tools=[open_website,searchQuery,speed_test,openApp,closeApp,take_screenshot,play_youtube,pause_youtube,storeFile,openFile]

model=ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GEMINI_API"),
    temperature=0.2
).bind_tools(tools)


def agent(state: AgentState)-> AgentState:
    print("Thinking..")
    prompt=SystemMessage("""You are an AI assistant that answers to users query while also using the tools whenever required
                         - Use tools whenever required
                         - If no tool solves the problem , use your intelligence to answer it
                         - if you have to give a file path follow this format : D:/{file name}
                         - after the tool returns a success or failure message, craft a message based on it or if you want to try any other tool then do that
    """)
    
    response=model.invoke([prompt]+state["messages"])
    return {"messages":[response]}

def shouldContinue(state: AgentState)-> AgentState:
    print("Checking..")
    messages=state["messages"]
    last_message=messages[-1]
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
    results=app.invoke(inputs)
    print("-"*100)
    print(results["messages"][-1])
    print("-"*100)
    
# input="play sapphire"
input="open spotify"
# input="open a file train which is in pdf format"
# input="create a word file and write a report about the lastest ai trends in the past week in 500 words"

getAgent({"messages":input})


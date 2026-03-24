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
import os
from dotenv import load_dotenv
load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage],add_messages]

tools=[open_website,searchQuery,speed_test,openApp,closeApp,take_screenshot,play_youtube,pause_youtube,storeFile,openFile,openProject,get_weather,monitor_system]

model=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv("GEMINI_API"),
    temperature=0.2
).bind_tools(tools)

def agent(state: AgentState)-> AgentState:
    # inp=input("\nUser : ")
    print("Thinking..")
    prompt=SystemMessage("""You are an AI assistant that answers to users query while also using the tools whenever required
                         - Use tools whenever required
                         - If no tool solves the problem , use your intelligence to answer it
                         - if you have to give a file path follow this format : D:/{file name}
                         - always reply with a message stating whether the tool was successful or not
                         - whenever the user says thank you or bye as a closing statement, return 'Bye!'
                         - whenever an error occurs while using a tool, catch the error and reply with a message stating that the tool could not be used
    """)
    
    response=model.invoke([prompt]+state["messages"])
    # print(response.content)
    return {"messages":[response]}

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
    inp={"messages":[HumanMessage(content=inputs)]}
    results=app.invoke(inp)
    print("-"*100)
    return results
    
# input="play sapphire"
# input="open spotify"
# input="open a file train which is in pdf format"
input="open my datachatbot project"
# input="create a word file and write a report about the lastest ai trends in the past week in 500 words"

# print(voiceInput())
# print(getAgent("what can you do")["messages"][-1].content)
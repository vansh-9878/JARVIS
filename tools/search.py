import webbrowser
from langchain_core.tools import tool

@tool
def open_website(url:str)->str:
    """opens any website, url should be provided as parameter in https format"""
    try:
        print(f"Opening website : {url}")
        webbrowser.open(url)
        return "opened successfully"
    except:
        return "could not open the website"
     
@tool
def searchQuery(query:str)->str:
    """Searches the query on google"""
    try:
        query = query.replace(" ", "+")
        print(f"🔍 Searching Google for: {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return "search successful"
    except:
        return "could not search on google"
   
@tool
def speed_test()->str:
    """Opens a website which tells the speed of the internet (speed test)"""
    try:
        webbrowser.open("https://fast.com/")      
        return "success"
    except:
        return "could not open fast.com"
# open_website("virat kohli")
# speed_test()
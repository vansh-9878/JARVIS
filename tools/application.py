import os,pyautogui
from langchain_core.tools import tool

@tool
def openApp(app:str)->str:
    """Opens any application installed in the local machine"""
    try:
        os.startfile(app)
        print("opening app!")
        return "app successfully opened"
    except:
        return "Application not found in the local machine, try opening its website"


@tool
def closeApp(app_name:str)->str:
    """Used to close any application on the local machine"""
    try:
        os.system(f"taskkill /f /im {app_name}.exe")
        return "closed successfully"
    except:
        return "application already closed"
    
@tool
def take_screenshot(filename:str)->str:
    """Used to take screenshot"""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        return f"screenshot saved with the name {filename}"
    except:
        return "could not take screenshot"
    
    
# closeApp("spotify")
# take_screenshot("test.jpg")
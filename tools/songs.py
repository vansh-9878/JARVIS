# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
import os
import time,pyautogui
from langchain_core.tools import tool
from dotenv import load_dotenv
import pywhatkit as kit
load_dotenv()

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=os.getenv("CLIENT_ID"),
#     client_secret=os.getenv("CLIENT_SECRET"),
#     redirect_uri="http://127.0.0.1:8000/callback",
#     scope="user-modify-playback-state,user-read-playback-state"
# ))

# def play():
#     sp.start_playback()

# def pause():
#     sp.pause_playback()

# def next_track():
#     sp.next_track()

# def previous_track():
#     sp.previous_track()


# play()


@tool
def play_youtube(name:str)->str:
    """Plays any video or song on youtube"""
    try:
        print(f"Playing: {name}")
        kit.playonyt(name)
        time.sleep(5) 
        pyautogui.press('space')
        return f"Playing {name}"
    except:
        return "could not open youtube"
    
@tool
def pause_youtube()->str:
    """Used to pause the video playing on youtube"""
    # pyautogui.click()
    pyautogui.press("space")
    return "paused"

# play_youtube("ind vs eng 1st test highlights from england cricket channel")
# play_youtube("zindagi tu aana song")
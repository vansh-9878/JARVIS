import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
from agent import getAgent
import speech_recognition as sr
import pyttsx3

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    
def voiceInput() -> str:
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = rec.listen(source)
    try:
        query = rec.recognize_google(audio)
        return query
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Could not request results.")
        return ""

def append_chat(text, sender="User"):
    chat_window.configure(state='normal')
    chat_window.insert(tk.END, f"{sender}: {text}\n")
    chat_window.configure(state='disabled')
    chat_window.see(tk.END)

def run_agent(query=None):
    if not query:
        query = voiceInput()
    query = query.strip()
    if query == "":
        # append_chat("No input detected.", sender="System")
        return

    append_chat(query, sender="User")

    try:
        messages = getAgent(query)
        ai_response = messages["messages"][-1].content
    except Exception as e:
        ai_response = f"Error: {str(e)}"

    append_chat(ai_response, sender="AI")
    speak(ai_response)

def handle_text_input():
    query = user_input.get()
    user_input.delete(0, tk.END)
    Thread(target=run_agent, args=(query,)).start()

def handle_voice_input():
    Thread(target=run_agent).start()

# Create main window
root = tk.Tk()
root.title("Assistant")
root.geometry("700x800")

# Chat history window
chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', font=("Arial", 12))
chat_window.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Input field
user_input = tk.Entry(root, font=("Arial", 14))
user_input.pack(padx=10, pady=10, fill=tk.X)
user_input.bind("<Return>", lambda event: handle_text_input())

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

text_button = tk.Button(button_frame, text="Send", command=handle_text_input, font=("Arial", 12), width=10)
text_button.pack(side=tk.LEFT, padx=5)

voice_button = tk.Button(button_frame, text="🎤 Speak", command=handle_voice_input, font=("Arial", 12), width=10)
voice_button.pack(side=tk.LEFT, padx=5)

# Start the app
root.mainloop()

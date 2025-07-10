# 🤖 Jarvis - AI Desktop Assistant

Jarvis is a smart desktop assistant capable of performing various automation and productivity tasks using both **voice** and **text** input. It features a minimal GUI built with Tkinter and integrates speech recognition and text-to-speech for a hands-free experience.

## 🚀 Features

Jarvis supports a wide range of smart capabilities:

- 🎵 **Play YouTube Songs/Videos** — Voice-controlled YouTube playback  
- 🔍 **Search on Google** — Smart web searching using natural language  
- 🌐 **Open Any Website** — Just say or type the site you want  
- 🖥️ **Launch Applications** — Open installed apps (e.g., Spotify, VS Code, etc.)  
- 📸 **Take Screenshots** — Capture your screen instantly  
- 📁 **Find Files in D Drive** — Locate and open files using natural language  
- 📝 **Create Word Files** — Generate reports or notes directly from voice or text  
- 💻 **Open Project in VS Code** — Seamless dev workflow support  

## 🖼️ GUI Interface

- Built using **Tkinter**
- Supports **both text and speech input**
- Displays assistant responses
- Click the mic button 🎤 to speak, or type directly

## 🧠 Tech Stack

- **LangGraph** – Orchestrates conversational flow with tool support  
- **LangChain** – Tool binding and message management  
- **Google Gemini API** – LLM backend (via `langchain_google_genai`)  
- **SpeechRecognition** – For capturing voice input  
- **Pyttsx3** – Text-to-speech voice output  
- **Tkinter** – GUI for interaction  
- **Python 3.9+**

## 🛠️ Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/jarvis-assistant.git
   cd jarvis-assistant
   ```
2. **Install Dependencies**
   
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**

   Create a .env file with your Google Gemini API key:  
   ```bash
   GEMINI_API=your_google_gemini_api_key
   ```
5. **Run the Assistant**

   ```bash
   python ui.py
   ```

## 🧑‍💻 Author

Made by Vansh

Feel free to contribute, suggest improvements, or fork!
   

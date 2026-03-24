import os
import speech_recognition as sr
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
load_dotenv()

SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

def speak(text, rate="+15%"):
    try:
        cfg = speechsdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
        cfg.speech_synthesis_voice_name = "en-US-CoraMultilingualNeural"
        synth = speechsdk.SpeechSynthesizer(speech_config=cfg)

        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
            <voice name='en-US-CoraMultilingualNeural'>
                <prosody rate='{rate}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        result = synth.speak_ssml_async(ssml).get()
        if result.reason == speechsdk.ResultReason.Canceled:
            print(f"TTS canceled: {result.cancellation_details.reason}")
    except Exception as e:
        print(f"TTS error: {e}")
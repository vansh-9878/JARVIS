import threading
import re
from plyer import notification
from pushbullet import Pushbullet
import os
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

PB_ACCESS_TOKEN = os.getenv("PB_TOKEN")
pb = Pushbullet(PB_ACCESS_TOKEN)


def parse_time(text):

    text = text.lower()

    match = re.search(r'(\d+)\s*(second|seconds|sec|s|minute|minutes|min|mins|hour|hours)', text)

    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2)

    if unit in ["second","seconds","sec","s"]:
        return value
    elif unit in ["minute","minutes","min","mins"]:
        return value * 60
    elif unit in ["hour","hours"]:
        return value * 3600


def extract_task(text):

    text = text.lower()

    match = re.search(r"reminder to (.+?) in", text)

    if match:
        return match.group(1)

    return text


@tool
def remind_task(command: str):
    """Sets a reminder from a natural language command"""

    delay = parse_time(command)
    task = extract_task(command)

    print("Task:", task)
    print("Delay:", delay)

    def send_reminder():

        notification.notify(
            title="Task Reminder",
            message=task,
            timeout=10
        )

        pb.push_note("Task Reminder", task)

    timer = threading.Timer(delay, send_reminder)
    timer.daemon = True
    timer.start()

    return f"Reminder set for '{task}' in {delay} seconds."
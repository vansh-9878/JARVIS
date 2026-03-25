import time
from plyer import notification
from .notificationsTask import task_list
from pushbullet import Pushbullet
import os
from dotenv import load_dotenv
load_dotenv()

PB_ACCESS_TOKEN = os.getenv('PB_TOKEN')
pb = Pushbullet(PB_ACCESS_TOKEN)

def get_pending_tasks():
    return [t["task"] for t in task_list if not t["done"]]


def notify_tasks():
    while True:
        pending = get_pending_tasks()

        if pending:
            message = "\n".join(pending)

            notification.notify(
                title="Pending Tasks",
                message=message,
                timeout=10
            )

            pb.push_note("Pending Tasks", message)

        time.sleep(20)
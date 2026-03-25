import win32com.client 
import pythoncom
from win32com.client import gencache
from langchain_core.tools import tool
from tools.application import openApp

@tool
def poll_outlook()->list:
    """Poll through the inbox of ms outlook and returns the details of emails in the inbox"""   
    inboxemails=[]
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)
    print(f"Polling Outlook Inbox. Total items found: {len(messages)}")

    for msg in messages:
        try:
            email_data = {
                "subject": msg.Subject,
                "sender": msg.SenderName,
                "body": msg.Body,
                "received": msg.ReceivedTime
            }
            inboxemails.append(email_data)
        except:
            continue
    return inboxemails

@tool
def draftemail(receiveremail:str, subject:str, body:str)->str:
    """Creates a draft email in Outlook"""
    outlook = gencache.EnsureDispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = receiveremail
    mail.Subject = subject
    mail.Body = body
    mail.Save()
    logstatement = openApp("Outlook")

    return f"Draft email created for {receiveremail} with subject '{subject}'"

if __name__ == "__main__":
    res = draftemail.invoke({
        "receiveremail": "venugopalcoldcoffee@gmail.com",
        "subject": "Test Email",
        "body": "Hello, this is a test draft created using Python."
    })

    print(res)
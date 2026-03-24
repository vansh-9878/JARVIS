import psutil
import time
import os
from langchain_core.tools import tool

@tool
def monitor_system():
    print("--- System Performance Monitor ---")

    cpu_percent = psutil.cpu_percent(interval=1.0)
    print(f"Current CPU Usage: {cpu_percent}%")
    print(f"Logical CPU Cores: {psutil.cpu_count(logical=True)}")
    print(f"Physical CPU Cores: {psutil.cpu_count(logical=False)}")

    memory = psutil.virtual_memory()
    print("\n--- Memory Details ---")
    print(f"Total Memory: {memory.total / (1024**3):.2f} GB")
    print(f"Used Memory: {memory.used / (1024**3):.2f} GB")
    print(f"Available Memory: {memory.available / (1024**3):.2f} GB")
    print(f"Memory Usage Percentage: {memory.percent}%")

    disk = psutil.disk_usage('/')
    print("\n--- Disk Details (C:\\) ---")
    print(f"Total Disk Space: {disk.total / (1024**3):.2f} GB")
    print(f"Used Disk Space: {disk.used / (1024**3):.2f} GB")
    print(f"Free Disk Space: {disk.free / (1024**3):.2f} GB")
    print(f"Disk Usage Percentage: {disk.percent}%")

    processes_count = len(list(psutil.process_iter()))
    print(f"\nTotal Running Processes: {processes_count}")
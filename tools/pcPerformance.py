import psutil
from langchain_core.tools import tool

@tool
def monitor_system()->dict:
    """This tool analyses the performance of the pc (cpu, memory, disk usage)"""
    print("Analyzing system performance...")
    cpu_percent = psutil.cpu_percent(interval=1.0)
    print(f"CPU Usage: {cpu_percent}%")
    memory = psutil.virtual_memory()
    
    print(f"Memory Usage: {memory.percent}%")
    disk = psutil.disk_usage('/')

    processes_count = len(list(psutil.process_iter()))

    system_data = {
        "cpu_usage_percent": cpu_percent,
        "logical_cpu_cores": psutil.cpu_count(logical=True),
        "physical_cpu_cores": psutil.cpu_count(logical=False),

        "memory_total_gb": round(memory.total / (1024**3), 2),
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_available_gb": round(memory.available / (1024**3), 2),
        "memory_percent": memory.percent,

        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_used_gb": round(disk.used / (1024**3), 2),
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_percent": disk.percent,

        "running_processes": processes_count
    }

    return system_data


if __name__ == "__main__":
    res = monitor_system.invoke({})
    print(res)
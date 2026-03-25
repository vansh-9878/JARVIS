from langchain_core.tools import tool

task_list = []

@tool
def add_to_list(task: str) -> list:
    """Add the task specified to the task list"""
    task_list.append({"task": task, "done": False})
    return task_list


@tool
def delete_from_list(task: str) -> str:
    """Mark a task as completed"""
    for t in task_list:
        if t["task"] == task:
            t["done"] = True
            return f"{task} marked as completed"

    return f"{task} does not exist in the list"


@tool
def display_pending_tasks() -> str:
    """Display all pending tasks"""

    pending = [t["task"] for t in task_list if not t["done"]]

    if not pending:
        return "No pending tasks"

    return "\n".join(pending)
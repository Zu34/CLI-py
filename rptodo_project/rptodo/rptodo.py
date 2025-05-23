"""This module provides the RP To-Do model-controller."""

from pathlib import Path
from typing import Any, Dict, List, Tuple

from rptodo import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, ID_ERROR
from rptodo.database import DatabaseHandler

# You can pass the DB path when calling these functions
def add_task(db_path: Path, task: str) -> Tuple[int, str]:
    """Add a task to the database."""
    db_handler = DatabaseHandler(db_path)

    # Read existing todos
    response = db_handler.read_todos()
    if response.error != SUCCESS:
        return response.error, "Failed to read the database."

    todos = response.todo_list

    # Create new todo item with new ID
    new_id = 1 if not todos else max(t.get("id", 0) for t in todos) + 1
    new_todo = {"id": new_id, "task": task, "done": False}
    todos.append(new_todo)

    # Write updated todos back to DB
    write_error = db_handler.write_todos(todos)
    if write_error != SUCCESS:
        return write_error, "Failed to write to the database."

    return SUCCESS, f'Task "{task}" added successfully!'


def remove_task(db_path: Path, task_id: int) -> Tuple[int, str]:
    """Remove a task from the database."""
    db_handler = DatabaseHandler(db_path)

    # Read existing todos
    response = db_handler.read_todos()
    if response.error != SUCCESS:
        return response.error, "Failed to read the database."

    todos = response.todo_list
    filtered_todos = [t for t in todos if t.get("id") != task_id]

    if len(todos) == len(filtered_todos):
        return ID_ERROR, f"Task with ID {task_id} not found."

    # Write updated todos back to DB
    write_error = db_handler.write_todos(filtered_todos)
    if write_error != SUCCESS:
        return write_error, "Failed to write to the database."

    return SUCCESS, f"Task with ID {task_id} removed successfully!"

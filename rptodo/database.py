"""This module provides the RP To-Do database functionality."""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from rptodo import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, ID_ERROR


def read_todos(db_path: Path) -> List[Dict[str, Any]]:
    """Read the to-do list from the JSON database."""
    try:
        if not db_path.exists():
            return []
        with db_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        # You might want to log the error here in real apps
        raise Exception(DB_READ_ERROR)


def write_todos(db_path: Path, todos: List[Dict[str, Any]]) -> int:
    """Write the to-do list to the JSON database."""
    try:
        with db_path.open("w", encoding="utf-8") as f:
            json.dump(todos, f, indent=4)
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR


def get_new_id(todos: List[Dict[str, Any]]) -> int:
    """Generate a new ID for a to-do item."""
    if not todos:
        return 1
    max_id = max(todo.get("id", 0) for todo in todos)
    return max_id + 1


def add_todo(db_path: Path, task: str) -> int:
    try:
        todos = read_todos(db_path)
    except Exception:
        return DB_READ_ERROR

    new_id = get_new_id(todos)
    todo = {"id": new_id, "task": task, "done": False}  # Add 'done'
    todos.append(todo)
    return write_todos(db_path, todos)



def remove_todo(db_path: Path, todo_id: int) -> int:
    """Remove a to-do item by id."""
    try:
        todos = read_todos(db_path)
    except Exception:
        return DB_READ_ERROR

    filtered_todos = [t for t in todos if t.get("id") != todo_id]

    if len(todos) == len(filtered_todos):
        # No item was removed because ID was not found
        return ID_ERROR

    return write_todos(db_path, filtered_todos)


def list_todos(db_path: Path) -> Optional[List[Dict[str, Any]]]:
    """Return the list of to-dos, or None on error."""
    try:
        return read_todos(db_path)
    except Exception:
        return None

class DatabaseHandler:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read(self) -> List[Dict[str, Any]]:
        return read_todos(self._db_path)

    def write(self, todos: List[Dict[str, Any]]) -> int:
        return write_todos(self._db_path, todos)

    def add(self, task: str) -> int:
        return add_todo(self._db_path, task)

    def remove(self, todo_id: int) -> int:
        return remove_todo(self._db_path, todo_id)

    def list(self) -> Optional[List[Dict[str, Any]]]:
        return list_todos(self._db_path)
def set_done_status(db_path: Path, todo_id: int, done: bool) -> int:
    try:
        todos = read_todos(db_path)
    except Exception:
        return DB_READ_ERROR

    updated = False
    for todo in todos:
        if todo.get("id") == todo_id:
            todo["done"] = done
            updated = True
            break

    if not updated:
        return ID_ERROR

    return write_todos(db_path, todos)
def edit_todo(db_path: Path, todo_id: int, new_task: str) -> int:
    try:
        todos = read_todos(db_path)
    except Exception:
        return DB_READ_ERROR

    edited = False
    for todo in todos:
        if todo.get("id") == todo_id:
            todo["task"] = new_task
            edited = True
            break

    if not edited:
        return ID_ERROR

    return write_todos(db_path, todos)

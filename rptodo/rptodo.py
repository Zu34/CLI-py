"""This module provides the RP To-Do model-controller."""

# rptodo/rptodo.py

from typing import Any, Dict, List, Tuple

def add_task(task: str) -> Tuple[int, str]:
    """Add a task to the database (placeholder)."""
    # For now, just return a success message
    return 0, f'Task "{task}" added successfully!'


def remove_task(task_id: int) -> Tuple[int, str]:
    """Remove a task from the database (placeholder)."""
    # For now, just return a success message
    return 0, f"Task with ID {task_id} removed successfully!"

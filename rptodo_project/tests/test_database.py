import tempfile
from pathlib import Path
from rptodo import database, ERRORS, SUCCESS

def test_add_todo_creates_task():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "todo_db.json"
        # Initialize empty database or do any setup if required
        database.init_database(db_path)
        
        # Add a task
        result = database.add_todo(db_path, "Test task")

        assert result == SUCCESS

        # Check if the task was really added
        todos = database.list_todos(db_path)
        assert len(todos) == 1
        assert todos[0]["task"] == "Test task"

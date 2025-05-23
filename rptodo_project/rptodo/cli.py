from pathlib import Path
from typing import Optional
import typer
import json
import csv
from rptodo import ERRORS, __app_name__, __version__, config, database

from rptodo.config import init_app
from rptodo.database import get_database_path
from rptodo.rptodo import add_task, remove_task
app = typer.Typer()

def get_db_path() -> Path:
    config_path = config.CONFIG_FILE_PATH
    return database.get_database_path(config_path)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    pass

@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db-path",
        "-db",
        prompt="to-do database location?",
    ),
) -> None:
    """Initialize the to-do database."""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f'Creating config file failed with "{ERRORS[app_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f'Creating database failed with "{ERRORS[db_init_error]}"',
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    
    typer.secho(f"The to-do database is {db_path}", fg=typer.colors.GREEN)


@app.command()
def add(task: str = typer.Argument(..., help="Task description")):
    """Add a new to-do task."""
    db_path = get_db_path()
    code, message = add_task(db_path, task)
    if code != 0:
        typer.secho(f"Failed to add task: {ERRORS.get(code, 'Unknown error')}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(message, fg=typer.colors.GREEN)

@app.command()
def remove(todo_id: int = typer.Argument(..., help="ID of the to-do to remove")):
    """Remove a to-do task by its ID."""
    db_path = get_db_path()
    code, message = remove_task(db_path, todo_id)
    if code != 0:
        typer.secho(f"Failed to remove task: {ERRORS.get(code, 'Unknown error')}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(message, fg=typer.colors.GREEN)

@app.command()
def list():
    """List all to-do tasks."""
    db_path = get_db_path()
    todos = database.list_todos(db_path)
    if todos is None:
        typer.secho(f"Failed to read tasks.", fg=typer.colors.RED)
        raise typer.Exit(1)
    if not todos:
        typer.echo("No tasks found.")
        return
    for todo in todos:
        typer.echo(f"{todo['id']}: {todo['task']}")

@app.command()
def done(todo_id: int = typer.Argument(..., help="ID of the task to mark as done")):
    """Mark a task as done."""
    db_path = get_db_path()
    result = database.set_done_status(db_path, todo_id, True)
    if result != 0:
        typer.secho(f"Error: {ERRORS.get(result, 'Unknown error')}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Task {todo_id} marked as done.", fg=typer.colors.GREEN)


@app.command()
def undone(todo_id: int = typer.Argument(..., help="ID of the task to mark as not done")):
    """Mark a task as not done."""
    db_path = get_db_path()
    result = database.set_done_status(db_path, todo_id, False)
    if result != 0:
        typer.secho(f"Error: {ERRORS.get(result, 'Unknown error')}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Task {todo_id} marked as not done.", fg=typer.colors.GREEN)
@app.command()
def edit(
    todo_id: int = typer.Argument(..., help="ID of the task to edit"),
    new_task: str = typer.Argument(..., help="New description for the task")
):
    """Edit a task description."""
    db_path = get_db_path()
    result = database.edit_todo(db_path, todo_id, new_task)
    if result != 0:
        typer.secho(f"Error: {ERRORS.get(result, 'Unknown error')}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"Task {todo_id} updated.", fg=typer.colors.GREEN)
@app.command()
def list():
    """List all to-do tasks with status."""
    db_path = get_db_path()
    todos = database.list_todos(db_path)

    if todos is None:
        typer.secho("Failed to read tasks.", fg=typer.colors.RED)
        raise typer.Exit(1)

    if not todos:
        typer.echo("No tasks found.")
        return

    for todo in todos:
        status = "[✔]" if todo.get("done") else "[ ]"
        typer.echo(f"{status} {todo['id']}: {todo['task']}")
@app.command("export-all")
@app.command("export-all")
def export_all(
    output_path: Path = typer.Argument(..., help="Path to save the to-do list export"),
    format: str = typer.Option("txt", "--format", "-f", help="Export format: txt, json, or csv"),
):
    """Export all to-do tasks to a file in TXT, JSON, or CSV format."""
    db_path = get_db_path()
    todos = database.list_todos(db_path)

    if todos is None:
        typer.secho("Failed to read tasks.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        format = format.lower()
        with output_path.open("w", encoding="utf-8", newline="") as f:
            if format == "txt":
                for todo in todos:
                    status = "✔" if todo.get("done") else "✗"
                    f.write(f"[{status}] {todo['id']}: {todo['task']}\n")
            elif format == "json":
                json.dump(todos, f, indent=4)
            elif format == "csv":
                import csv
                writer = csv.DictWriter(f, fieldnames=["id", "task", "done"])
                writer.writeheader()
                for todo in todos:
                    writer.writerow({
                        "id": todo.get("id"),
                        "task": todo.get("task"),
                        "done": todo.get("done", False)
                    })
            else:
                typer.secho("Unsupported format. Use txt, json, or csv.", fg=typer.colors.RED)
                raise typer.Exit(1)

        typer.secho(f"Tasks exported to {output_path}", fg=typer.colors.GREEN)

    except OSError:
        typer.secho("Failed to write to file.", fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command("export-task")
def export_task(
    todo_id: int = typer.Argument(..., help="ID of the to-do to export"),
    output_path: Path = typer.Argument(..., help="File to write the to-do task to"),
    format: str = typer.Option("txt", "--format", "-f", help="Export format: txt, json, or csv"),
):
    """Export a single to-do task to a file in TXT, JSON, or CSV format."""
    db_path = get_db_path()
    todos = database.list_todos(db_path)

    if todos is None:
        typer.secho("Failed to read tasks.", fg=typer.colors.RED)
        raise typer.Exit(1)

    todo = next((t for t in todos if t.get("id") == todo_id), None)

    if not todo:
        typer.secho(f"No task found with ID {todo_id}.", fg=typer.colors.RED)
        raise typer.Exit(1)

    try:
        format = format.lower()
        with output_path.open("w", encoding="utf-8", newline="") as f:
            if format == "txt":
                status = "✔" if todo.get("done") else "✗"
                f.write(f"[{status}] {todo['id']}: {todo['task']}\n")
            elif format == "json":
                json.dump(todo, f, indent=4)
            elif format == "csv":
                import csv
                writer = csv.DictWriter(f, fieldnames=["id", "task", "done"])
                writer.writeheader()
                writer.writerow({
                    "id": todo.get("id"),
                    "task": todo.get("task"),
                    "done": todo.get("done", False)
                })
            else:
                typer.secho("Unsupported format. Use txt, json, or csv.", fg=typer.colors.RED)
                raise typer.Exit(1)

        typer.secho(f"Task {todo_id} exported to {output_path}", fg=typer.colors.GREEN)

    except OSError:
        typer.secho("Failed to write to file.", fg=typer.colors.RED)
        raise typer.Exit(1)
@app.command()
def export(
    export_path: str = typer.Argument(..., help="Path to export the to-do list"),
    format: str = typer.Option("json", help="Export format: json or csv"),
):
    """Export the to-do list to a JSON or CSV file."""
    db_path = get_db_path()
    todos = database.list_todos(db_path)

    if todos is None:
        typer.secho("Failed to read tasks.", fg=typer.colors.RED)
        raise typer.Exit(1)

    export_path_obj = Path(export_path)

    if format.lower() == "json":
        try:
            with export_path_obj.open("w", encoding="utf-8") as f:
                json.dump(todos, f, indent=4)
            typer.secho(f"Tasks exported to {export_path} as JSON.", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Failed to export tasks: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)

    elif format.lower() == "csv":
        try:
            with export_path_obj.open("w", newline='', encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["id", "task"])
                writer.writeheader()
                writer.writerows(todos)
            typer.secho(f"Tasks exported to {export_path} as CSV.", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"Failed to export tasks: {e}", fg=typer.colors.RED)
            raise typer.Exit(1)

    else:
        typer.secho("Unsupported format. Please use 'json' or 'csv'.", fg=typer.colors.RED)
        raise typer.Exit(1)


from typer.testing import CliRunner
from rptodo.cli import app  
runner = CliRunner()

def test_add_cli():
    result = runner.invoke(app, ["add", "Test task from CLI"])
    assert result.exit_code == 0
    assert 'Task added: "Test task from CLI"' in result.output

def test_list_cli():
    # Add a task first (or mock your DB)
    runner.invoke(app, ["add", "Task 1"])
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "Task 1" in result.output

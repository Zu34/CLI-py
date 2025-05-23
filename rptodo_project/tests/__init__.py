# test/int.py

import pytest
from typer.testing import CliRunner
from rptodo.cli import app 

runner = CliRunner()

def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "rptodo v" in result.output.lower()

def test_add_task():
    result = runner.invoke(app, ["add", "Write tests"])
    assert result.exit_code == 0
    assert 'Task added: "Write tests"' in result.output

def test_list_tasks():
    # Assuming the db is initially empty or you handle a test db
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    # Could be "No tasks found." or a list depending on setup

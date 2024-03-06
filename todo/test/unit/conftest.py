import pytest
from click.testing import CliRunner
from datetime import date
from to_do_list.models import Task

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def tasks():
    return [
            Task(id=1, task_description="Buy milk", task_date=date.fromisoformat("2024-02-01"), done=False, important=False),
            Task(id=2, task_description="Buy bread", task_date=date.fromisoformat("2024-02-01"), done=True, important=False),
            Task(id=3, task_description="Clean the house", task_date=date.fromisoformat("2024-02-01"), done=False, important=True)
        ]
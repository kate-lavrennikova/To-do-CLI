import pytest
from pytest_mock import mocker
from unittest.mock import patch
from to_do_list.cli import show, add, update, delete
from to_do_list.service import UserService, TaskService
from to_do_list.models import Task
from datetime import date, timedelta
from to_do_list.exceptions import SessionHasExpiredException, UserAlreadyExistsExeption, UserNotLoggedInException


class TestShowCommand:
    def test_show_command_displays_tasks(self, mocker, cli_runner):
        tasks = [
            Task(id=1, task_description="Buy milk", task_date=date.fromisoformat("2024-02-01"), done=False, important=False),
            Task(id=2, task_description="Buy bread", task_date=date.fromisoformat("2024-02-01"), done=True, important=False),
            Task(id=3, task_description="Clean the house", task_date=date.fromisoformat("2024-02-01"), done=False, important=True)
        ]
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.get_filtered", return_value=tasks)
        result = cli_runner.invoke(show)
        assert result.exit_code == 0
        assert """2024-02-01  1  \u2610  Buy milk   \n2024-02-01  2  \u2611  Buy bread   \n2024-02-01  3  \u2610  Clean the house  \u22C6\n""" == result.output

    def test_show_command_does_not_displays_tasks(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.get_filtered", return_value=[])
        result = cli_runner.invoke(show, ['--day', '2024-02-01', '--done', '--not-important'])
        kwargs = {"task_date": date.fromisoformat('2024-02-01'), "user_id": 1, "done": True, "important": False}
        TaskService.get_filtered.assert_called_once_with(**kwargs)
        assert result.exit_code == 0
        assert "No tasks found for 2024-02-01\n" == result.output

    def test_show_command_when_session_has_expired(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.TaskService.get_filtered", return_value=[])
        with patch('to_do_list.service.UserService.get_current_user', side_effect=SessionHasExpiredException):
            result = cli_runner.invoke(show)
            TaskService.get_filtered.assert_not_called()
            assert result.output == SessionHasExpiredException().message + "\n"
            assert result.exit_code == 0

    def test_show_command_when_user_is_not_logged_in(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.TaskService.get_filtered", return_value=[])
        with patch('to_do_list.service.UserService.get_current_user', side_effect=UserNotLoggedInException):
            result = cli_runner.invoke(show)
            TaskService.get_filtered.assert_not_called()
            assert result.output == UserNotLoggedInException().message + "\n"
            assert result.exit_code == 0


class TestAddCommand:
    def test_add_command_creates_task(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.create")
        task = Task(task_description="Buy milk", task_date=date.today(), done=False, important=True, user_id=1)
        result = cli_runner.invoke(add, ["Buy milk", "--important"])
        TaskService.create.assert_called_once_with(task)
        assert result.exit_code == 0

    def test_add_command_does_not_create_task_with_long_description(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user")
        mocker.patch("to_do_list.service.TaskService.create")
        result = cli_runner.invoke(add, ["A"*151])
        TaskService.create.assert_not_called()
        UserService.get_current_user.assert_not_called()
        assert result.exit_code == 0
        assert result.output == "Too long task. It should contain no more than 150 symbols.\n"

    def test_add_command_when_session_has_expired(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.TaskService.create")
        with patch('to_do_list.service.UserService.get_current_user', side_effect=SessionHasExpiredException):
            result = cli_runner.invoke(add, ["Buy milk"])
            TaskService.create.assert_not_called()
            assert result.output == SessionHasExpiredException().message + "\n"
            assert result.exit_code == 0

    def test_add_command_when_user_is_not_logged_in(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.TaskService.create")
        with patch('to_do_list.service.UserService.get_current_user', side_effect=UserNotLoggedInException):
            result = cli_runner.invoke(add, ["Buy milk"])
            TaskService.create.assert_not_called()
            assert result.output == UserNotLoggedInException().message + "\n"
            assert result.exit_code == 0

class TestUpdateCommand:
    def test_update_command_updates_task(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.update")
        result = cli_runner.invoke(update, ["today", "1", "--desc", "Buy bread", "--important"])
        kwargs = {"important": True, "description": "Buy bread"}
        TaskService.update.assert_called_once_with(date.today(), 1, 1, **kwargs)
        assert result.exit_code == 0

    def test_update_command_does_not_update_task_due_to_lack_of_info(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.update")
        result = cli_runner.invoke(update, ["today", "1"])
        UserService.get_current_user.assert_not_called()
        TaskService.update.assert_not_called()
        assert result.output == "Define at least one parameter to change\n"
        assert result.exit_code == 0

    def test_update_command_does_not_update_task_with_long_description(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user")
        mocker.patch("to_do_list.service.TaskService.update")
        result = cli_runner.invoke(update, ["today", "1", "--desc", "A"*151])
        TaskService.update.assert_not_called()
        UserService.get_current_user.assert_not_called()
        assert result.exit_code == 0
        assert result.output == "Too long description. It should contain no more than 150 symbols.\n"

class TestDeleteCommand:
    def test_delete_command_deletes_task(self, mocker, cli_runner):
        mocker.patch("to_do_list.service.UserService.get_current_user", return_value=1)
        mocker.patch("to_do_list.service.TaskService.delete")
        result = cli_runner.invoke(delete, ["tomorrow", "3"])
        TaskService.delete.assert_called_once_with(date.today() + timedelta(days=+1), 3, 1)
        assert result.exit_code == 0

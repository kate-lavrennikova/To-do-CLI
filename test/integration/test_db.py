import pytest
from to_do_list.database import Base, engine
from to_do_list.config import settings
from to_do_list.exceptions import UserNotLoggedInException


class TestUserService:
    def test_create_user(self, user_service, users):
        for user in users:
            user_service.create(user)
        users_from_db = user_service.get_all()
        assert len(users) == len(users_from_db)

    def test_login_successful(self, user_service, users):
        user = users[0]
        assert user_service.login(user.user_name, user.user_password) == True
        assert user_service.get_current_user() != None

    def test_login_failed(self, user_service, users):
        user = users[0]
        user.user_password = user.user_password + "1"
        assert user_service.login(user.user_name, user.user_password) == False

    def test_logout(self, user_service):
        user_service.logout()
        with pytest.raises(UserNotLoggedInException) as e:
            user_service.get_current_user()
        assert str(e.value) == "Please login to get an access to your tasks"

@pytest.mark.usefixtures("add_users_to_db")
class TestTaskService:

    def test_create_task(self, task_service, tasks):
        for task in tasks:
            task_service.create(task)
        
        tasks_from_db = task_service.get_tasks()
        assert len(tasks) == len(tasks_from_db)

    def test_get_tasks(self, task_service):
        kwargs = {"user_id": 1, "done": False}
        tasks_from_db = task_service.get_tasks(**kwargs)
        assert len(tasks_from_db) == 2
        for task in tasks_from_db:
            assert task.user_id == 1 and task.done == False
    
    def test_update_task(self, task_service, tasks):
        task = tasks[0]
        kwargs = {"task_description": task.task_description + "!"}
        task_service.update(task.task_date, 1, task.user_id, **kwargs)
        assert len(task_service.get_tasks()) == len(tasks)
        assert len(task_service.get_tasks(task_description=task.task_description + "!", user_id=task.user_id)) == 1
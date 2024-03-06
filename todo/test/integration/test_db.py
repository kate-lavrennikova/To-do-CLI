import pytest
from to_do_list.exceptions import UserNotLoggedInException
from to_do_list.database import Session

@pytest.mark.usefixtures("empty_users")
class TestUserService:
    def test_create_user(self, user_service, user, session):
        user_service.create(session, user)
        session.commit()
        user_from_db = user_service.get_user(session, user.user_name, user.user_password)
        assert user.user_name == user_from_db.user_name
        assert user.user_password == user_from_db.user_password

    def test_login_successful(self, user_service, user, session):
        user_service.create(session, user)
        session.commit()
        assert user_service.login(session, user.user_name, user.user_password) == True
        assert user_service.get_current_user(session) != None

    def test_login_failed(self, user_service, user, session):
        user_service.create(session, user)
        session.commit()
        assert user_service.login(session, user.user_name, user.user_password + "1") == False

    def test_logout(self, user_service, session):
        user_service.logout(session)
        session.commit()
        with pytest.raises(UserNotLoggedInException) as e:
            user_service.get_current_user(session)
        assert str(e.value) == "Please log in to get an access to your tasks"

@pytest.mark.usefixtures("not_empty_users")
@pytest.mark.usefixtures("empty_tasks")
class TestTaskService:

    def test_create_task(self, task_service, tasks, session):
        for task in tasks:
            task_service.create(session, task)
        session.commit()
        tasks_from_db = task_service.get_tasks(session)
        assert len(tasks) == len(tasks_from_db)

    def test_get_tasks(self, task_service, tasks, session):
        for task in tasks:
            task_service.create(session, task)
        session.commit()
        kwargs = {"user_id": 1, "done": False}
        tasks_from_db = task_service.get_tasks(session, **kwargs)
        assert len(tasks_from_db) == 2
        for task in tasks_from_db:
            assert task.user_id == 1 and task.done == False
    
    def test_update_task(self, task_service, tasks, session):
        for task in tasks:
            task_service.create(session, task)
        session.commit()
        task = tasks[0]
        kwargs = {"task_description": task.task_description + "!"}
        task_service.update(session, task.task_date, 1, task.user_id, **kwargs)
        session.commit()
        assert len(task_service.get_tasks(session)) == len(tasks)
        assert len(task_service.get_tasks(session, task_description=task.task_description, user_id=task.user_id)) == 1


    def test_delete_task(self, task_service, tasks, session):
        for task in tasks:
            task_service.create(session, task)
        session.commit()
        task = tasks[0]
        task_service.delete(session, task.task_date, 1, task.user_id)
        session.commit()
        assert len(task_service.get_tasks(session)) == len(tasks) - 1
        assert len(task_service.get_tasks(session, task_description=task.task_description, user_id=task.user_id)) == 0
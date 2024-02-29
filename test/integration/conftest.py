import pytest
from to_do_list.database import Base, engine
from to_do_list.config import settings
from to_do_list.models import User, Task
from datetime import date, timedelta
from to_do_list.repository import TaskRepository, UserRepository, SessionRepository
from to_do_list.service import TaskService, UserService

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    assert settings.MODE == "TEST"
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    

@pytest.fixture
def tasks():
    return [
        Task(task_description="Buy milk", task_date=date.today(), done=True, important=False, user_id=1),
        Task(task_description="Buy bread", task_date=date.today(), done=False, important=False, user_id=1),
        Task(task_description="Finish report", task_date=date.today() + timedelta(days=+1), done=False, important=True, user_id=1),
        Task(task_description="Go to the dentist", task_date=date.today() + timedelta(days=-1), done=False, important=True, user_id=2),
        Task(task_description="Go to gym", task_date=date.today(), done=True, important=True, user_id=2)
    ]

@pytest.fixture
def users():
    return [
        User(user_name="Jack", user_password="12345"),
        User(user_name="Lana", user_password="aaaaa"),
        User(user_name="Peter", user_password="zxcvb")
    ]

@pytest.fixture
def task_service():
    return TaskService(TaskRepository())

@pytest.fixture
def user_service():
    return UserService(UserRepository(), SessionRepository())

@pytest.fixture()
def add_users_to_db(user_service, users):
    if len(user_service.get_all()) == 0:
        for user in users:
            user_service.create(user)


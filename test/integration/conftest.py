import pytest
from to_do_list.database import Base, engine
from to_do_list.config import settings
from to_do_list.models import User, Task
from datetime import date, timedelta
from to_do_list.repository import TaskRepository, UserRepository, SessionRepository
from to_do_list.service import TaskService, UserService
from to_do_list.database import Session

@pytest.fixture(scope="session", autouse=True)
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

@pytest.fixture(scope="session")
def users():
    return [
        User(user_name="Jack", user_password="12345"),
        User(user_name="Lana", user_password="aaaaa"),
        User(user_name="Peter", user_password="zxcvb")
    ]

@pytest.fixture(scope="session")
def user():
    return User(user_name="Jack", user_password="12345")

@pytest.fixture(scope="session")
def task_service():
    return TaskService(TaskRepository())

@pytest.fixture(scope="session")
def user_service():
    return UserService(UserRepository(), SessionRepository())

@pytest.fixture(scope="class")
def not_empty_users(user_service, users, session):
    user_service.delete_all(session)
    for user in users:
        user_service.create(session, user)
    session.commit()


@pytest.fixture(scope="class")
def session():
    with Session() as session:
        yield session

@pytest.fixture
def empty_users(user_service, session):
    user_service.logout(session)
    session.flush()
    user_service.delete_all(session)

@pytest.fixture
def empty_tasks(task_service, session):
    task_service.delete_all(session)

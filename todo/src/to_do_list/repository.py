from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.exc import NoResultFound
from datetime import datetime
from .models import Task, User, UserSession
from .exceptions import TaskNotFoundException


class TaskRepository:
    def get_tasks(self, session, **kwargs):
        t = aliased(Task)
        query = select(
            t.task_description,
            t.task_date,
            t.done,
            t.important,
            t.user_id,
            func.rank().over(order_by=t.timestamp).label("id")
        ).select_from(t).filter_by(**kwargs)
        result = []
        for row in session.execute(query).all():
            result.append(Task(**row._asdict()))
        return result
        

    def create(self, session, task):
        session.add(task)


    def update(self, session, date, fake_id, user_id, **kwargs):
        try:
            query = select(Task).filter_by(task_date=date, user_id=user_id).order_by(Task.timestamp).offset(fake_id - 1).limit(1)
            task = session.execute(query).scalar_one()
            for k, v in kwargs.items():
                if k == "task_date":
                    task.timestamp = datetime.now()
                setattr(task, k, v)
            # session.commit()
        except NoResultFound:
            raise TaskNotFoundException(fake_id, date)


    def delete(self, session, date, fake_id, user_id):
        try:
            query = select(Task).filter_by(task_date=date, user_id=user_id).order_by(Task.timestamp).offset(fake_id - 1).limit(1)
            task = session.execute(query).scalar_one()
            session.delete(task)
        except NoResultFound:
            raise TaskNotFoundException(fake_id, date)
        
    def delete_all(self, session):
        session.execute(Task.__table__.delete())



class UserRepository:
    def get_all(self, session):
        return session.execute(select(User)).scalars().all()


    def create(self, session, user):
        session.add(user)


    def get_by_username_and_password(self, session, username, password):
        query = select(User).filter_by(user_name=username, user_password=password)
        return session.execute(query).scalar()
        
    def update(self, session, **kwargs):
        query = select(User).filter_by(**kwargs)
        user = session.execute(query).scalar()
        for k, v in kwargs.items():
            setattr(user, k, v)

    def delete_all(self, session):
        session.execute(User.__table__.delete())    
        

class SessionRepository:
    def create(self, session, user_id):
        user_session = UserSession(user_id=user_id, last_updated=datetime.now())
        session.add(user_session)

    def get_current_session(self, session):
        return session.execute(select(UserSession)).scalar()

    def delete(self, session):
        user_session = self.get_current_session(session)
        if user_session != None:
            session.delete(user_session)
            
    def update(self, session, id):
        user_session = session.get(UserSession, id)
        user_session.last_updated = datetime.now()


from sqlalchemy import select, update
from to_do_list.database import session_factory
from to_do_list.models import Task, User, UserSession
from datetime import datetime

class TaskRepository:
    def get_filtered(self, **kwargs):
        with session_factory() as session:
            query = select(Task).filter_by(**kwargs)
            return session.execute(query).scalars().all()

    
    def get_by_id(self, id):
        pass

    def create(self, task):
        with session_factory() as session:
            session.add(task)
            session.commit()

    def update(self, id, **kwargs):
        with session_factory() as session:
            task = session.get(Task, id)
            for k, v in kwargs.items():
                setattr(task, k, v)
            session.commit()


    def delete(self, id):
        with session_factory() as session:
            task = session.get(Task, id)
            session.delete(task)
            session.commit()



class UserRepository:
    def create(self, user):
        with session_factory() as session:
            session.add(user)
            session.commit()

    def get_by_username_and_password(self, username, password):
        with session_factory() as session:
            query = select(User.id).filter_by(user_name=username, user_password=password)
            return session.execute(query).scalar()
        

class SessionRepository:
    def create(self, user_id):
        with session_factory() as session:
            user_session = UserSession(user_id=user_id, last_updated=datetime.now())
            session.add(user_session)
            session.commit()

    def delete(self):
        with session_factory() as session:
            query = select(UserSession)
            user_session = session.execute(query).first()
            if user_session != None:
                session.delete(user_session.tuple()[0])
                session.commit()

    def get(self):
         with session_factory() as session:
            return session.execute(select(UserSession)).scalar_one()
         
    def update(self, id):
        with session_factory() as session:
            user_session = session.get(UserSession, id)
            user_session.last_updated = datetime.now()
            session.commit()
            
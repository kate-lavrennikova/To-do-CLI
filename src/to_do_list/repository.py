from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from sqlalchemy.exc import IntegrityError, NoResultFound
from to_do_list.database import session_factory
from to_do_list.models import Task, User, UserSession
from datetime import datetime, timedelta
from to_do_list.exceptions import SessionHasExpiredException, UserAlreadyExistsExeption, UserNotLoggedInException


class TaskRepository:
    def get_filtered(self, **kwargs):
        with session_factory() as session:
            t = aliased(Task)
            query = select(
                t.task_description,
                t.task_date,
                t.done,
                t.important,
                func.rank().over(order_by=t.timestamp).label("id")
            ).select_from(t).filter_by(**kwargs)
            result = []
            for row in session.execute(query).all():
                result.append(Task(**row._asdict()))
            return result
        

    def create(self, task):
        with session_factory() as session:
            session.add(task)
            session.commit()


    def update(self, date, fake_id, user_id, **kwargs):
        with session_factory() as session:
            query = select(Task).filter_by(task_date=date, user_id=user_id).order_by(Task.timestamp).offset(fake_id - 1).limit(1)
            task = session.execute(query).scalar()
            for k, v in kwargs.items():
                if k == "task_date":
                    task.timestamp = datetime.now()
                setattr(task, k, v)
            session.commit()


    def delete(self, date, fake_id, user_id):
        with session_factory() as session:
            query = select(Task).filter_by(task_date=date, user_id=user_id).order_by(Task.timestamp).offset(fake_id - 1).limit(1)
            task = session.execute(query).scalar()
            session.delete(task)
            session.commit()



class UserRepository:
    def create(self, user):
        try:
            with session_factory() as session:
                session.add(user)
                session.commit()
        except IntegrityError:
            raise UserAlreadyExistsExeption(user.user_name)

    def get_by_username_and_password(self, username, password):
        with session_factory() as session:
            query = select(User.id).filter_by(user_name=username, user_password=password)
            return session.execute(query).scalar()
        
    def update(self, **kwargs):
        with session_factory() as session:
            query = select(User).filter_by(**kwargs)
            user = session.execute(query).scalar()
            for k, v in kwargs.items():
                setattr(user, k, v)
            session.commit()
            
        

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

    def get_current_session(self):
         with session_factory() as session:
            try:
                user_session = session.execute(select(UserSession)).scalar_one()
            except NoResultFound:
                raise UserNotLoggedInException
            if (user_session.last_updated + timedelta(hours=+1) <= datetime.now()):
                session.delete(user_session)
                session.commit()
                raise SessionHasExpiredException
            return user_session
                
         
    def update(self, id):
        with session_factory() as session:
            user_session = session.get(UserSession, id)
            user_session.last_updated = datetime.now()
            session.commit()

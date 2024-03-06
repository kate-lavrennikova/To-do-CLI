from datetime import datetime, timedelta
from .exceptions import UserNotLoggedInException, SessionHasExpiredException

class UserService:

    def __init__(self, user_repository, session_repository):
        self.user_repository = user_repository
        self.session_repository = session_repository
 
    def create(self, session, user):
         self.user_repository.create(session, user)

    def update(self, session, **kwargs):
        self.user_repository.update(session, **kwargs)

    def get_user(self, session, username, password):
        return self.user_repository.get_by_username_and_password(session, username, password)
  
    def login(self, session, username, password):
        user = self.get_user(session, username, password)
        if user != None:
            self.session_repository.delete(session)
            self.session_repository.create(session, user.id)
        return user != None
    
    def logout(self, session):
        self.session_repository.delete(session)

    def get_current_user(self, session):
        user_session = self.session_repository.get_current_session(session)
        if user_session == None:
            raise UserNotLoggedInException()
        if (user_session.last_updated + timedelta(hours=+1) <= datetime.now()):
            raise SessionHasExpiredException() 
        return user_session.user_id
    
    def get_all(self, session):
        return self.user_repository.get_all(session)
    
    def delete_all(self, session):
        self.user_repository.delete_all(session)


class TaskService:

    def __init__(self, repository):
        self.repository = repository

    def create(self, session, task):
        self.repository.create(session, task)

    def delete(self, session, date, fake_id, user_id):
        self.repository.delete(session, date, fake_id, user_id)

    def update(self, session, date, fake_id, user_id, **kwargs):
        self.repository.update(session, date, fake_id, user_id, **kwargs)

    def get_tasks(self, session, **kwargs):
        return self.repository.get_tasks(session, **kwargs)
    
    def delete_all(self, session):
        return self.repository.delete_all(session)
    

    

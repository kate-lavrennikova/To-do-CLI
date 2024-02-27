from datetime import datetime, timedelta


class TaskService:

    def __init__(self, repository):
        self.repository = repository

    def create(self, task):
        self.repository.create(task)

    def delete(self, date, fake_id, user_id):
        self.repository.delete(date, fake_id, user_id)

    def update(self, date, fake_id, user_id, **kwargs):
        self.repository.update(date, fake_id, user_id, **kwargs)

    def get_filtered(self, **kwargs):
        return self.repository.get_filtered(**kwargs)
    

class UserService:

    def __init__(self, user_repository, session_repository):
        self.user_repository = user_repository
        self.session_repository = session_repository

    def create(self, user):
         self.user_repository.create(user)

    def update(self, **kwargs):
        self.user_repository.update(**kwargs)
  
    def login(self, username, password):
        user_id = self.user_repository.get_by_username_and_password(username, password)
        if user_id != None:
            self.session_repository.delete()
            self.session_repository.create(user_id)
        return user_id != None
    
    def logout(self):
        self.session_repository.delete()

    def get_current_user(self):
        user_session = self.session_repository.get_current_session()
        return user_session.user_id
    
    


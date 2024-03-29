class SessionHasExpiredException(Exception):
    def __init__(self):
        self.message = f"Your session has expired. Login again please."
        super().__init__(self.message)

class UserAlreadyExistsExeption(Exception):
    def __init__(self, username):
        self.message = f"User {username!r} already exists"
        super().__init__(self.message)

class UserNotLoggedInException(Exception):
    def __init__(self):
        self.message = f"Please log in to get an access to your tasks"
        super().__init__(self.message)

class DatabaseIsNotInitializedException(Exception):
    def __init__(self):
        self.message = f"Please initialize database first. Use command 'todo init'"
        super().__init__(self.message)

class DatabaseIsNotAvailableException(Exception):
    def __init__(self):
        self.message = f"Lost connection with database"
        super().__init__(self.message)

class TaskNotFoundException(Exception):
    def __init__(self, id, date):
        self.message = f"Task №{id} for {date} not found"
        super().__init__(self.message)
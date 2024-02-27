class SessionHasExpiredException(Exception):
    def __init__(self):
        self.message = f"Session has expired. Login again please."
        super().__init__(self.message)

class UserAlreadyExistsExeption(Exception):
    def __init__(self, username):
        self.message = f"User {username!r} already exists"
        super().__init__(self.message)

class UserNotLoggedInException(Exception):
    def __init__(self):
        self.message = f"Please login to get an access to your tasks"
        super().__init__(self.message)
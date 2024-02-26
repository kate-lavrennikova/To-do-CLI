class SessionHasExpiredException(Exception):
    def __init__(self):
        self.message = f"Session has expired. Login again please."
        super().__init__(self.message)
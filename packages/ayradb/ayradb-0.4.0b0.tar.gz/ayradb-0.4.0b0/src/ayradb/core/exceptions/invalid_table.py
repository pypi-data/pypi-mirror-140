class InvalidTableName(BaseException):
    def __init__(self, m):
        self.message = m
    def __str__(self):
        return self.message
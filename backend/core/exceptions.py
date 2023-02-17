class BaseError(Exception):
    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code
        super(BaseError, self).__init__(msg)


class ServerError(BaseError):
    pass


class UserError(BaseError):
    pass


class UnknownError(ServerError):
    pass

class BaseError(Exception):
    pass


class UnknownError(BaseError):
    pass


class InvalidLogin(BaseError):
    pass


class WrongParameter(BaseError):
    pass


class InvalidURL(BaseError):
    pass

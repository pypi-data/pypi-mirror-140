# coding=utf-8


class PostResultFailedError(Exception):
    pass


class NewConnectionError(Exception):
    pass


class MaxRetryError(Exception):
    pass


class ConnectTimeoutError(Exception):
    pass


class InvalidInputError(Exception):
    pass

class APIError(Exception):
    pass


class DirtyProjectError(Exception):
    pass

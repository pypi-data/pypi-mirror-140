class fdict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __or__(self, incoming):
        # assert isinstance(incoming, self.__class__)
        # for arg in args:
        # assert isinstance(arg, self.__class__)
        self.update(incoming)
        return self


class fstr(str):
    def __init__(self, obj):
        self.__str__ = obj
        super().__init__()

    def removesuffix(self, suffix):

        if len(self) < len(suffix):
            return self
        else:
            if self[-len(suffix) :] == suffix:
                return self[: -len(suffix)]
            else:
                return self

    def removeprefix(self, prefix: str):
        if len(self) < len(prefix):
            return self
        else:
            if self[: len(prefix)] == prefix:
                return self[len(prefix) :]
            else:
                return self


def __or__(self, incoming, **args):
    assert isinstance(incoming, dict)
    for arg in args:
        assert isinstance(arg, dict)

    self.update(incoming)
    for arg in args:
        self.update(incoming)


def removeprefix(self: str, prefix: str):
    assert isinstance(prefix, str)
    if len(self) < len(prefix):
        return self
    else:
        if self[: len(prefix)] == prefix:
            return self[len(prefix) :]
        else:
            return self


def removesuffix(self: str, suffix: str):
    assert isinstance(suffix, str)
    if len(self) < len(suffix):
        return self
    else:
        if self[-len(suffix) :] == suffix:
            return self[: -len(suffix)]
        else:
            return self



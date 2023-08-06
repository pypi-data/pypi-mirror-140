class BaseSearchContainer:
    @property
    def names(self):
        return list(map(lambda _: _["name"], list(self.all())))
    
    @property
    def ids(self):
        return list(map(lambda _: _["id"], list(self.all())))
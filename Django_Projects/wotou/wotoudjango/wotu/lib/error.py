class CookiesError(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value


class NetworkDisConnect(Exception):
    def __init__(self, value):
        Exception.__init__(self)
        self.value = value

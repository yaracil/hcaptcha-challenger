class BaseSettings:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)


class SettingsConfigDict(dict):
    pass

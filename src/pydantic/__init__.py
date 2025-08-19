class BaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

    @classmethod
    def model_validate_json(cls, data: bytes):
        import json
        return cls(**json.loads(data.decode()))

    def model_dump(self, mode: str = "json"):
        return self.__dict__

    def json(self):
        import json
        return json.dumps(self.__dict__)


def Field(default=None, default_factory=None, **kwargs):
    if default_factory is not None:
        return default_factory()
    return default


class SecretStr(str):
    def get_secret_value(self) -> str:
        return str(self)


def field_validator(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

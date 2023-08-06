import requests
from .serializers import LogSerializer


class Logger(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    # TODO: Convert scheme to Enum
    def __init__(self, scheme: str, url: str, port: str, log_name: str) -> None:
        # TODO: Check if this violates the singleton pattern. I should not be
        #       able to reconfigure the logger after it has been created.
        self.scheme = scheme
        self.url = url
        self.port = port
        self.log_name = log_name
        self.is_valid()

    def log_to_remote(self, data: dict, log_type: str) -> None:
        '''
        Sends logs to remote server
        '''
        # TODO: Restrict log_types

        log = LogSerializer(data=data)
        requests.post(
            url=f"{self.scheme}://{self.url}:{self.port}/{self.log_name}.{log_type}",
            json=log.get_data()
        )

    def is_valid(self):
        # TODO: implement validator
        pass

    def log_to_file() -> None:
        raise NotImplementedError

class FlaskLogger(Logger):
    pass


class FastApiLogger(Logger):
    pass

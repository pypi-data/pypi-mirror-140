import traceback
from typing import Any
from time import time

from .loggers import Logger
from .serializers import LogSerializer

def log_to_remote(logger: Logger) -> Any:
    '''
    Takes a function as argument, executes the function in a try catch block and
    logs the exception in remote server if raise any or the function throws any.

    Also logs the successful function execution with execution time.
    '''
    def decorator(function):
        def wrapper(*args, **kwargs):
            result = None

            try:
                start_time = time()
                result = function(*args, **kwargs)
                execution_time = time() - start_time
                logger.log_to_remote(
                    LogSerializer(
                        execution_status=True,
                        message=f"Successfully executed function: `{function.__name__}`",
                        execution_time=execution_time,
                    )
                )
            except Exception as _exn:
                logger.log_to_remote(
                    LogSerializer(
                        execution_status=False,
                        message=f"Error during the execution of {function.__name__}",
                        traceback=traceback.format_exc(),
                    )
                )

            return result
        return wrapper
    return decorator

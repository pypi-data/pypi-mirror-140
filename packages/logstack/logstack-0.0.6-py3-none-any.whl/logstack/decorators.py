import traceback
from typing import Any
from time import time

from .loggers import Logger

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
                data = {
                    'message': 'Successfully executed',
                    'function_name': function.__name__,
                    'execution_time': execution_time,
                }
                logger.log_to_remote(data=data, log_type='info')
            except Exception as _exn:
                data = {
                    'message': 'Error during the execution',
                    'function_name': function.__name__,
                    'traceback': traceback.format_exc(),
                }
                logger.log_to_remote(data=data, log_type='error')

            return result
        return wrapper
    return decorator

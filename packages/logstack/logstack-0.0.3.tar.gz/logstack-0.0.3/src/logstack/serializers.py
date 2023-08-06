class LogSerializer():
    data = dict()

    def __init__(
        self,
        execution_status: bool = False,
        message: str = "No message",
        execution_time: float = 0.0,
    ):
        # TODO: Add data validation.
        # TODO: Add log level?
        # TODO: Add additional data serializer for sending any additional information as a JSON serializable dict.
        self.data['execution_status'] = execution_status
        self.data['execution_time'] = execution_time
        self.data['message'] = message
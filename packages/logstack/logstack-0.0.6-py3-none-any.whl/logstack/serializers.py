import json
from typing import Any

class LogSerializer():
    FIELDS_CONFIG = {
        'execution_time': {'required': False, 'type': float, 'default': None},
        'message': {'required': True, 'type': str},
        'traceback': {'required': False, 'type': str, 'default': None},
        'function_name': {'required': False, 'type': str, 'default': None},
        'extra': {'required': False, 'type': dict, 'default': None}
    }

    def __init__(self, data: dict):
        self.initial_data = data
        self.data = dict()
        self.is_valid()

    def is_valid(self):
        '''
        Runs validation of required and non-required fields
        '''
        self._validate_required_values()
        self._extract_extra_data()

    def _validate_required_values(self) -> None:
        '''
        Validates if all the fields are present as FIELDS_CONFIG.
        then sets the fields as instance fields
        '''
        for key, value in self.FIELDS_CONFIG.items():
            field_value_in_data = self.initial_data.get(key)
            if value.get('required') and not field_value_in_data:
                raise AttributeError(f"`{key}` is required but not provided in data")
            elif not value.get('required') and not field_value_in_data:
                self.data[key] = value.get('default')
            elif field_value_in_data:
                self.__validate_types(value.get('type'), key, field_value_in_data)

    def __validate_types(
        self,
        expected_type: object,
        field_name: str,
        field_value: Any
    ):
        '''
        Validates if the field types and the provided data types are identical
        Paramterers:
            expected_type:
        '''
        field_type = type(field_value)
        if not expected_type == field_type:
            raise TypeError(f"Expected {expected_type} but got {field_type}")
        self.data[field_name] = field_value


    def _extract_extra_data(self) -> None:
        '''
        Takes data from 'extra' dict and sets each key as instance field and
        values as instance value
        '''
        if self.data.get('extra'):
            for key, value in self.data.get('extra').items():
                self.data[key] = value
        else:
            self.data.pop('extra')

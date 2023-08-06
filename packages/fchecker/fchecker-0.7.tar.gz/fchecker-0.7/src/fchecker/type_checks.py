# Built-in/Generic Imports
from typing import Union

# Exceptions
from fexception import (FAttributeError,
                        FTypeError)

__author__ = 'IncognitoCoding'
__copyright__ = 'Copyright 2022, type_check'
__credits__ = ['IncognitoCoding']
__license__ = 'MIT'
__version__ = '0.0.7'
__maintainer__ = 'IncognitoCoding'
__status__ = 'Beta'


def type_check(value: any, required_type: Union[type, list],
               tb_remove_name: str = None, msg_override: str = None) -> None:
    """
    A simple type validation check. This function is designed to be widely used to check any values.

    Raises a cleanly formatted reason if the type validation is unsuccessful.

    No return output.

    Args:
        value (any):
        \t\\- Any value needing its type validated.\\
        required_type (Union[type, list]):
        \t\\- The required type the value should match.\\
        \t\\- Can be a single type or list of types.
        tb_remove_name (str, optional):\\
        \t\\- Caller function name or any other function in the\\
        \t   traceback chain.\\
        \t\\- Removes all traceback before and at this function.\\
        \t\\- Defaults to None.
        msg_override (str, optional):
        \t\\- Main top-level message override.\\
        \t\\- The expected and returned results will be the same.\\
        \t\\- Ideal for type checks for other importing files such as YAML.\\
        \t\\- Defaults to None.

    Raises:
        FAttributeError (fexception):
        \t\\- The value \'{value}\' sent is not an accepted input.
        FAttributeError (fexception):
        \t\\- No type or list of types has been entered for type validation.
        FTypeError (fexception):
        \t\\- The value \'{value}\' is not in {required_type} format.
    """
    # Verifies a value is sent.
    if (
        value is None
        or value == ''
    ):
        exc_args: dict = {
            'main_message': f'The value \'{value}\' sent is not an accepted input.',
            'expected_result': 'Any value other than None or an empty string',
            'returned_result': type(value)
        }
        if not tb_remove_name:
            tb_remove_name = 'type_check'
        raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

    # Verifies a type or list is sent.
    if (
        not (isinstance(required_type, list) or isinstance(required_type, type))
    ):
        exc_args: dict = {
            'main_message': 'No type or list of types has been entered for type validation.',
            'expected_result': 'type or list of types',
            'returned_result': type(required_type)
        }
        if not tb_remove_name:
            tb_remove_name = 'type_check'
        raise FAttributeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

    matching_type_flag: bool = None
    # Checks if the required type option one type or multiple.
    if isinstance(required_type, list):
        for value_type in required_type:
            if isinstance(value, value_type):
                matching_type_flag = True
                break
            else:
                matching_type_flag = False
    else:
        if not isinstance(value, required_type):
            matching_type_flag = False
        else:
            matching_type_flag = True

    # Checks for no match.
    if matching_type_flag is False:
        # Sets message override if one is provided.
        if msg_override:
            main_message: str = msg_override
        else:
            main_message: str = f'The value \'{value}\' is not in {required_type} format.'

        exc_args: dict = {
            'main_message': main_message,
            'expected_result': required_type,
            'returned_result': type(value)
        }
        if not tb_remove_name:
            tb_remove_name = 'type_check'
        raise FTypeError(message_args=exc_args, tb_limit=None, tb_remove_name=tb_remove_name)

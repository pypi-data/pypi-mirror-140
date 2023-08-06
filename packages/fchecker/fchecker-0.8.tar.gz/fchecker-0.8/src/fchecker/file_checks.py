# Built-in/Generic Imports
import pathlib
from typing import Optional

# Local Functions
from .type_checks import type_check

# Exceptions
from fexception import FFileNotFoundError


__author__ = 'IncognitoCoding'
__copyright__ = 'Copyright 2022, file_checks'
__credits__ = ['IncognitoCoding']
__license__ = 'MIT'
__version__ = '0.0.7'
__maintainer__ = 'IncognitoCoding'
__status__ = 'Beta'


def file_check(file_path: str, file_description: Optional[str] = None) -> None:
    """
    Checks if the file exists.

    Raises a cleanly formatted reason if the key validation is unsuccessful.

    No return output.

    Args:
        file_path (str):
        \t\\- The file path being checked.
        file_description (str, optional):
        \t\\- Name of the file being checked.\\
        \t\\- Defaults to None.

    Raises:
        FFileNotFoundError (fexception):
        \t\\- The file ({file_description}) does not exist in the validating file path ({file_path}).
        FFileNotFoundError (fexception):
        \t\\- The file does not exist in the validating file path ({file_path}).
    """
    type_check(value=file_path, required_type=str, tb_remove_name='file_checks')
    if file_description:
        type_check(value=file_description, required_type=str, tb_remove_name='file_checks')

    # Checks if the file does not exist
    file: pathlib.Path = pathlib.Path(file_path)
    if not file.exists():
        # Sets message based on description choice.
        if file_description:
            exc_args: dict = {
                'main_message': f'The file ({file_description}) does not exist '
                                f'in the validating file path ({file_path}).',
                'suggested_resolution': 'Ensure the file path is the correct path to your file.'
            }
        else:
            exc_args: dict = {
                'main_message': f'The file does not exist in the validating file path ({file_path}).',
                'suggested_resolution': 'Ensure the file path is the correct path to your file.'
            }
        raise FFileNotFoundError(message_args=exc_args, tb_limit=None, tb_remove_name='file_check')

import inspect
from inspect import currentframe
from typing import Union, Optional
from typing import Optional
from pathlib import Path

from .common import (InputFailure,
                     CallerOverrideFailure)


__author__ = 'IncognitoCoding'
__copyright__ = 'Copyright 2022, util'
__credits__ = ['IncognitoCoding']
__license__ = 'MIT'
__version__ = '0.3.10'
__maintainer__ = 'IncognitoCoding'
__status__ = 'Beta'


class InvalidKeyError(Exception):
    """
    Exception raised for an invalid dictionary key.

    Built in KeyErrors do not format cleanly.

    Attributes:
        error_message: The invalid key reason.
    """
    __module__ = 'builtins'
    pass


def get_line_number() -> int:  # pragma: no cover
    """Returns the calling function's line number."""
    cf = currentframe()
    return cf.f_back.f_lineno


def set_caller_override(tb_remove_name: str) -> dict:
    """
    Sets the caller override dictionary values.

    Usage:
    \t\\- tb_remove_name is designed for local override setting based\\
    \t   on a matching function in the currentframe\\

    Args:
        tb_remove_name (str):
        \t\\- The name caller function\\
        \t\\- The tb_remove_name name will be used to determine the\\
        \t   correct f_back line to set.

    Raises:
        InputFailure::
        \t\\- The value \'{tb_remove_name}\' is not in {type(tb_remove_name)} format.
        InputFailure:
        \t\\- Incorrect caller_override keys.
        CallerOverrideFailure:
        \t\\- The function or method name did not match any co_name in the inspect.currentframe().

    Return:
        dict:
        \t\\- The caller override dictionary values.
    """
    if tb_remove_name:
        if not isinstance(tb_remove_name, str):
            error_message = (
                f'Invalid tb_remove_name type. The value \'{tb_remove_name}\' is not in {type(tb_remove_name)} format.\n'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Expected Result:\n'
                f'  - <class \'str\'>\n\n'
                + 'Returned Result:\n'
                f'  - {type(tb_remove_name)}\n\n'
                + 'Suggested Resolution:\n'
                f'  - Check the calling fexception Exception class arguments.\n'
                + (('-' * 150) + '\n') * 2
            )
            raise InputFailure(error_message)

    f_backs: list = []
    co_names: list = []
    tracker: int = 1
    # Loops until a fun or method name matches a currentframe co_name.
    while True:
        if tracker == 1:
            f_backs.append('f_back')
        else:
            f_backs.append('.f_back')

        # tries until a match occurs or no f_backs causes and exception during the eval.
        try:
            joined_f_backs: str = ''.join(f_backs)
            co_name: str = eval(f'inspect.currentframe().{joined_f_backs}.f_code.co_name')
            # Adds to the list in case an exception occurs.
            co_names.append(co_name)
            # Checks if the tb_remove_name (func or method name) matches the f_back co_name.
            if tb_remove_name == co_name:
                # Adds the next traceback entry after the tb_removal.
                f_backs.append('.f_back')
                joined_f_backs: str = ''.join(f_backs)
                # Final eval check to make sure an entry exists.
                co_name: str = eval(f'inspect.currentframe().{joined_f_backs}.f_code.co_name')
                break

            tracker += 1
        except Exception:
            joined_co_names: str = ', '.join(co_names)
            error_message = (
                'The function or method name did not match any co_name in the inspect.currentframe().\n'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Expected Result:\n'
                f'  - \'{tb_remove_name}\' matching co_name\n\n'
                + 'Returned Result:\n'
                '  - No Match\n'
                f'  - co_names = {joined_co_names}\n\n'
                + f'Trace Details:\n'
                f'  - Exception: AttributeError\n'
                f'  - Module: {Path(inspect.currentframe().f_back.f_back.f_back.f_code.co_filename).stem}\n'
                f'  - Name: {inspect.currentframe().f_back.f_back.f_back.f_code.co_name}\n'
                f'  - Line: {inspect.currentframe().f_back.f_back.f_back.f_lineno}\n'
                + (('-' * 150) + '\n') * 2
            )
            raise CallerOverrideFailure(error_message)

    # Runs eval on the commands to pull the output based on the f_backs.
    caller_override = {
        'module': eval(f'Path(inspect.currentframe().{joined_f_backs}.f_code.co_filename).stem'),
        'name': eval(f'inspect.currentframe().{joined_f_backs}.f_code.co_name'),
        'line': eval(f'inspect.currentframe().{joined_f_backs}.f_lineno'),
        'tb_remove': tb_remove_name
    }

    return caller_override


class KeyCheck():
    """
    An advanced dictionary key checker that offers two different check options.

    Raises an exception if the key validation is unsuccessful. No return output.

    Options:\\
    \t\\- contains_keys():\\
    \t\t\\- Checks if some required keys exist in the dictionary.\\
    \t\\- all_keys():\\
    \t\t\\- Checks if all required keys exist in the dictionary.

    Args:
        values (dict): A dictionary that needs the keys validated.
        caller_module (str): The name of the caller module. Use '__name__'.
        caller_name (str): The name of the caller (func or method).
        caller_line (int): The calling function line.
    """
    def __init__(self, values: dict,
                 caller_module: str,
                 caller_name: str,
                 caller_line: int
                 ) -> None:
        self.__values: dict = values
        self.__caller_module: str = caller_module
        self.__caller_name: str = caller_name
        self.__caller_line: int = caller_line

    def contains_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if some required keys exist in the dictionary.

        Args:
            required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            AttributeError:
            \t\\- The input keys have inconsistent value and requirement keys.
            AttributeError:
            \t\\- The expected key list contains duplicate keys. All keys must be unique.
            InvalidKeyError:
            \t\\- The dictionary key (\'{no_matching_key}\') does not exist in the expected required key(s).
            InvalidKeyError:
            \t\\- The dictionary key (\'{no_matching_key}\') does not match any expected match option key(s).
        """
        self.__required_keys: Union[str, list] = required_keys
        self.__all_key_check: bool = False
        self.__reverse_output: bool = reverse_output
        self.__key_validation()

    def all_keys(self, required_keys: Union[str, list], reverse_output: Optional[bool] = False) -> None:
        """
        Checks if all required keys exist in the dictionary

        Args:
            required_keys (Union[str, list])):\\
            \t\\- The required key(s) that should match.\\
            \t\\- Can be a single str or list of keys.
            reverse (bool, optional):\\
            \t\\- Reverses the key check exception output, so the\\
            \t   expected result and returned results are flipped.\\
            \t\\- Defaults to False.

        Raises:
            AttributeError:\\
            \t\\- The input keys have inconsistent value and requirement keys.
            AttributeError:\\
            \t\\- The expected key list contains duplicate keys. All keys must be unique.
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\') does not exist in the expected required key(s).
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\') does not match any expected match option key(s).
        """
        self.__required_keys: Union[str, list] = required_keys
        self.__all_key_check: bool = True
        self.__reverse_output: bool = reverse_output
        self.__key_validation()

    def __key_validation(self) -> None:
        """
        Performs the key validation.

        Raises:
            AttributeError:\\
            \t\\- No key(s) were sent.
            AttributeError:\\
            \t\\- The input keys have inconsistent value and requirement keys.\\
            AttributeError:\\
            \t\\- The required key list contains duplicate keys. All keys must be unique.\\
            InvalidKeyError:\\
            \t\\- The dictionary key (\'{no_matching_key}\')\\
            \t  does not exist in the expected required key(s).
        """
        # Loops through to find any keys that do not match.
        dict_keys: list = list(self.__values.keys())

        # Reverses key results for flipped reverse checks.
        expected_key_result: list = None
        required_key_result: Union[str, list] = None
        if self.__reverse_output:
            expected_key_result = dict_keys
            required_key_result = self.__required_keys
        else:
            expected_key_result = self.__required_keys
            required_key_result = dict_keys

        # Checks for that required keys are sent.
        if not self.__required_keys:
            # Formats the output based on the check option.
            if self.__all_key_check:
                expected_result: str = f'  - Expected Key(s) = {expected_key_result}'
            else:
                expected_result: str = f'  - Expected Match Option Key(s) = {expected_key_result}'

            error_message: str = (
                f'No key(s) were sent.\n'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Returned Result:\n'
                f'{expected_result}\n\n'
                'Returned Result:\n'
                f'  - None\n\n'
                + f'Trace Details:\n'
                f'  - Exception: AttributeError\n'
                f'  - Module: {self.__caller_module}\n'
                f'  - Name: {self.__caller_name}\n'
                f'  - Line: {self.__caller_line}\n'
                + (('-' * 150) + '\n') * 2
            )
            raise AttributeError(error_message)

        # Checks for 1:1 input when using the all_keys option.
        if self.__all_key_check:
            mismatched_input: bool = None
            if isinstance(self.__required_keys, list):
                if len(dict_keys) != len(self.__required_keys):
                    mismatched_input = True
                else:
                    mismatched_input = False
            else:
                if len(self.__values) > 1:
                    mismatched_input = True

            if mismatched_input is True:
                error_message: str = (
                    f'The input keys have inconsistent value and requirement keys.\n'
                    + (('-' * 150) + '\n')
                    + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                    + (('-' * 150) + '\n')
                    + 'Expected Result:\n'
                    f'  - Required Key(s) = {expected_key_result}\n\n'
                    'Returned Result:\n'
                    f'  - Failed Key(s) = {required_key_result}\n\n'
                    + f'Trace Details:\n'
                    f'  - Exception: AttributeError\n'
                    f'  - Module: {self.__caller_name}\n'
                    f'  - Name: {self.__caller_name}\n'
                    f'  - Line: {self.__caller_line}\n'
                    + (('-' * 150) + '\n') * 2
                )
                raise AttributeError(error_message)
        else:
            mismatched_input = False

        # Checks for duplicate values.
        if isinstance(self.__required_keys, list):
            if len(self.__required_keys) != len(set(self.__required_keys)):
                error_message: str = (
                    f'The required key list contains duplicate keys. All keys must be unique.\n'
                    + (('-' * 150) + '\n')
                    + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                    + (('-' * 150) + '\n')
                    + 'Returned Result:\n'
                    f'  - Required Key(s) = {required_key_result}\n\n'
                    + f'Trace Details:\n'
                    f'  - Exception: AttributeError\n'
                    f'  - Module: {self.__caller_module}\n'
                    f'  - Name: {self.__caller_name}\n'
                    f'  - Line: {self.__caller_line}\n'
                    + (('-' * 150) + '\n') * 2
                )
                raise AttributeError(error_message)

        # Sets the keys in reverse order so the no-match is the last entry checked
        # but the first no-match in the list of keys.
        sorted_dict_keys: list = sorted(dict_keys, reverse=True)

        if isinstance(self.__required_keys, list):
            no_matching_key: str = None
            for required_key in self.__required_keys:
                # Checks if the validation requires all the required keys
                # to match all sorted_dict_keys or the required keys to match
                # some of the sorted_dict_keys.
                if self.__all_key_check:
                    for dict_key in sorted_dict_keys:
                        # Checks for exact match.
                        if required_key == dict_key:
                            no_matching_key = None
                            break
                        else:
                            no_matching_key = required_key
                else:
                    if required_key in sorted_dict_keys:
                        no_matching_key = None
                    else:
                        no_matching_key = required_key
                # If a match is not found on the first required
                # key check the loop will exit and return the no-matched key.
                if no_matching_key:
                    break
        else:
            # Variable name swap for easier loop reading.
            required_key: str = self.__required_keys
            no_matching_key: str = None
            for dict_key in sorted_dict_keys:
                if required_key != dict_key:
                    no_matching_key = required_key

        # Checks if a no matching key exists, to output the error
        if no_matching_key:
            # Formats the output based on the check option.
            if self.__all_key_check:
                main_message: str = (f'The dictionary key (\'{no_matching_key}\') '
                                     'does not exist in the expected required key(s).\n')
                expected_result: str = f'  - Expected Key(s) = {expected_key_result}'
                returned_result: str = f'  - Failed Key(s) = {required_key_result}'
            else:
                main_message: str = (f'The dictionary key (\'{no_matching_key}\') '
                                     'does not match any expected match option key(s).\n')
                expected_result: str = f'  - Match Option Key(s) = {expected_key_result}'
                returned_result: str = f'  - Failed Key(s) = {required_key_result}'

            error_message: str = (
                f'{main_message}'
                + (('-' * 150) + '\n')
                + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
                + (('-' * 150) + '\n')
                + 'Expected Result:\n'
                f'{expected_result}\n\n'
                'Returned Result:\n'
                f'{returned_result}\n\n'
                + f'Trace Details:\n'
                f'  - Exception: AttributeError\n'
                f'  - Module: {self.__caller_module}\n'
                f'  - Name: {self.__caller_name}\n'
                f'  - Line: {self.__caller_line}\n'
                + (('-' * 150) + '\n') * 2
            )
            raise InvalidKeyError(error_message)

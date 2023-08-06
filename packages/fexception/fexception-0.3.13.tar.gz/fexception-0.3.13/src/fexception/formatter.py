from pathlib import Path
from .common import ProcessedMessageArgs, ExceptionArgs


__author__ = 'IncognitoCoding'
__copyright__ = 'Copyright 2022, formatter'
__credits__ = ['IncognitoCoding']
__license__ = 'MIT'
__version__ = '0.3.10'
__maintainer__ = 'IncognitoCoding'
__status__ = 'Beta'


def exception_formatter(processed_message_args: ProcessedMessageArgs, exception_args: ExceptionArgs) -> str:
    """
    The exception formatter creates consistent clean exception output.
    No logging will take place within this function.\\
    The exception output will have an origination location based on the exception section.\\
    Any formatted raised exceptions will originate from the calling function.\\
    All local function or Attribute errors will originate from this function.

    The user can override the exception type from the general custom exception module classes above.

    Args:
        processed_message_args (ProcessedMessageArgs):\\
        \t\\- Message args to populate the formatted exception message.
        exception_args (ExceptionArgs):
        \t\\- Exception args to populate the formatted exception message.
    """
    # #################################################
    # ###########Formats Lists or Str Output###########
    # #################################################
    if processed_message_args.expected_result:
        if isinstance(processed_message_args.expected_result, list):
            formatted_expected_result: str = str('  - ' + '\n  - '.join(map(str, processed_message_args.expected_result)))
        else:
            formatted_expected_result: str = f'  - {processed_message_args.expected_result}'
    if processed_message_args.returned_result:
        if isinstance(processed_message_args.returned_result, list):
            formatted_returned_result: str = str('  - ' + '\n  - '.join(map(str, processed_message_args.returned_result)))
        else:
            formatted_returned_result: str = f'  - {processed_message_args.returned_result}'
    if processed_message_args.suggested_resolution:
        if isinstance(processed_message_args.suggested_resolution, list):
            formatted_suggested_resolution: str = str('  - ' + '\n  - '.join(map(str, processed_message_args.suggested_resolution)))
        else:
            formatted_suggested_resolution = f'  - {processed_message_args.suggested_resolution}'
    if processed_message_args.original_exception:
        formatted_original_exception: str = str('\n            ' + '\n            '.join(map(str, str(processed_message_args.original_exception).splitlines())))

    # #################################################
    # #######Constructs Message Based On Input#########
    # #################################################
    if processed_message_args.main_message:
        formatted_main_message: str = f'{processed_message_args.main_message}\n'
    else:
        formatted_main_message: str = ' None: No Message Provided\n'

    if processed_message_args.expected_result:
        formatted_expected_result: str = ('Expected Result:\n'
                                          + f'{formatted_expected_result}\n\n')
    else:
        formatted_expected_result: str = ''

    if processed_message_args.returned_result:
        formatted_returned_result: str = ('Returned Result:\n'
                                          + f'{formatted_returned_result}\n\n')
    else:
        formatted_returned_result: str = ''

    if processed_message_args.original_exception:
        # Sets as empty string to format empty line if no
        # nested trace details exist.
        formatted_nested_trace_details: str = ''
        # Checks if the nested exception is previously formatted.
        # Previously formatted exceptions will not have the nested trace details added.
        if 'Nested Trace Details:' not in str(processed_message_args.original_exception):
            nested_module: str = Path(processed_message_args.original_exception.__traceback__.tb_frame.f_code.co_filename).stem
            nested_name: str = processed_message_args.original_exception.__traceback__.tb_frame.f_code.co_name
            if str(nested_name) == '<module>':  # pragma: no cover
                nested_name = '__main__'
            nested_line: int = processed_message_args.original_exception.__traceback__.tb_lineno

            # Sets the trace details even if the limit is 0.
            # Without the trace details, the nested message would be useless with a limit of 0.
            formatted_nested_trace_details: str = (
                f'            Nested Trace Details:\n'
                f'              - Exception: {type(processed_message_args.original_exception).__name__}\n'
                f'              - Module: {nested_module}\n'
                f'              - Name: {nested_name}\n'
                f'              - Line: {nested_line}\n'
            )

        formatted_original_exception: str = ('Nested Exception:\n\n'
                                             + '            '
                                             + (('~' * 150) + '\n            ')
                                             + (('~' * 63) + 'Start Original Exception' + ('~' * 63) + '\n            ')
                                             + (('~' * 150) + '\n            \n')
                                             + f'{formatted_original_exception}\n\n'
                                             + f'{formatted_nested_trace_details}'
                                             + '            ' + (('~' * 150) + '\n            ')
                                             + (('~' * 65) + 'End Original Exception' + ('~' * 63) + '\n            ')
                                             + (('~' * 150) + '\n            \n'))
    else:
        formatted_original_exception: str = ''

    if processed_message_args.suggested_resolution:
        formatted_suggested_resolution: str = ('Suggested Resolution:\n'
                                               f'{formatted_suggested_resolution}\n\n')
    else:
        formatted_suggested_resolution: str = ''

    # Sets the trace details if the limit is anything other than 0.
    if exception_args.tb_limit != 0:
        caller_name: str = exception_args.caller_name
        if str(caller_name) == '<module>':  # pragma: no cover
            caller_name = '__main__'

        formatted_trace_details: str = ('Trace Details:\n'
                                        f'  - Exception: {exception_args.exception_type.__name__}\n'
                                        f'  - Module: {exception_args.caller_module}\n'
                                        f'  - Name: {caller_name}\n'
                                        f'  - Line: {exception_args.caller_line}\n')
    else:
        formatted_trace_details: str = ''

    exception_message: str = (
        formatted_main_message
        + (('-' * 150) + '\n')
        + (('-' * 65) + 'Additional Information' + ('-' * 63) + '\n')
        + (('-' * 150) + '\n')
        + formatted_expected_result
        + formatted_returned_result
        + formatted_original_exception
        + formatted_suggested_resolution
        + formatted_trace_details
        + (('-' * 150) + '\n') * 2
    )
    return exception_message

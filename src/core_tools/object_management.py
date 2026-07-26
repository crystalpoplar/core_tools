import re
import traceback

from . import file_management
from . import logger

LOG = logger.create_logger("core_tools", "core_tools.log")

def make_list_comma_separated(list):
    """
    Converts a list to a comma-separated string.

    Parameters:
        list (list): The list to convert.

    Returns:
        str: The comma-separated string.
    """
    text = ''
    for entry in list:
        text = str(text) + str(entry) + ', '
    text = text.rstrip(', ') + '.'
    return text


def make_list_comma_separated_text(entries):
    """Preferred snake_case alias for make_list_comma_separated."""
    return make_list_comma_separated(entries)


def list2csv(list_check):
    """
    Converts a list to a CSV string.

    Parameters:
        list (list): The list to convert.

    Returns:
        str: The CSV string.
    """
    csv_list = ''
    if not isinstance(list_check, list):
        for value in list_check:
            csv_list = csv_list + ',' + value
        return csv_list[1:]
    else:
        return list_check


def list_to_csv(list_check):
    """Preferred snake_case alias for list2csv."""
    return list2csv(list_check)


def makeTextJson(textStr):
    """
    Converts a text string to JSON format.

    Parameters:
        textStr (str): The text string to convert.

    Returns:
        str: The JSON string.
    """
    while len(textStr) > 0 and textStr[0] != '{':
        textStr = textStr[1:]
    while len(textStr) > 0 and textStr[-1] != '}':
        textStr = textStr[:-1]
    return textStr


def make_text_json(text_str):
    """Preferred snake_case alias for makeTextJson."""
    return makeTextJson(text_str)


def getValuesFromJson(keys, jsonFilePath):
    """
    Retrieves values from a JSON file based on the provided keys.

    Parameters:
        keys (list): A list of string keys to retrieve values for. Nested keys should be provided as lists.
        jsonFilePath (str): The path to the JSON file.

    Returns:
        tuple: A tuple of values corresponding to the keys. If a key does not exist, the value will be None.
    """

    def get_nested_value(data, key_list):
        """Helper function to retrieve nested values from a dictionary."""
        for key in key_list:
            if isinstance(data, dict):
                data = data.get(key, None)
            else:
                return None
        return data

    jsonData = file_management.getJsonDict(jsonFilePath)
    values = tuple(get_nested_value(jsonData, key) if isinstance(key, list) else jsonData.get(key, None) for key in keys)
    return values


def get_values_from_json(keys, json_file_path):
    """Preferred snake_case alias for getValuesFromJson."""
    return getValuesFromJson(keys, json_file_path)


def stringFormatter(string: str, log: logger.create_logger = LOG) -> str:
    """
    Replace placeholders in the input string:
      - {functionName} -> call a zero-argument function with that name from globals() and substitute its return value
      - [LOOKUP]        -> lookup value from globals() or JSON files with special prefix DICT.<file>.<key1>.<key2>...

    Behavior and improvements:
      - Uses regular expressions with callback functions for efficient single-pass replacements.
      - Performs iterative passes (up to max_passes) to resolve placeholders introduced by replacements,
        preventing infinite loops by bounding iterations.
      - Robustly handles missing functions/values and logs warnings/errors to mainLog.
      - Supports nested dict lookups in JSON files and nested attribute/key access for globals variables.
      - Normalizes replacement values to strings and strips newlines/tabs.
    """

    max_passes = 5
    pass_num = 0

    if not isinstance(string, str):
        log.debug("stringFormatter received non-str input; converting to str")
        string = str(string)

    func_pattern = re.compile(r'\{([^{}]+)\}')
    lookup_pattern = re.compile(r'\[([^\[\]]+)\]')

    def _format_value(val):
        """Normalize various types to a safe string representation."""
        if val is None:
            return ''
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, list):
            return ', '.join(str(x) for x in val)
        if isinstance(val, dict):
            return ', '.join(f"{k}: {v}" for k, v in val.items())
        s = str(val)
        return s.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

    def _replace_function(match):
        name = match.group(1).strip()
        func_name = name.split('(')[0].strip()
        func = globals().get(func_name)
        if not callable(func):
            log.warning(f"stringFormatter: function '{func_name}' not found or not callable")
            return match.group(0)
        try:
            result = func()
            formatted = _format_value(result)
            log.debug(f"stringFormatter: replaced function {{{name}}} -> '{formatted}'")
            return formatted
        except Exception as e:
            log.error(f"stringFormatter: error calling function '{func_name}': {e}")
            log.error(traceback.format_exc())
            return match.group(0)

    def _resolve_dict_lookup(dict_name: str, keys, log: logger.create_logger = LOG):
        """Load a JSON file and traverse nested keys."""
        try:
            jsonData = file_management.getJsonDict(f"{dict_name}.json")
        except Exception as e:
            log.error(f"stringFormatter: error loading JSON '{dict_name}.json': {e}")
            return None
        data = jsonData
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k, None)
            else:
                return None
        return data

    def _resolve_global_lookup(parts):
        """Resolve nested lookups in globals (dict keys or attributes)."""
        obj = globals().get(parts[0])
        if obj is None:
            return None
        for p in parts[1:]:
            if isinstance(obj, dict):
                obj = obj.get(p, None)
            else:
                obj = getattr(obj, p, None)
            if obj is None:
                return None
        return obj

    def _replace_lookup(match):
        content = match.group(1).strip()
        try:
            if content.startswith('DICT.'):
                rest = content[len('DICT.'):].strip()
                parts = rest.split('.')
                dict_name = parts[0]
                keys = parts[1:] if len(parts) > 1 else []
                val = _resolve_dict_lookup(dict_name, keys)
            else:
                parts = content.split('.')
                val = _resolve_global_lookup(parts)
            formatted = _format_value(val)
            log.debug(f"stringFormatter: replaced lookup [{content}] -> '{formatted}'")
            return formatted
        except Exception as e:
            log.error(f"stringFormatter: error resolving lookup '[{content}]': {e}")
            log.error(traceback.format_exc())
            return match.group(0)

    previous = None
    while pass_num < max_passes and string != previous:
        previous = string
        try:
            string = func_pattern.sub(_replace_function, string)
        except Exception as e:
            log.error(f"stringFormatter: error during function replacements: {e}")
            log.error(traceback.format_exc())
            break
        try:
            string = lookup_pattern.sub(_replace_lookup, string)
        except Exception as e:
            log.error(f"stringFormatter: error during lookup replacements: {e}")
            log.error(traceback.format_exc())
            break
        pass_num += 1

    if pass_num == max_passes:
        log.warning("stringFormatter: maximum passes reached; result may still contain unresolved placeholders")

    return string


def string_formatter(text: str) -> str:
    """Preferred snake_case alias for stringFormatter."""
    return stringFormatter(text)


def executeFunctionInString(string):
    """
    This function replaces placeholders in the format {functionName} within the input string
    with the result of calling the corresponding function.

    Arguments:
    string (str): The input string containing placeholders.

    Returns:
    str: The string with placeholders replaced by function results.
    """
    while '{' in string and '}' in string:
        try:
            function_name = string.split('{')[1].split('}')[0]
            function_result = globals().get(function_name.split('(')[0])
            if function_result:
                function_string = function_result()
                string = string.replace(f'{{{function_name}}}', function_string)
            else:
                raise ValueError(f"Function '{function_name}' not found.")
        except Exception as e:
            print(f"Error executing function '{function_name}': {e}")
            break
    return string


def execute_function_in_string(text):
    """Preferred snake_case alias for executeFunctionInString."""
    return executeFunctionInString(text)


def largeSentenceDisplay(text, maxLength=190, log: logger.create_logger = LOG):
    """
    Wraps long text lines by breaking them at a maximum length.

    Takes text that may contain newlines and ensures no line exceeds maxLength
    characters. Lines longer than maxLength are split into multiple lines.

    Parameters:
        text (str): The input text to wrap, may contain newline characters.
        maxLength (int, optional): Maximum characters per line. Defaults to 190.

    Returns:
        str: The wrapped text with newlines inserted to enforce line length limits.
    """
    log.debug(f"largeSentenceDisplay: wrapping text of length {len(text)} with maxLength={maxLength}")

    if not isinstance(text, str):
        log.warning(f"largeSentenceDisplay: received non-string input of type {type(text)}, converting to string")
        text = str(text)

    if maxLength <= 0:
        log.error(f"largeSentenceDisplay: invalid maxLength={maxLength}, using default 190")
        maxLength = 190

    textList = text.split('\n')
    result_lines = []

    for textStr in textList:
        if len(textStr) <= maxLength:
            result_lines.append(textStr)
        else:
            chunks = []
            for i in range(0, len(textStr), maxLength):
                chunks.append(textStr[i:i + maxLength])
            result_lines.extend(chunks)

    newText = '\n'.join(result_lines) + '\n'

    log.debug(f"largeSentenceDisplay: output has {len(result_lines)} lines")
    return newText


def large_sentence_display(text, max_length=190):
    """Preferred snake_case alias for largeSentenceDisplay."""
    return largeSentenceDisplay(text, maxLength=max_length)

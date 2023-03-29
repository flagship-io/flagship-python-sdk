from __future__ import absolute_import

import json

import six

import flagship
from flagship.constants import TAG_CONFIG_PARAM, WARNING_CONFIGURATION_PARAM_TYPE, WARNING_CONFIGURATION_PARAM_MIN_MAX


def log(tag, level, message, start_config=None):
    configuration = start_config if start_config is not None else flagship.Flagship.config()
    if configuration is not None:
        custom_log_manager = configuration.log_manager
        custom_log_level = configuration.log_level
        if custom_log_manager is not None and (0 < level.value <= custom_log_level.value):
            custom_log_manager.log(tag, level, message)


def log_exception(tag, exception, traceback):
    configuration = flagship.Flagship.config()
    configured_log_manager = configuration.log_manager if configuration is not None else None
    if configured_log_manager is not None:
        configured_log_manager.exception(tag, exception, traceback)


def get_args_or_default(key, expected_type, default_value, kwargs):
    if key not in kwargs:
        return default_value or None
    elif not isinstance(kwargs[key], expected_type):
        from flagship import LogLevel
        log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_TYPE.format(key))
    else:
        return kwargs[key]

        #     return default_value
    # if key in kwargs and isinstance(kwargs[key], expected_type):
    #     return kwargs[key]
    # else:
    #     from flagship import LogLevel
    #     log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_TYPE.format(key))
    #     return default_value


def get_args_or_default_with_min_max(key, expected_type, default_value, kwargs, min=-1, max=-1):
    from flagship import LogLevel
    if key not in kwargs:
        return default_value or None
    elif not isinstance(kwargs[key], expected_type):
        from flagship import LogLevel
        log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_TYPE.format(key))
    elif not -1 < min <= kwargs[key] <= max and max > min:
        log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_MIN_MAX.format(key, default_value))
        return default_value
    else:
        return kwargs[key]
    # from flagship import LogLevel
    # if key in kwargs and isinstance(kwargs[key], expected_type):
    #     result = kwargs[key]
    #     if -1 < min <= result <= max and max > min:
    #         return result
    #     else:
    #         log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_MIN_MAX.format(key, default_value))
    #         return default_value
    # else:
    #     log(TAG_CONFIG_PARAM, LogLevel.WARNING, WARNING_CONFIGURATION_PARAM_TYPE.format(key))
    #     return default_value


def pretty_dict(node, indent=2, string="", first=True):
    if isinstance(node, dict):
        if first:
            string += '{\n'
        for key, value in node.items():
            string += ((' ' * indent + '"' + str(key)) + '"')
            if isinstance(value, dict):
                string += ": {\n" + pretty_dict(value, indent + 2, "", False) + "\n" + (' ' * indent) + "},\n"
            elif isinstance(value, list):
                string += ": [\n" + pretty_dict(value, indent + 2, "", False) + "\n" + (' ' * indent) + "],\n"
            else:
                string += ": " + pretty_dict(value, indent + 2, "", False) + ",\n"
    elif isinstance(node, list):
        if first:
            string += '[\n'
        for i in range(0, len(node)):
            if isinstance(node[i], dict):
                string += (' ' * indent) + "{\n" + pretty_dict(node[i], indent + 2, "", False) + "\n" + (
                            ' ' * indent) + "},\n"
            elif isinstance(node[i], list):
                string += (' ' * indent) + "[\n" + pretty_dict(node[i], indent + 2, "", False) + "\n" + (
                            ' ' * indent) + "],\n"
            else:
                string += (' ' * indent) + pretty_dict(node[i], indent + 2, "", False) + ",\n"
    else:
        if node is None:
            string += "null"
        elif isinstance(node, six.string_types):
            string += ('"{}"'.format(node))
        elif isinstance(node, bool):
            string += ('{}'.format("true" if node is True else "false"))
        else:
            string += ('{}'.format(node))
        string += ",\n"

    if first and isinstance(node, dict):
        return (string[:-2] if len(string) > 2 else string) + "\n}"
    elif first and isinstance(node, list):
        return (string[:-2] if len(string) > 2 else string) + "\n]"
    return string[:-2]
    # return json.dumps(node, indent=2)

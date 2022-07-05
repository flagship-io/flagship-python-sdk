from __future__ import absolute_import

import json

import flagship


def log(tag, level, message):
    configuration = flagship.Flagship.config()
    configured_log_manager = configuration.log_manager if configuration is not None else None
    if configured_log_manager is not None:
        configured_log_manager.log(tag, level, message)


def log_exception(tag, exception, traceback):
    configuration = flagship.Flagship.config()
    configured_log_manager = configuration.log_manager if configuration is not None else None
    if configured_log_manager is not None:
        configured_log_manager.exception(tag, exception, traceback)


def pretty_dict(dictionary, indent=2, string="", first=True):
    if first:
        string += '{\n'
    for key, value in dictionary.items():
        string += ((' ' * indent + "\"" + str(key)) + "\"")
        if isinstance(value, dict):
            string += ": {\n" + pretty_dict(value,  indent + 2, "", False) + "\n" + (
                ' ' * indent) + "},\n"
        elif isinstance(value, list):
            string += ": [\n"
            for i in range(0, len(value)):
                string += (' ' * (indent + 2)) + "{\n"
                string += pretty_dict(value[i], indent + 4, "", False) + "\n"
                string += (' ' * (indent + 2)) + "},\n"
            string = string[:-2] + "\n"
            string += (' ' * indent) + "],\n"
        else:
            if value is None:
                string += ": null"
            elif isinstance(value, str):
                string += (': \"{}\"'.format(value))
            elif isinstance(value, bool):
                string += (': {}'.format("true" if value is True else "false"))
            else:
                string += (': {}'.format(value))
            string += ",\n"

    if first:
        return (string[:-2] if len(string) > 2 else string) + "\n}"
    else:
        return string[:-2]
    # return json.dumps(dictionary, indent=4)

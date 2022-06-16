from __future__ import absolute_import


import flagship


def log(tag, level, message):
    configuration = flagship.Flagship.config()
    configured_log_manager = configuration.log_manager if configuration is not None else None
    if configured_log_manager is not None:
        configured_log_manager.log(tag, level, message)
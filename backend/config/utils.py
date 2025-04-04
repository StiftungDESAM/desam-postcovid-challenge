"""
This file contains helper functions for initializing the project settings.
"""

def str_to_bool(value: str) -> bool:
    value = value.lower()
    if value in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif value in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError("Invalid truth value %r" % (value,))

def str_to_list(value: str, separator: str = ","):
    if not value:
        return []
    return value.split(separator)

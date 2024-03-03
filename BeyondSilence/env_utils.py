import os


def get_env_var(var_name):
    """
    Get the value of an environment variable.

    Args:
        var_name (str): The name of the environment variable.

    Returns:
        str or False: The value of the environment variable, or False if it is not set or empty.
    """
    value = os.environ.get(var_name)
    if value and value != "":
        return value
    else:
        return False

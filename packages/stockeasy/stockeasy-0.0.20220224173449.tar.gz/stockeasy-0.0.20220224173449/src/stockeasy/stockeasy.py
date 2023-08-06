def analyzer(config: dict, data: dict, logger: object):
    """
    This function completes a review of a provide stock portfolio.

    Args:
        config (dict): Configurable Options
        data (dict): Dictionary of named Pandas Dataframes
        logger (object): Standard Python Logger
    Returns:
        None
    """
    # Type Check
    if (not isinstance(config, dict)):
        return 1
    if (not isinstance(data, dict)):
        return 1

    print(r'Hello World')

    return 0

from logging import Logger


def validate_input_contract(data, config, logger):
    """
    This function validates that the tool is receiving expected values.
        Args:
        config (dict): Configurable Options
        data (dict): Dictionary of named Pandas Dataframes
        logger (object): Standard Python Logger

    Returns:
        None
    """
    if (not isinstance(config, dict)):
        raise TypeError('Invalid Configuration Provided. Must be of type Dict')
    if (not isinstance(data, dict)):
        raise TypeError('Invalid Data Provided. Must be of type Dict')
    if (not isinstance(logger, Logger)):
        raise TypeError('Invalid Logger Provided. Must be of type Logger')

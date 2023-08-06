import pandas as pd
import logging
from . import utils


def analyzer(data: dict = {}, config: dict = {}, logger: object = logging.getLogger('default')):
    """
    This function completes a review of a provide stock portfolio.

    Args:
        config (dict): Configurable Options
        data (dict): Dictionary of named Pandas Dataframes
        logger (object): Standard Python Logger

    Returns:
        Results(dict): Dictionary of output pandas dataframes
    """
    utils.validate_input_contract(data=data, config=config, logger=logger)

    return {
        'output': data.get('input'),
        'report': pd.DataFrame(['<html><body>passthrough used</body></html>'], columns=['report']),
    }

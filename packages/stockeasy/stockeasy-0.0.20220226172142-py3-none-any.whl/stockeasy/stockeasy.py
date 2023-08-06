import pandas as pd
import logging
from . import utils
import yfinance as yf


def get_info(data: dict = {}, config: dict = {}, logger: object = logging.getLogger('default')):
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

    # Set required Parameters
    columns_list = config.setdefault('dataFields', ['exchange', 'symbol', 'shortName', 'sector', 'country', 'marketCap'])
    symbolField = config.setdefault('symbolField', 'symbol')
    df_input = data.setdefault('input', pd.DataFrame(columns=['symbol']))

    raw_data = []

    for index, row in df_input.iterrows():
        stock_symbol = row[symbolField]
        stock_info = yf.Ticker(stock_symbol).info

        stock_data = []
        for column in columns_list:
            stock_data.append(stock_info.get(column))
        raw_data.append(stock_data)

    df_stock_info = pd.DataFrame(data=raw_data, columns=columns_list)

    df_stock_data = pd.merge(
        left=df_input,
        right=df_stock_info,
        how='inner',
        left_on=symbolField,
        right_on='symbol'
    )

    return {
        'output': df_stock_data,
        'report': pd.DataFrame(['<html><body>Update with render</body></html>'], columns=['report']),
    }

from typing import Dict

import pandas as pd

from src.base.loggers import Logger

__all__ = [
    'get_data',
]


def get_data(foods_df: pd.DataFrame, nutrient_aliases: pd.DataFrame, logger: Logger) -> Dict:
    """
    TODO: scape data from Agile spreadsheet
          conform to output format in .usda_foods
    """
    _ = foods_df, nutrient_aliases

    log = logger.spawn('Herbalife')

    log.info('Parsed Herbalife data')
    return {}

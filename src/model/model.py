import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from typing import Tuple

from src import __RESOURCE__
from src.base import loggers

__all__ = [
    'build_model',
]


def build_model(logger: loggers.Logger, on_complete_f: Callable) -> None:
    ti = time.perf_counter()

    log = logger.spawn('Model')
    import pandas as pd
    from src.model import herbalife_foods
    from src.model import usda_foods
    from src.model.config import Model

    def read_spreadsheet(args: Tuple[str, loggers.Logger]):
        name, logger = args
        file_name = f'{name}.xlsx'

        logger.info(f'Loading `{file_name}`...')
        df = pd.read_excel(__RESOURCE__.dat(file_name))

        logger.info(f'Loaded `{file_name}`.')
        return df

    try:
        # load app configuration file into app's Model object
        model = Model(**__RESOURCE__.cfg('app.yml', parse=True))
        log.info('Read `app.yml`.')

        # loading spreadsheets into memory takes forever, so we do them concurrently
        sheet_filenames = 'USDA_foods', 'USDA_nutrients', 'Herbalife_foods', 'Herbalife_nutrient_aliases'
        with ThreadPoolExecutor() as executor:
            dataframes: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] = executor.map(  # type: ignore
                read_spreadsheet, [(name, log) for name in sheet_filenames]
            )

        usda_food_df, usda_nutrient_df, hl_foods_df, nutrient_aliases_df = dataframes

        # extract needed data from the USDA config spreadsheets
        usda_foods_of_interest = usda_food_df['FoodID'].to_list()
        nutrients_of_interest = usda_nutrient_df['Nutrient'].to_list()

        # fetch latest data from the USDA API
        usda_food_data = usda_foods.get_data(
            usda_foods_of_interest, nutrients_of_interest, model.USDA_MISSES_MAX_QTY, log
        )

        for food_id, food in usda_food_data.items():
            for k in ('UOM', 'QTY'):
                food[k] = usda_food_df.loc[usda_food_df.FoodID == food_id, k].values[0]

        model.foods = usda_food_data
        # get data from the Herbalife Agile spreadsheet
        model.foods.update(herbalife_foods.get_data(hl_foods_df, nutrient_aliases_df, log))

        log.info(f'Built model in {time.perf_counter() - ti: .3f}s')
        on_complete_f(model)

    except Exception as e:
        on_complete_f(e)

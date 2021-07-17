import pathlib
import pickle
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from typing import Tuple

from kivy import Logger

from src import __RESOURCE__
from src.base import loggers

__all__ = [
    'build_model',
]

PICKLE_PATH = __RESOURCE__.dat('model_dump.p')


def build_model(logger: loggers.Logger, on_complete_f: Callable) -> None:
    ti = time.perf_counter()

    if pathlib.Path(PICKLE_PATH).exists():
        with open(PICKLE_PATH, 'rb') as pf:
            model = pickle.load(pf)
            on_complete_f(model)
            return

    log = logger.spawn('Model')
    import pandas as pd
    from src.build import herbalife
    from src.build import usda
    from src.model.config import Model

    def read_spreadsheet(args: Tuple[str, loggers.Logger]):
        name, logger = args
        file_name = f'{name}.xlsx'

        logger.info(f'Loading `{file_name}`...')
        df = pd.read_excel(__RESOURCE__.dat(file_name), sheet_name=None)
        if len(df) == 1:
            for sheet_name, df in df.items():
                break

        logger.info(f'Loaded `{file_name}`.')
        return df

    try:
        # load app configuration file into app's Model object
        model = Model(**__RESOURCE__.cfg('app.yml', parse=True))
        log.info('Read `app.yml`.')

        # loading spreadsheets into memory takes forever, so we do them concurrently
        sheet_filenames = (
            'USDA_Foods', 'USDA_Nutrients', 'HLF_Foods',
            'Nutrient_Aliases', 'UOM_Aliases', 'Limits_by_Region'
        )
        with ThreadPoolExecutor() as executor:
            dataframes: Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame] = executor.map(  # type: ignore
                read_spreadsheet, [(name, log) for name in sheet_filenames]
            )

        usda_food_df, usda_nutrient_df, hl_foods_df, *rest = dataframes
        nutrient_aliases_df, uom_aliases, limits_by_region = rest

        # extract needed data from the USDA config spreadsheets
        usda_foods_of_interest = usda_food_df['FoodID'].to_list()
        nutrients_of_interest = usda_nutrient_df['Nutrient'].to_list()
        model.limits_by_region.update(limits_by_region)

        # fetch latest data from the USDA API
        usda_food_data = usda.get_data(
            usda_foods_of_interest, nutrients_of_interest, model.USDA_MISSES_MAX_QTY, log
        )

        for food_id, food in usda_food_data.items():
            for k in ('UOM', 'QTY'):
                food[k] = usda_food_df.loc[usda_food_df.FoodID == food_id, k].values[0]

        model.foods = usda_food_data
        # get data from the Herbalife Agile spreadsheet
        model.foods.update(herbalife.get_data(hl_foods_df, nutrient_aliases_df, log))

        with open(PICKLE_PATH, 'wb') as pf:
            pickle.dump(model, pf)

        log.info(f'Built model in {time.perf_counter() - ti: .3f}s')
        on_complete_f(model)

    except Exception as e:
        on_complete_f(e)


if __name__ == '__main__':
    log = loggers.Logger('Model', Logger)

    # def callback(return_value):
    #     if isinstance(return_value, Exception):
    #         raise return_value
    #     log.info(return_value)
    #
    #
    # build_model(log, callback)

    from src.model import Database, db

    session_manager = Database(db.Schema, "sqlite:///c:/projects/nutrition/dev/db/test.db") \
        .connect(log, True, True)

import random
from typing import *

from requests_toolbelt import threaded

from src.base.exceptions import USDAFoodsError
from src.base.loggers import Logger

__all__ = [
    'get_data',
]

# noinspection SpellCheckingInspection
API_KEY: str = r'IAq4gn3KahA24GAAeEOZLNO6ghwzTWWtU7awLFw5'
POST_URI: str = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}'


class HTTPRequestError(Exception):
    pass


class FoodIdNotFoundError(Exception):
    pass


class NutrientNotExtantError(Exception):
    pass


def requests_for(food_ids: List[int]) -> List[Dict[str, Union[str, Dict[str, int]]]]:
    """
    make a list of request data to pass to the threaded package
    the only difference between each element in the returned list is the food_id
    """
    return [{
        'url': POST_URI,
        'method': 'POST',
        'json': {
            "query": fid
        }
    } for fid in food_ids]


def parse_response(http_response, nutrients: List[str], output: Dict) -> int:
    """
    extract the amount of each nutrient from one food response
    include the food id from the response because requests might be serviced in any order
    """

    # parse returned data
    # an example of the raw return data is dev\response_data.json
    _json = http_response.json()
    results = _json['foods']

    if not results:
        # if a query succeeds but there is no matching food,
        # raise a descriptive exception
        query_term = _json['foodSearchCriteria']['query']
        raise FoodIdNotFoundError(f'Requesting food_id {query_term} returned no results')

    # searching by food_id returns a list of one element
    # we extract that element here
    response = results[0]

    # initialize working structures
    # output is a dictionary containing the description and will be extended in the loop
    fid = response['fdcId']
    description = response['description']

    parsed_output = dict(
        food_id=fid,
        source='USDA' if not random.randint(0, 2) else 'Herbalife',  # TODO: remove this
        description=description,
    )

    # nutrients of interest are made into a set for fast operations
    # this is a to-do list of data to extract
    _nutrients_of_interest = set(nutrients)

    for d in response['foodNutrients']:
        # d is one nutrient dictionary at a time

        _name = d['nutrientName']

        if _name in _nutrients_of_interest:

            # this block executes if the nutrient is one we care about
            # this makes a small dict with only the values we care about and
            # puts it in the output dict
            parsed_output[_name] = {
                'value': d['value'],
                'unit': d['unitName']
            }

            # once we pull out the relevant data, we remove that nutrient from the to-do list
            _nutrients_of_interest.remove(_name)

        if not _nutrients_of_interest:
            # when our to-do list is empty, we stop the loop
            break

    else:
        # if there are to-do items left after all the nutrients have been done,
        # raise a descriptive exception
        raise NutrientNotExtantError(f'{_nutrients_of_interest} not found in response for {fid}')

    # return whatever data have been parsed out if successful
    output[fid] = parsed_output
    return fid


def get_data(food_ids, nutrients, max_misses: int, logger: Logger) -> Dict:
    """
    requests all data for each food
    parses out the nutrients of interest from the responses
    passes results to caller
    """

    log = logger.spawn('USDA')

    # given foods of interest, request those data from the API
    responses, exceptions = threaded.map(requests_for(food_ids))
    log.info('Requested USDA data')

    # raise any HTTP request error as fatal (this should never fail)
    for e in exceptions:
        raise USDAFoodsError(f'HTTP POST error') from e

    output = dict()

    # iterate through HTTP POST responses and parse them for desired nutrient info
    for response in responses:
        if max_misses:
            try:
                fid = parse_response(response, nutrients, output)

            except FoodIdNotFoundError as e:
                # errors of this kind may happen up to USDA_MISSES_MAX_QTY before fatal
                log.warning(str(e))

            except NutrientNotExtantError as e:
                # raise as fatal (this should never happen)
                log.error(str(e), exc_info=False)
                raise USDAFoodsError from e

            else:
                log.debug(f'parsed data for `{fid}`')
                continue

            max_misses -= 1

        else:
            raise USDAFoodsError(f'>{max_misses} failures in USDA get_data')

    log.info('Parsed USDA data')
    return output

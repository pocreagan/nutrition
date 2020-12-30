import json
from typing import *

from requests_toolbelt import threaded

__all__ = [
    'get_food_nutrients',
]

# noinspection SpellCheckingInspection
API_KEY: str = r'IAq4gn3KahA24GAAeEOZLNO6ghwzTWWtU7awLFw5'
POST_URI: str = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}'


class FoodIdNotFoundError(Exception):
    pass


class NutrientNotExtantError(Exception):
    pass


def requests_for(food_ids: list[int]) -> list[dict[str, Union[str, dict[str, int]]]]:
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


def parse_response(http_response, nutrients: list[str]) -> dict:
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
        raise FoodIdNotFoundError(f'requesting food_id {query_term} returned no results')

    # searching by food_id returns a list of one element
    # we extract that element here
    response = results[0]

    # initialize working structures
    # output is a dictionary containing the food id and will be extended in the loop
    fid = response['fdcId']
    parsed_output = dict(food_id=fid)

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
    return parsed_output


def get_food_nutrients(foods: list[int], nutrients: list[str]) -> None:
    """
    requests all data for each food
    parses out the nutrients of interest from the responses
    passes results to the output function
    """

    # given foods of interest, request those data from the API
    responses, exceptions = threaded.map(requests_for(foods))

    # parse each response
    data = [parse_response(response, nutrients) for response in responses]

    # pass the data and exceptions generator through to the output function
    output(data, exceptions)


def output(data, exceptions) -> None:
    """
    takes the parsed data and any http exceptions and displays them
    this function is where a person might write results to file or enqueue them or whatever
    """

    # print parsed JSON data in a readable format, with indentation
    print(json.dumps(data, indent=4))

    # print HTTP exceptions if any
    [print(exception) for exception in exceptions]


if __name__ == '__main__':
    # test our routine with hardcoded values

    # these are the hardcoded values
    foods_of_interest = [
        478743,
        433603,
        1102695,
        169134,
        1102757,
        167787,
        171909,
        1104367,
        170913,
        173166,

        # this should raise an exception
        # 11111111111111111111111111111111111111111111111111111111,
    ]
    nutrients_of_interest = [
        'Protein',
        'Energy',

        # this should raise an exception
        # 'blah blah blah',
    ]

    # run function
    get_food_nutrients(foods_of_interest, nutrients_of_interest)

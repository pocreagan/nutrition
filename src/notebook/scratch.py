import json
from typing import Dict

import requests

# noinspection SpellCheckingInspection
API_KEY: str = r'IAq4gn3KahA24GAAeEOZLNO6ghwzTWWtU7awLFw5'
POST_URI: str = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}'


def get_one_id(food_id: int) -> Dict:
    response = requests.post(POST_URI, json={"query": food_id})
    return response.json()


if __name__ == '__main__':
    print(json.dumps(get_one_id(171719), indent=4))

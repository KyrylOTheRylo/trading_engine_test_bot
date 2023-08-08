import requests
from config import APIADRESS
import json
from classes import TradingPair
from typing import List


def get_list_of_pairs() -> List[TradingPair]:
    return json.loads(requests.get(APIADRESS + "get_list_of_pairs").content)


def get_limits_for_a_pair(pair: TradingPair):
    return requests.get(APIADRESS + "get_limits_for_a_pair/{}_{}".format(pair.base, pair.quote)).content

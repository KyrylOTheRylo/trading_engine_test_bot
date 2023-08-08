import requests
from config import APIADRESS
import json
from classes import TradingPair, BidOrAsk
from typing import List


def get_list_of_pairs() -> List[TradingPair]:
    return json.loads(requests.get(APIADRESS + "get_list_of_pairs").content)


def get_limits_for_a_pair(pair: TradingPair):
    return requests.get(APIADRESS + "get_limits_for_a_pair/{}_{}".format(pair.base, pair.quote)).content


def place_limit_order(pair: TradingPair, buy_or_sell, price, size):
    answer = requests.post(APIADRESS + "create_limit_order/{}_{}/{}/{}/{}".format(pair.base, pair.quote, buy_or_sell,
                                                                                  price, size)).text
    return answer


def place_market_order(pair: TradingPair, buy_or_sell, size):
    answer = requests.post(APIADRESS + "create_market_order/{}_{}/{}/{}".format(pair.base, pair.quote, buy_or_sell,
                                                                                 size)).text
    return answer

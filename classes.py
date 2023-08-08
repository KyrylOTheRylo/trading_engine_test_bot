from pydantic import BaseModel
from typing import AnyStr, Dict, List
from enum import Enum
from itertools import islice


class TradingPair(BaseModel):
    base: AnyStr
    quote: AnyStr

    def prepare_for_list_command(self) -> str:
        return "/{}_{}".format(self.base, self.quote)


class BidOrAsk(Enum):
    Ask = "Ask"
    Bid = "Bid"


class Order(BaseModel):
    size: float
    bid_or_ask: BidOrAsk


class Limit(BaseModel):
    price: float
    orders: List[Order]
    total_volume: float

    @property
    def total_volume(self):
        return self.total_volume


class OrderBook(BaseModel):
    asks: Dict[float, Limit]
    bids: Dict[float, Limit]
    ask_capacity: float
    bid_capacity: float

    def get_n_ask(self, n: int) -> list:
        tmp = list(islice(self.asks.items(), n))
        answer = []
        for (x, limit) in tmp:
            answer.append((x, limit.total_volume))

        return answer

    def get_n_bid(self, n: int) -> List[tuple]:
        tmp = list(islice(self.bids.items(), n))
        answer = []
        for (x, limit) in tmp:
            answer.append((x, limit.total_volume))

        return answer

    def get_bids_and_asks_as_tuples_by_amount(self, n: int):
        return {"bids": self.get_n_bid(n), "asks": self.get_n_ask(n)}

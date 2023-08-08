from pydantic import BaseModel
from typing import AnyStr, OrderedDict, List
from enum import Enum


class TradingPair(BaseModel):
    base: AnyStr
    quote: AnyStr

    def prepare_for_list_command(self) -> str:
        return "/{}_{}".format(self.base, self.quote)


class BidOrAsk(Enum):
    Ask = 0,
    Bid = 1


class Order(BaseModel):
    size: float
    bid_or_ask: BidOrAsk


class Limit(BaseModel):
    price: float
    orders: List[Order]
    total_volume: float


class OrderBook(BaseModel):
    asks: OrderedDict[float, Limit]
    bids: OrderedDict[float, Limit]
    ask_capacity: float
    bid_capacity: float

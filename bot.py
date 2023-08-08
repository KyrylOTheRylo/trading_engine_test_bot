import json

from aiogram import Bot, Dispatcher, types, filters
from api_calls import get_list_of_pairs, get_limits_for_a_pair
from classes import TradingPair, OrderBook, Limit, BidOrAsk, Order
from aiogram.types import Message
import random
import datetime
from aiogram.utils import executor
import asyncio
from config import APITOKEN
import os

bot = Bot(token=APITOKEN)

dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, text="It is the bot for a demonstrational purpose of trading engine"
                                                      " built in Rust."
                                                      " (https://github.com/KyrylOTheRylo/tradingEngine)\n\n"
                                                      "Source code of this bot can be seen on "
                                                      "(https://github.com/KyrylOTheRylo/trading_engine_test_bot)\n\n"
                                                      "To get all current demo pairs use /list_of_pairs")


@dp.message_handler(commands=["list_of_pairs"])
async def list_of_pairs(message: types.Message):
    answer = []

    for pair in get_list_of_pairs():
        tmp_pair = TradingPair(base=pair[0], quote=pair[1])
        answer.append(tmp_pair.prepare_for_list_command())

    await bot.send_message(message.from_user.id, "To get info about orders use \n " + "\n\t".join(answer))


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'/(.*)_(.*)']))
async def pair_info(message: types.Message, regexp_command):
    pair = TradingPair(base=regexp_command.group(1), quote=regexp_command.group(2))
    orderbook = OrderBook(**json.loads(get_limits_for_a_pair(pair)))
    orderbook_bids_ask = orderbook.get_bids_and_asks_as_tuples_by_amount(5)
    answer = "ASKS\n"

    for ask_limit in orderbook_bids_ask["asks"]:
        answer += f"price = {ask_limit[0]} with amount {ask_limit[1]}\n"

    answer += f"\n\n\nBIDS\ntotal_bids_capacity = " \
              f"{orderbook.bid_capacity}\ntotal_asks_capacity = {orderbook.ask_capacity}"

    for bid_limit in orderbook_bids_ask["bids"]:
        answer += f"price = {bid_limit[0]} with amount {bid_limit[1]}\n"

    await bot.send_message(message.from_user.id, answer)


executor.start_polling(dp, skip_updates=True)

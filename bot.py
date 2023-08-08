import json

from typing import Optional
from aiogram import Bot, Dispatcher, types, filters
from api_calls import get_list_of_pairs, get_limits_for_a_pair, place_limit_order, place_market_order
from classes import TradingPair, OrderBook, Limit, BidOrAsk, Order
from aiogram.types import Message
import random
import datetime
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import asyncio
from config import APITOKEN
import os
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=APITOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    base = State()
    quote = State()
    limit_direction = State()
    price = State()
    size = State()


class Form1(StatesGroup):
    base = State()
    quote = State()
    market_direction = State()
    size = State()


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'/(.*)_(.*)_market']))
async def cmd_start_market_handler(message: types.Message, state: FSMContext, regexp_command):
    await Form1.market_direction.set()
    await state.update_data(base=str(regexp_command.group(1)))
    await state.update_data(quote=str(regexp_command.group(2)))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("buy", "sell")

    await message.reply("You want to place a buy market order or a sell one?\n"
                        "Write Cancel if you want to abort", reply_markup=markup)


@dp.message_handler(lambda message: (not message.text == "buy" and not message.text == "sell"),
                    state=Form.limit_direction)
async def failed_market_direction(message: types.Message):
    return await message.reply("market direction gotta be a buy or sell.\nYou want to place a buy order or a sell one?"
                               "\nWrite Cancel if you want to abort ")


@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[r'/(.*)_(.*)_limit']))
async def cmd_start(message: types.Message, state: FSMContext, regexp_command):
    """
    Conversation's entry point
    """
    # Set state
    await Form.limit_direction.set()
    await state.update_data(base=str(regexp_command.group(1)))
    await state.update_data(quote=str(regexp_command.group(2)))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("buy", "sell")

    await message.reply("You want to place a buy order or a sell one?\n"
                        "Write Cancel if you want to abort", reply_markup=markup)


@dp.message_handler(lambda message: (message.text == "buy" or message.text == "sell"),
                    state=Form1.market_direction)
async def process_market_direction(message: types.Message, state: FSMContext):
    await Form1.next()
    await state.update_data(market_direction=str(message.text))
    markup = types.ReplyKeyboardRemove()

    await message.reply("How many orders you want to be placed?"
                        "\nWrite Cancel if you want to abort", reply_markup=markup)


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form1.size)
async def failed_process_market_size(message: types.Message):
    return await message.reply("size gotta be a number.\nHow many orders you want to be placed? (digits only)"
                               "\nWrite Cancel if you want to abort")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form1.size)
async def process_market_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = float(message.text)

        # And send message
        pair = TradingPair(base=data["base"], quote=data["quote"])

        response = place_market_order(pair, data['market_direction'], data["size"])
        print(response)
        await bot.send_message(message.chat.id, response + f"\n\n use /{pair.base}_{pair.quote} to look at the "
                                                           f"orderbook ")
        # Finish conversation
        data.state = None


@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext, raw_state: Optional[str] = None):
    """
    Allow user to cancel any action
    """
    if raw_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Canceled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(lambda message: (not message.text == "buy" and not message.text == "sell"),
                    state=Form.limit_direction)
async def failed_limit_direction(message: types.Message, state: FSMContext):
    return await message.reply("limit_direction gotta be a buy or sell.\nYou want to place a buy order or a sell one?"
                               "\nWrite Cancel if you want to abort ")


@dp.message_handler(lambda message: (message.text == "buy" or message.text == "sell"),
                    state=Form.limit_direction)
async def process_limit_direction(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(limit_direction=str(message.text))
    markup = types.ReplyKeyboardRemove()

    await message.reply("What level you want order to be placed on?"
                        "\nWrite Cancel if you want to abort", reply_markup=markup)


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.price)
async def failed_process_level(message: types.Message):
    return await message.reply("level gotta be a number.\nWhat level you want order to be placed on? (digits only)"
                               "\nWrite Cancel if you want to abort")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.price)
async def process_level(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(price=float(message.text))

    await message.reply("How many orders you want to be placed?"
                        "\nWrite Cancel if you want to abort")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.size)
async def failed_process_size(message: types.Message):
    return await message.reply("size gotta be a number.\nHow many orders you want to be placed? (digits only)"
                               "\nWrite Cancel if you want to abort")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.size)
async def process_size(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = float(message.text)

        # And send message
        pair = TradingPair(base=data["base"], quote=data["quote"])
        response = place_limit_order(pair, data["limit_direction"], data["price"], data["size"])
        await bot.send_message(message.chat.id, response + f"\n\n use /{pair.base}_{pair.quote} to look at the "
                                                           f"orderbook ")
        # Finish conversation
        data.state = None


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

    answer += f"\n\n\nBIDS\n"
    for bid_limit in orderbook_bids_ask["bids"]:
        answer += f"price = {bid_limit[0]} with amount {bid_limit[1]}\n"

    answer += "\n\n\ntotal_bids_capacity = " \
              f"{orderbook.bid_capacity}\ntotal_asks_capacity = {orderbook.ask_capacity}"
    answer += f"\nif you want to place a limit order please use /{pair.base}_{pair.quote}_limit"
    answer += f"\nif you want to place a market order please use /{pair.base}_{pair.quote}_market"
    await bot.send_message(message.from_user.id, answer)


executor.start_polling(dp, skip_updates=True)

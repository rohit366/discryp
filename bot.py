import urllib.request
import requests
import time
import datetime
import hmac
import hashlib
import json
import sys
import csv
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import pytz
import itertools
from colorama import init, Fore, Back, Style
from tabulate import tabulate
init(convert=True)
import discord
import asyncio
import aiohttp
import random
from discord.ext.commands import Bot
from discord.ext import commands

api_key = os.environ["API_KEY"]
api_secret = os.environ["API_SECRET"]
bot_token = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='+', description='A bot that greets the user back.')


@bot.event
async def on_ready():
    print('I M Online! & testing')
    print('---------------')
    print('Logged in as')
    print(bot.user.name)
    print('---------------')


@bot.event
async def on_message(message):
    msg = message.content.lower()
    channel = message.channel
    words = msg.split()

    # Don't parse message if sent via PM or by the bot itself
    if message.author == bot.user or isinstance(message.channel, discord.PrivateChannel):
        return

    # Check if a possible command has been submitted
    if msg.startswith('+'):
        response = None
        cmd = words[0][1:]
        if cmd == "lms":
            try:
                a = words[1]
                print(a)
                b = words[2]
                print(b)
                c = words[3]
                print(c)
                while True:
                    print("i am here")
                    sr = float(a)
                    print(">>>>>")
                    pr = float(sr / 100000000)
                    print(">>>>>")
                    xp = float(b)
                    print(">>>>>")
                    xr = float(c)
                    print(sr)
                    print(pr)
                    print(xp)
                    print(xr)
                    print("Starting further processing")
                    btc_price = json.loads(urllib.request.urlopen("https://blockchain.info/ticker").read())['USD']['last']
                    bittrex_market_data = GetPublicRequestFromBittrex("https://bittrex.com/api/v1.1/public/getmarketsummaries")
                    market_data = json.dumps(bittrex_market_data)
                    live_market_data = pd.read_json(market_data, orient='records')
                    live_market_df = pd.DataFrame(live_market_data)
                    live_market_df['D_Cng'] = ((live_market_df['Last'] - live_market_df['High']) / live_market_df['High'] * 100)
                    live_market_df.D_Cng = live_market_df.D_Cng.astype(float)
                    live_market_df.OpenBuyOrders = live_market_df.OpenBuyOrders.astype(float)
                    live_market_df.OpenSellOrders = live_market_df.OpenSellOrders.astype(float)
                    mark = live_market_df.rename(index=str, columns={"MarketName": "Coin", "BaseVolume": "Vol", "OpenBuyOrders": "Open_Buy", "OpenSellOrders": "Open_Sell"})
                    print("blah blah")
                    sig = []
                    for index, row in live_market_df.iterrows():
                        if row['OpenBuyOrders'] <= row['OpenSellOrders']:
                            sig.append("Sell")
                        else:
                            sig.append("Buy")
                    mark['Signal'] = sig
                    mark1 = mark[mark['Coin'].str.contains("BTC") & (mark.Bid <= pr) & (mark.Bid > 0) & (mark.D_Cng >= (xp * (-1))) & (mark.Vol >= xr)].loc[:, ['Coin', 'Last', 'High', 'D_Cng', 'Vol', 'Low', 'Ask', 'Bid', 'Open_Buy', 'Open_Sell', 'Signal']].sort_values('Last', ascending=True)
                    mark1['D_Cng'] = mark1['D_Cng'].round(2).apply(lambda x: str(x) + '%')
                    mark1['Vol'] = mark1['Vol'].round(2)
                    bt_pr = ("Current BTC Price: $ **{:.2f}**".format(btc_price))
                    lmsd = mark1.loc[:, ['Coin', 'Last', 'High', 'D_Cng', 'Vol', 'Low', 'Ask', 'Bid', 'Open_Buy', 'Open_Sell', 'Signal']]
                    print("trying the print btc price")
                    embd = discord.Embed(title="BTC Prices", description=bt_pr, colour=0xFF9900)
                    await bot.send_message(channel, embed=embd)
                    for i in range(len(lmsd.index)):
                        coin = lmsd['Coin'].iloc[i]
                        last = lmsd['Last'].iloc[i]
                        high = lmsd['High'].iloc[i]
                        dcng = lmsd['D_Cng'].iloc[i]
                        vol = lmsd['Vol'].iloc[i]
                        low = lmsd['Low'].iloc[i]
                        ask = lmsd['Ask'].iloc[i]
                        bid = lmsd['Bid'].iloc[i]
                        ob = lmsd['Open_Buy'].iloc[i]
                        os = lmsd['Open_Sell'].iloc[i]
                        sgn = lmsd['Signal'].iloc[i]
                        msg = ("Coin: **{}**\n" "Last Was: **{:.8f}**\n" "24 Hr High: **{:.8f}**\n" "Daily Change: **{}**\n" "Cur Vol: **{:.2f}**\n" "Low Was: **{:.8f}**\n" "Cur Ask: **{:.8f}**\n" "Cur Bid: **{:.8f}**\n" "Open Buy: **{:.0f}**\n" "Open Sell: **{:.0f}**\n" "Signal: **{}**\n".format(coin, last, high, dcng, vol, low, ask, bid, ob, os, sgn))
                        emb = discord.Embed(title="Live Market Summary", description=msg, colour=0xFF9900)
                        print("trying to print the pandas data")
                        await bot.send_message(channel, embed=emb)
                    await asyncio.sleep(180)
            except:
                err = fmtError("The `+lms` command must be formatted like this: `+lms <satoshi_range> <daily_change> <volume>`\n\n Example: `+lms 100 20 2`")
                await bot.send_message(channel, embed=err)
                return

        elif cmd == "bal":
            try:
                btc_price = json.loads(urllib.request.urlopen("https://blockchain.info/ticker").read())['USD']['last']
                my_balances = GetPrivateRequestForBittrex("https://bittrex.com/api/v1.1/account/getbalances", api_key, api_secret)
                my_balances_data = json.dumps(my_balances)
                balance_data = pd.read_json(my_balances_data, orient='records')
                balance_df = pd.DataFrame(balance_data)
                balance_data_1 = balance_df[balance_df.Available > 0].loc[:, ['Currency', 'Available']]
                blist = balance_df.loc[(balance_df.Available > 0) & (balance_df.Currency != 'USDT') & (balance_df.Currency != 'BTC'), 'Currency'].tolist()
                cur_price = []
                pairs = []
                for pair in blist:
                    if pair is not None:
                        coin = last_price = GetPublicRequestFromBittrex("https://bittrex.com/api/v1.1/public/getticker?market=BTC-" + pair)['Last']
                        cur_price.append(coin)
                        pairs.append(pair)
                    else:
                        print("Either You Have Open Orders Or You Don't Have Any Coins")
                data_tuples1 = list(zip(pairs, cur_price))
                cp_df = pd.DataFrame(data_tuples1, columns=['Currency', 'Price_Now'])
                pfoli_df = pd.merge(balance_data_1, cp_df, on='Currency')
                pfoli_df['BTC_On_Sell'] = (pfoli_df['Available'] * pfoli_df['Price_Now'])
                pfoli_df['USD_On_Sell'] = (pfoli_df['BTC_On_Sell'] * btc_price).round(2).apply(lambda x: '$' + str(x))
                mybal = pfoli_df.loc[:, ['Currency', 'Available', 'Price_Now', 'BTC_On_Sell', 'USD_On_Sell']]
                mybal.USD_On_Sell = mybal.USD_On_Sell.astype(str)
                bt_pr = ("Current BTC Price: $ **{:.2f}**".format(btc_price))
                emb = discord.Embed(title="BTC Prices", description=bt_pr, colour=0xFF9900)
                await bot.send_message(channel, embed=emb)
                #table = mybal.to_html(classes='table', index=False, escape=False)
                #em = discord.Embed(title="Balances", description=table, colour=0xFF9900)
                # await bot.send_message(channel, embed=em)
                for i in range(len(mybal.index)):
                    coin = mybal['Currency'].iloc[i]
                    amt = mybal['Available'].iloc[i]
                    pn = mybal['Price_Now'].iloc[i]
                    bamt = mybal['BTC_On_Sell'].iloc[i]
                    damt = mybal['USD_On_Sell'].iloc[i]
                    msg = ("Coin: **{}**\n" "Available Balance: **{:.2f}**\n" "Current Price: **{:.8f}**\n" "BTC on sell: **{:.8f}**\n" "USD on sell: **{}**\n".format(coin, amt, pn, bamt, damt))
                    em = discord.Embed(title="Balances", description=msg, colour=0xFF9900)
                    await bot.send_message(channel, embed=em)
            except:
                errs = fmtError("The `+bal` command is not working")
                await bot.send_message(channel, embed=errs)
                return

        elif cmd == "mob":
            try:
                btc_price = json.loads(urllib.request.urlopen("https://blockchain.info/ticker").read())['USD']['last']
                my_orders = GetPrivateRequestForBittrex("https://bittrex.com/api/v1.1/account/getorderhistory", api_key, api_secret)
                open_orders = GetPrivateRequestForBittrex("https://bittrex.com/api/v1.1/market/getopenorders", api_key, api_secret)
                my_orders_data = json.dumps(my_orders)
                order_data = pd.read_json(my_orders_data, orient='records')
                order_df = pd.DataFrame(order_data)
                order_df['Closed'] = pd.to_datetime(order_df['Closed']).replace(to_replace=['-'], value='/', inplace=False).apply(lambda x: x.strftime('%d/%h/%Y'))
                order_data_1 = order_df.loc[:, ['Exchange', 'OrderType', 'Limit', 'Quantity', 'Commission', 'PricePerUnit', 'Price', 'Closed']].sort_values('Quantity', ascending=True)
                obk = order_data_1.loc[:, ['Exchange', 'OrderType', 'Limit', 'Quantity', 'Commission', 'PricePerUnit', 'Price', 'Closed']]
                bt_pr = ("Current BTC Price: $ **{:.2f}**".format(btc_price))
                emb = discord.Embed(title="BTC Prices", description=bt_pr, colour=0xFF9900)
                await bot.send_message(channel, embed=emb)
                for i in range(len(obk.index)):
                    coin = obk['Exchange'].iloc[i]
                    ot = obk['OrderType'].iloc[i]
                    lm = obk['Limit'].iloc[i]
                    qun = obk['Quantity'].iloc[i]
                    comm = obk['Commission'].iloc[i]
                    ppu = obk['PricePerUnit'].iloc[i]
                    pri = obk['Price'].iloc[i]
                    cld = obk['Closed'].iloc[i]
                    msg = ("Coin: **{}**\n" "Order Type: **{}**\n" "At Limit: **{:.8f}**\n" "Quantity Was: **{:.2f}**\n" "Commission Paid: **{:.8f}**\n" "PPU Was: **{:.8f}**\n" "Final Price Was: **{:.8f}**\n" "On Date: **{}**\n".format(coin, ot, lm, qun, comm, ppu, pri, cld))
                    em = discord.Embed(title="My Order Book", description=msg, colour=0xFF9900)
                    await bot.send_message(channel, embed=em)
            except:
                errs = fmtError("The `+mob` command is not working")
                await bot.send_message(channel, embed=errs)
                return


def fmtError(error):
    embed = discord.Embed(title="There was an error", description=error, color=0xFF9900)
    embed.set_footer(text="For more information about rohit's bot, type +help")

    return embed


def ParseBittrexResponse(response_text, debug=False):
    '''Parses both public and private Bittrex JSON responses and returns None if failure.'''
    result = json.loads(response_text)
    if (result['success'] != True):
        print("Failed response:", response_text)
        debug = True
        result = None
    else:
        result = result['result']
    return result


def GetPrivateRequestForBittrex(request_url, api_key, api_secret, debug=False):
    '''Submits a private request to Bittrex, returns a parsed response or None if failure.'''

    def BuildPrivateRequestForBittrex(url_root):
        '''
        Helper function to append Bittrex authentication info to the request URL.
        Parameter "url_root" is a request URL string such as "https://bittrex.com/api/v1.1/account/getbalances"
        Returns a request object from urllib.request.Request() with necessary headers.
        The request is authenticated by adding api_key and nonce to the request URL.
        '''
        nonce = str(time.time())
        request_url = url_root
        if ('?' not in request_url):
            request_url += '?'
        if (request_url[-1] != '?'):
            request_url += '&'
        request_url += "apikey=" + api_key + "&nonce=" + nonce

        hash = hmac.new(bytes(api_secret, 'utf-8'),
                        bytes(request_url, 'utf-8'), hashlib.sha512).hexdigest()
        request_obj = urllib.request.Request(request_url)
        request_obj.add_header('apisign', hash)
        return request_obj

    request_obj = BuildPrivateRequestForBittrex(request_url)
    response = urllib.request.urlopen(request_obj)
    response_text = response.read()
    result = ParseBittrexResponse(response_text, debug)
    if result == None:
        debug = True
    if debug:
        print(response.geturl())
        print(response.info())
        print(response.getcode())
    return result


def GetPublicRequestFromBittrex(url, debug=False):
    '''Submits a public request to Bittrex, returns the parsed response object.'''
    response_text = urllib.request.urlopen(url).read()
    result = ParseBittrexResponse(response_text, debug)
    if result == None:
        debug = True
    if debug:
        print(url)
    return result


def GetLastPriceFromBittrex(market, debug=False):
    '''
    Gets the last price traded for the given Bittrex market.
    Parameter "market" is a string, can be found in Bittrex URLs. Ex: "USDT-ETH"
    '''
    last_price = None
    try:
        last_price = GetPublicRequestFromBittrex(
            "https://bittrex.com/api/v1.1/public/getorderbook?market=" + market)['Last']
    except:
        print("Error, market probably not found:", market)
    return last_price

bot.run(bot_token)
#bot.run(TOKEN)

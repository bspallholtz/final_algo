import json
import re
from sqlite3.dbapi2 import DatabaseError
import rh_lib as r
import log_lib
import yahoo_lib as y
import database_lib as d
import tipranks_lib as t
import finviz
import datetime
import os
import time

log = log_lib.write_log
r.login()
today = datetime.date.today().strftime("%m_%d_%Y")

def start():
    if os.path.isdir('data') is False:
        os.mkdir('data')
    symbols = finviz.get_new()
    log('INFO', 'Initially found {} symbols'.format(len(symbols)))
    with open('data/finviz_symbols_{}.json'.format(today), 'w') as f:
        for symbol in symbols:
            f.write(symbol + '\n')
    return True

def second():
    data = {}
    with open('data/finviz_symbols_{}.json'.format(today)) as f:
        finviz_symbols = f.readlines()
    total_symbols = len(finviz_symbols)
    rejected = []
    for symbol in sorted(finviz_symbols):
        symbol = symbol.rstrip()
        rh_data = r.get_rh_rating(symbol, 5, 80)
        if rh_data is False:
            log('INFO', '{symbol} - Has no data from RH , removing from Analysis'.format(symbol=symbol))
            rejected.append(symbol)
            log('INFO', 'RH has rejected {}/{} symbols'.format(len(rejected),total_symbols))
            continue
        data[symbol] = {}
        data[symbol]['rh_buy_analysts'] = rh_data[1]
        data[symbol]['rh_total_analysts'] = rh_data[2]
        data[symbol]['rh_percent_buy'] = rh_data[3]
    with open('data/rh_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)
    return True

def third():
    rh_symbols = open('data/rh_data_{}.json'.format(today), 'r')
    data = json.loads(rh_symbols.read())
    total_symbols = len(data.keys())
    rejected = []
    print('Evaluating {} symbols'.format(total_symbols))
    for symbol in list(data.keys()):
        y_data = y.get_yahoo_rating(symbol,min_avg=80,min_analysts=5)
        if y_data is False:
            rejected.append(symbol)
            print('Yahoo has rejected {}/{} symbols'.format(len(rejected),total_symbols))
            del data[symbol]
            continue
        data[symbol]['yahoo_number_analysts'] = y_data[1]
        data[symbol]['yahoo_percent_buys'] = y_data[2]
        data[symbol]['yahoo_number_buy_analysts'] = y_data[3]
    with open('data/yahoo_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)
    return True

def fourth():
    yahoo_symbols = open('data/yahoo_data_{}.json'.format(today), 'r')
    data = json.loads(yahoo_symbols.read())
    total_symbols = len(data.keys())
    log('INFO', 'Evaluating {} symbols'.format(total_symbols))
    t_data = t.new(data.keys(),total_symbols,min_per=30)
    for symbol in list(data.keys()):
        if symbol not in t_data.keys():
            del data[symbol]
    for symbol in t_data.keys():
        #data[symbol]['tipranks_tp'] = t_data[symbol]['tipranks_tp']
        #data[symbol]['tipranks_tp_percent'] = t_data[symbol]['tipranks_tp_percent']
        #data[symbol]['tipranks_smart_string'] = t_data[symbol]['tipranks_smart_string']
        data[symbol]['tipranks_smart_score'] = t_data[symbol]['tipranks_smart_score']
        #data[symbol]['tipranks_fundementals'] = t_data[symbol]['tipranks_fundementals']
        #data[symbol]['tipranks_sediment'] = t_data[symbol]['tipranks_sediment']
    with open('data/tiprank_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)

def fifth():
    tiprank_data = open('data/tiprank_data_{}.json'.format(today), 'r')
    data = json.loads(tiprank_data.read())
    for symbol in data.keys():
        finviz_recom, finviz_tp = finviz.individual(symbol)
        data[symbol]['finviz_recom'] = finviz_recom
        data[symbol]['finviz_tp'] = finviz_tp
        cp = r.get_price(symbol)
        finviz_tp_per = round((((finviz_tp - cp) * 100) / cp), 2)
        data[symbol]['cp'] = cp
        data[symbol]['finviz_tp_percent'] = finviz_tp_per
    with open('data/final_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)

def sixth(data=None):
    if data is None:
        data = open('data/final_data_{}.json'.format(today), 'r')
    current_buys = json.loads(data.read())
    log('INFO', 'There are {} buys'.format(len(data.keys())))
    open_positions = d.get_all_open()
    for symbol in data.keys():
        if symbol not in open_positions:
            log('INFO', '{symbol} - Buying symbol {symbol}'.format(symbol=symbol))
            if d.execute_trade(symbol,data[symbol], action='buy') is False:
                return False
            if r.buy(symbol) is False:
                return False
            else:
                print('bought {}'.format(symbol))
                time.sleep(5)
        else:
            if d.execute_trade(symbol,data[symbol], action='hold') is False:
                return False
        if symbol not in d.get_all_buys():
            d.update_buy_status(symbol)
    return True

def seven(data=None):
    if data is None:
        data = open('data/final_data_{}.json'.format(today), 'r')
    data = json.loads(data.read())
    open_positions = d.get_all_open()
    for symbol in open_positions:
        if symbol not in data.keys():
            d.update_buy_status(symbol,still_buy=False)
        if d.is_symbol_still_buy(symbol) == 'False':
            buy_price = d.get_buy_price(symbol)
            cp = r.get_price(symbol)
            profit = round(( cp - buy_price),2)
            percent_profit = round((((cp - buy_price) / buy_price) * 100),2)
            if percent_profit < -30 or percent_profit > 100:
                cp = r.get_price(symbol)
                d.execute_sell(symbol,cp)
                d.set_to_closed(symbol)
    r_open = r.get_open_symbols()
    unbought = list(set(open_positions) - set(r_open))
    for symbol in unbought:
        log('INFO', '{} - Buying {}'.format(symbol,symbol))
        if r.buy(symbol) is False:
            return False
            

start()
second()
third()
fourth()
fifth()
sixth()
seven()

import json
from symtable import Symbol
import rh_lib as r
import log_lib
import yahoo_lib as y
import database_lib as d
import tipranks_lib as t
import finviz
import datetime
import os
import time
import concurrent.futures
import zacks_lib


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

def do_yahoo(symbol):
     return y.get_yahoo_rating(symbol,min_avg=80,min_analysts=5)

def third():
    rh_symbols = open('data/rh_data_{}.json'.format(today), 'r')
    data = json.loads(rh_symbols.read())
    total_symbols = len(data.keys())
    rejected = []
    print('Evaluating {} symbols'.format(total_symbols))
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = [executor.submit(do_yahoo, param) for param in list(data)]
        results = [f.result() for f in future]
    for entry in results:
        for symbol,v in entry.items():
            if v['buy'] is False:
                rejected.append(symbol)
                del data[symbol]
                print('Yahoo has rejected {}/{} symbols'.format(len(rejected),total_symbols))
                continue
            data[symbol]['yahoo_number_analysts'] = v['number_of_analysts']
            data[symbol]['yahoo_percent_buys'] = v['per_buys']
            data[symbol]['yahoo_number_buy_analysts'] = v['analysts_buys']
    with open('data/yahoo_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)
    return True

def fourth():
    yahoo_symbols = open('data/yahoo_data_{}.json'.format(today), 'r')
    data = json.loads(yahoo_symbols.read())
    total_symbols = len(data.keys())
    log('INFO', 'Evaluating {} symbols'.format(total_symbols))
    zacks_data = zacks_lib.batch(data.keys())
    print(zacks_data)
    for symbol in zacks_lib.batch(data.keys()):
        print(symbol)
        exit()
    with open('data/zacks_data_{}.json'.format(today), 'w') as f:
        json.dump(data, f)


def fifth():
    tiprank_data = open('data/zacks_data_{}.json'.format(today), 'r')
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
    data = json.loads(data.read())
    log('INFO', 'There are {} buys'.format(len(data.keys())))
    print(json.dumps(data))
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
#fifth()
#sixth()
#seven()

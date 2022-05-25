import requests
from bs4 import BeautifulSoup
import time

import log_lib as l

data_sources = { 'strongbuy': { 'tp': [ 50, 40, 30 ]}, 'buybetter' : { 'tp': [ 50, 40, 30]}, 'buy' : { 'tp': [ 50, 40, 30 ]}}

log = l.write_log

def get_an_recom(an_recom=None):
    """Make sure any an_recom passed to this Funciton is one of the possible"""
    possible = [ 'strongbuy', 'buybetter', 'buy' ]
    if an_recom is None:
        an_recom = 'strongbuy'
    if isinstance(an_recom, str) is False:
        an_recom = 'strongbuy'
    if an_recom not in possible:
        an_recom = 'strongbuy'
    return an_recom
    
def get_cap( cap=None):
    """Make sure any market cap passed is good"""
    possible = [ 'microover', 'smallover', 'midover', 'largeover' ]
    if cap is None:
        cap = 'midover'
    if isinstance(cap, str) is False:
        cap = 'midover'
    if cap not in possible:
        cap = 'midover'
    return cap

def get_target( target=None):
    """Make sure the target priced passed is correct"""
    possible = [ 50 , 40 , 30 ]
    if target is None:
        target = 50
    try:
        target = int(target)
    except ValueError:
        target = 50
    if target not in possible:
        target = 50
    return str(target)

def get_symbol_data(end):
    """For a FinViz URL return the Symbols it finds"""
    response = requests.get(end, headers={'User-Agent': 'curl/7.61.1','Accept': '*/*'})
    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.prettify()
    data = data.partition('<!-- TS')
    final = ''
    for x in data:
        if 'TE -->' in x:
            final = x.partition('TE -->')[0]
            break
    if len(final) == 0:
        return None
    lines = final.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    symbols = []
    for symbol in non_empty_lines:
        symbols.append(symbol.split('|')[0])
    return symbols

def get_new():
    end = 'https://finviz.com/screener.ashx?v=111&f=an_recom_buybetter,cap_smallover,geo_usa,sh_price_o5,targetprice_a30&ft=4'
    symbols = []
    r = 1
    symbol_data = get_symbol_data(end)
    if symbol_data is None:
        return []
    symbols.extend(symbol_data)
    hold = False
    while hold is False:
        r = r + 20
        end = 'https://finviz.com/screener.ashx?v=111&f=an_recom_buybetter,cap_smallover,geo_usa,sh_price_o5,targetprice_a30&ft=4&r={r}'.format(r=r)
        symbol_data = get_symbol_data(end)
        if symbol_data is None:
            hold = True
        elif len(symbol_data) == 1:
            symbols.extend(symbol_data)
            hold = True
        else:
            symbols.extend(symbol_data)
            time.sleep(1)
    return sorted(set(symbols))
    

def individual( symbol):
    """Return information on an individual symbol"""
    end = 'https://finviz.com/quote.ashx?t={symbol}'.format(symbol=symbol)
    response = requests.get(end, headers={'User-Agent': 'curl/7.61.1','Accept': '*/*'})
    soup = BeautifulSoup(response.text, "html.parser")
    columns = soup.find_all("table")
    data = soup.prettify()
    data = data.splitlines()
    for index, line in enumerate(data):
        if "Analysts' mean recommendation (1=Buy 5=Sell)" in line:
            recom = data[index + 5]
            recom = recom.replace(" ", "")
            if 'spanclass=' in recom:
                recom = data[index + 6]
            recom = recom.replace(" ", "")    
            if recom == '-':
                recom = 0
        if "Analysts' mean target price" in line:
            tp = data[index + 6].replace(" ", "")
            if tp == '</b>':
                tp = 1
    return float(recom), float(tp)
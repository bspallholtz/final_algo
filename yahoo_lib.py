import datetime
import json
import yfinance as yf

import log_lib as l
log = l.write_log



worst = ['Sell']
bad = [ 'Underweight' ,'Underperform']
neutrals = ['Neutral', 'Equal-Weight', 'Hold' ,'In-Line','Market Perform','Perform', 'Sector Perform', 'Peer Perform','Sector Weight']
buys = [ 'Buy']
better_buys = ['Overweight']
outpreform = ['Outperform', 'Market Outperform','Sector Outperform', 'Positive']
strong_buys = ['Strong Buy']
oldest_analyst = datetime.datetime.now() + datetime.timedelta(days=-180)
oldest_analyst = oldest_analyst.timestamp()

def check_yahoo_data(data, symbol):
    try:
        data = data.recommendations
    except IndexError:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    except AttributeError:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    except KeyError:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    except:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    try:
        data = data.to_json(orient="split")
    except AttributeError:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    return data

def new_hotness(symbols):
    final = {}
    tickers = yf.Tickers(symbols)
    for symbol in tickers.tickers.keys():
        recom = tickers.tickers[symbol]
        data = check_yahoo_data(recom, symbol)
        if data is not False:
            final[symbol] = {}
            final[symbol]['data'] = really_new(data,symbol)
    return final
            

def really_new(data,symbol,min_avg=0, min_analysts=0,update=False):
    data = json.loads(data)
    start = None
    for index, date in enumerate(data['index']):
        date = int(str(date)[:-3])
        if date > oldest_analyst:
            start = index
            break
    grades = []
    analysts_buys = 0
    if start is None:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return False
    for firm in data['data'][start:]:
        firm_name = firm[0]
        grade = firm[1]
        log("INFO", "{symbol} - Looking at firm {firm_name} for symbol {symbol} with grade {grade}".format(symbol=symbol,firm_name=firm_name,grade=grade))
        if grade in strong_buys:
            grades.append(1)
            analysts_buys += 1
        elif grade in outpreform:
            grades.append(0.5)
            analysts_buys += 1
        elif grade in better_buys:
            grades.append(0.25)
            analysts_buys += 1
        elif grade in buys:
            grades.append(0.125)
            analysts_buys += 1
        elif grade in neutrals:
            grades.append(0)
        elif grade in bad:
            grades.append(-0.5)
        elif grade in worst:
            grades.append(-1)
        else:
            log("INFO", '{symbol} - Firm {firm_name} had the grade {grade}, which is not supported now'.format(firm_name=firm_name,grade=grade, symbol=symbol))
        if grade is None:
            log("INFO", '{symbol} - Failed to set a grade to_grade = {grade} analyst is {firm_name}'.format(symbol=symbol,grade=grade,firm_name=firm_name))
            return False
    number_of_analysts = len(grades)
    per_buys = round(analysts_buys / number_of_analysts * 100, 2)
    if per_buys < min_avg:
        log("DEBUG", '{} - Has {} analysts covering it , {} analysts mark it as a buy or {}% , the minimum percent is {}, removing from further analysis'.format(symbol,len(grades), analysts_buys, per_buys, min_avg))
        if update == 'update':
            return True, number_of_analysts, per_buys, analysts_buys
        return False
    if analysts_buys < min_analysts:
        log("DEBUG", '{} - Has {} analysts covering it , {} analysts mark it as a buy, the minimum number of analysts that need to mark it as a buy is {}, removing it from further analysis'.format(symbol, len(grades), analysts_buys, min_analysts))
        if update == 'update':
            return True, number_of_analysts, per_buys, analysts_buys
        return False
    log("INFO", '{} - Has {} analysts covering it , {} mark it as a buy or {}%'.format(symbol,number_of_analysts, analysts_buys, per_buys))
    return True, number_of_analysts, per_buys, analysts_buys

def get_yahoo_rating(symbol, min_avg=0, min_analysts=0,update=False):
    """Get a yahoo rating for a symbol"""
    log("INFO", "{symbol} - Starting yahoo analysis of {symbol}".format(symbol=symbol))
    oldest_analyst = datetime.datetime.now() + datetime.timedelta(days=-180)
    oldest_analyst = oldest_analyst.timestamp()
    data = yf.Ticker(symbol)
    data = check_yahoo_data(data, symbol)
    if data is False:
        return {symbol :{ 'buy': False }}
    data = json.loads(data)
    start = None
    for index, date in enumerate(data['index']):
        date = int(str(date)[:-3])
        if date > oldest_analyst:
            start = index
            break
    grades = []
    analysts_buys = 0
    if start is None:
        log("INFO", "{symbol} - Bad Yahoo data for symbol {symbol}".format(symbol=symbol))
        return {symbol :{ 'buy': False }}
    for firm in data['data'][start:]:
        firm_name = firm[0]
        grade = firm[1]
        log("INFO", "{symbol} - Looking at firm {firm_name} for symbol {symbol} with grade {grade}".format(symbol=symbol,firm_name=firm_name,grade=grade))
        if grade in strong_buys:
            grades.append(1)
            analysts_buys += 1
        elif grade in outpreform:
            grades.append(0.5)
            analysts_buys += 1
        elif grade in better_buys:
            grades.append(0.25)
            analysts_buys += 1
        elif grade in buys:
            grades.append(0.125)
            analysts_buys += 1
        elif grade in neutrals:
            grades.append(0)
        elif grade in bad:
            grades.append(-0.5)
        elif grade in worst:
            grades.append(-1)
        else:
            log("INFO", '{symbol} - Firm {firm_name} had the grade {grade}, which is not supported now'.format(firm_name=firm_name,grade=grade, symbol=symbol))
        if grade is None:
            log("INFO", '{symbol} - Failed to set a grade to_grade = {grade} analyst is {firm_name}'.format(symbol=symbol,grade=grade,firm_name=firm_name))
            return {symbol :{ 'buy': False }}
    number_of_analysts = len(grades)
    per_buys = round(analysts_buys / number_of_analysts * 100, 2)
    if per_buys < min_avg:
        log("DEBUG", '{} - Has {} analysts covering it , {} analysts mark it as a buy or {}% , the minimum percent is {}, removing from further analysis'.format(symbol,len(grades), analysts_buys, per_buys, min_avg))
        if update == 'update':
            return { symbol: { 'buy': True, 'number_of_analysts': number_of_analysts, 'per_buys': per_buys, 'analysts_buys': analysts_buys } }
        return {symbol :{ 'buy': False }}
    if analysts_buys < min_analysts:
        log("DEBUG", '{} - Has {} analysts covering it , {} analysts mark it as a buy, the minimum number of analysts that need to mark it as a buy is {}, removing it from further analysis'.format(symbol, len(grades), analysts_buys, min_analysts))
        if update == 'update':
            return { symbol: { 'buy': True, 'number_of_analysts': number_of_analysts, 'per_buys': per_buys, 'analysts_buys': analysts_buys } }
        return {symbol :{ 'buy': False }}
    log("INFO", '{} - Has {} analysts covering it , {} mark it as a buy or {}%'.format(symbol,number_of_analysts, analysts_buys, per_buys))
    return { symbol: { 'buy': True, 'number_of_analysts': number_of_analysts, 'per_buys': per_buys, 'analysts_buys': analysts_buys } }
    
def get_voo_profit(first_date):
    """Return the profit of S&P 500 from a given date"""
    voo = yf.Ticker("VOO")
    voo_old = voo.history(start=first_date)['Close'][0]
    voo_current = get_current_price('VOO')
    voo_return = round((((voo_current - voo_old) / voo_old) * 100), 2)
    log('INFO', 'From {first_date} to today the S&P 500 returned {voo_return}%'.format(first_date=first_date,voo_return=voo_return))
    return voo_return

def get_voo_price(first_date,symbol='VOO'):
    """Return the profit of S&P 500 from a given date"""
    voo = yf.Ticker(symbol)
    return voo.history(start=first_date)['Close'][0]

def get_high(first_date,symbol):
    """Return the high of a symbol since the buy date"""
    symbol_data = yf.Ticker(symbol)
    if symbol_data is None:
        return False
    try:
        symbol_data = symbol_data.history(start=first_date, end=datetime.datetime.today().strftime('%Y-%m-%d'))['Close']
    except ValueError:
        return False
    try:
        result = json.loads(symbol_data.to_json(orient='split'))
    except ValueError:
        return False
    result = result['data']
    final = [ i for i in result if i ]
    return round(max(final),2)

def get_current_price(symbol):
    """ Get the last traded price of a given symbol"""
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    current_price = todays_data['Close'][0]
    log('INFO', '{symbol} - Got the last traded price of {current_price} for {symbol}'.format(symbol=symbol,current_price=current_price))
    return current_price
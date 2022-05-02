from robin_stocks import robinhood as r
import pyotp

import log_lib as l
import lib

log = l.write_log

def login():
    """Always login when this class is called"""
    rh_username, rh_password,gmail_username, gmail_password, rh_mfa = lib.get_creds()
    totp  = pyotp.TOTP(rh_mfa).now()
    try:
        r.login(rh_username, rh_password, mfa_code=totp)            
    except Exception as e:
        r.login(rh_username, rh_password)
        log('INFO', 'Failed to login due to {e}'.format(e=e))
        return None
    else:
        return True

def get_rh_rating(symbol, min=0, min_avg=0,update=False):
    """Given a symbol, retunr a RH rating"""
    data = r.stocks.get_ratings(symbol, info=None)
    if isinstance(data, str) is True:
        data = data.rstrip('\n')
        if len(data) == 0:
            log('DEBUG', '{symbol} - For symbol {symbol}, did not get rh rating'.format(symbol=symbol))
            return False
    if data is None:
        log('DEBUG', '{symbol} - For symbol {symbol}, did not get rh rating'.format(symbol=symbol))
        return False
    if data['summary'] is None:
        log('DEBUG', '{symbol} - For symbol {symbol}, did not get rh rating'.format(symbol=symbol))
        return False
    buy = data['summary']['num_buy_ratings']
    hold = data['summary']['num_hold_ratings']
    sell = data['summary']['num_sell_ratings']
    total = buy + hold + sell
    rh_percent_buy = round((buy / total) * 100,2)
    if total <= min:
        log('DEBUG', '{} - Only {} analysts covering it which does not meet the min of {} removing it from futher analysis'.format(symbol, total, min))
        return False
    if rh_percent_buy < min_avg:
        log('DEBUG', '{} - Only {} analysts out of the total of {} analysts covering the symbol mark it as a \'BUY\'  which is {}% , this does not meet the min percentage of {}%, so removing it from futher analysis'.format(symbol, buy, total, rh_percent_buy, min_avg))
        if update == 'update':
            return True, buy, total, rh_percent_buy
        return False
    else:
        return True, buy, total, rh_percent_buy
    
def get_price(symbol):
    "Get a price for any given symbol"
    try:
        price = float(r.stocks.get_quotes(symbol)[0]['last_trade_price'])
    except TypeError:
        return False
    return price
    
def get_cap(symbol):
    "Get the market cap for any given symbol"
    try:
        cap = float(r.stocks.get_fundamentals(symbol, info='market_cap')[0].split('.')[0])
    except TypeError:
        return False
    return cap
    
def get_open_symbols():
    open_symbols = []
    open_positions = r.account.get_open_stock_positions()
    for position in open_positions:
        instrument_url = position['instrument']
        symbol = r.stocks.get_symbol_by_url(instrument_url)
        open_symbols.append(symbol)
    return open_symbols
    
def buy(symbol,amount=1.00):
    buying_power = float(r.account.load_phoenix_account(info='account_buying_power')['amount'])
    if buying_power < 1:
        return False
    return(r.orders.order_buy_fractional_by_price(symbol,amount,extendedHours=True))

login()
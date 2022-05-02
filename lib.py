import os
import configparser
import database_lib as d
import yahoo_lib as y

cred_file = '.saver.cfg'
config = configparser.ConfigParser()
    
def prompt_creds():
    """If the cred file isn't in the correct state, prompt the user to provide the creds"""
    if os.path.isfile(cred_file):
        os.remove(cred_file)
    username = input ("Enter RobinHood username: ")
    password = input ("Enter RobinHood password: ")
    mfa = input ("Enter RobinHood mfa code: ")
    username = input ("Enter Gmail username: ")
    password = input ("Enter Gmail password: ")
    config.add_section('ROBINHOOD')
    config.add_section('GMAIL')
    config['ROBINHOOD']['username'] = username
    config['ROBINHOOD']['password'] = password
    config['ROBINHOOD']['mfa'] = mfa
    config['GMAIL']['username'] = username
    config['GMAIL']['password'] = password
    with open(cred_file, 'w') as configfile:
        config.write(configfile)
    return True
    
def get_creds():
    """Get credentials needed to run this code"""
    if os.path.isfile(cred_file) is False:
        prompt_creds()
    config.read(cred_file)
    if config.has_section('ROBINHOOD') is False:
        prompt_creds()
    if config.has_section('GMAIL') is False:
        prompt_creds()
    if config.has_option('ROBINHOOD', 'username') is False:
        prompt_creds()
    if config.has_option('ROBINHOOD', 'password') is False:
        prompt_creds()
    if config.has_option('GMAIL', 'username') is False:
        prompt_creds()
    if config.has_option('GMAIL', 'password') is False:
        prompt_creds()
    rh_username = config['ROBINHOOD']['username']
    rh_password = config['ROBINHOOD']['password']
    rh_mfa = config['ROBINHOOD']['mfa']
    gmail_username = config['GMAIL']['username']
    gmail_password = config['GMAIL']['password']
    return rh_username,rh_password,gmail_username,gmail_password, rh_mfa
    
def get_total_profit():
    all_symbols = d.get_symbols(star=4)
    total_buy = 0
    total_current = 0
    for symbol in all_symbols:
        if d.detect_symbol_state(symbol) == 'open':
            buy_price, current_price = d.get_symbol_cost(symbol)
            total_buy += buy_price
            total_current += current_price
    return round((((total_current - total_buy ) / total_buy) * 100),2)
    
def get_closed_profit():
    closed_symbols = d.get_closed_positions()
    data = {}
    data['total_buy'] = 0
    data['total_sell'] = 0
    for symbol in closed_symbols:
        data[symbol] = {}
        buy_data = d.get_action_data(symbol,'buy')
        sell_data = d.get_action_data(symbol,'sell')
        data[symbol]['buy_date'] = buy_data[2]
        data[symbol]['buy_price'] = buy_data[3]
        data[symbol]['sell_date'] = sell_data[2]
        data[symbol]['sell_price'] = sell_data[3]
        data['total_buy'] =+ data[symbol]['buy_price']
        data['total_sell'] =+ data[symbol]['sell_price']
        data[symbol]['profit'] = round((data[symbol]['sell_price'] - data[symbol]['buy_price']),2)
        data[symbol]['percent_profit'] = round((((data[symbol]['sell_price'] - data[symbol]['buy_price'] ) / data[symbol]['buy_price']) * 100),2)
    return data
    
def calculate_profit():
    total_buy = 0
    total_cp = 0
    first_date = d.find_first_trade()
    voo_profit = y.get_voo_profit(first_date)
    all_open = d.get_all_open()
    rows = []
    for symbol in all_open:
        state = d.detect_symbol_state(symbol)
        if state == 'closed':
            continue
        last_trade = d.get_latest_data(symbol)
        if last_trade is None:
            continue
        last_trade['symbol'] = symbol
        buy_price = d.get_buy_price(symbol)
        buy_date = d.get_buy_date(symbol)
        last_trade['buy_price'] = buy_price
        last_trade['action_date'] = buy_date
        last_trade['profit'] = round(( last_trade['cp'] - last_trade['buy_price']),2)
        last_trade['percent_profit'] = round((((last_trade['cp'] - last_trade['buy_price'] ) / last_trade['buy_price']) * 100),2)
        last_trade['buy_state'] = d.is_symbol_still_buy(symbol)
        total_buy += last_trade['buy_price']
        total_cp += last_trade['cp']
        del last_trade['id']
        del last_trade['action']
        rows.append(last_trade)
    total_cp = round(total_cp, 2)
    total_buy = round(total_buy, 2)
    total_profit = round(( total_cp - total_buy),2)
    total_percent = round((((total_cp - total_buy ) / total_buy) * 100),2)
    data = {\
        'total_profit': total_profit, \
        'total_percent': total_percent, \
        'total_cp':total_cp, \
        'total_buy':total_buy,\
        'first_date':first_date, \
        'total_open': len(d.get_all_open()),\
        'voo_profit': voo_profit,\
        'first_date': first_date,\
        'rows': rows
    }
    return data

def todays_buys():
    todays_buys = d.get_today_buys()
    if todays_buys is None:
        return None
    for symbol in todays_buys:
        profit = round(( symbol['cp'] - symbol['action_price']),2)
        percent_profit = round((((symbol['cp'] - symbol['action_price'] ) / symbol['action_price']) * 100),2)
        todays_buys[symbol]['profit'] = profit
        todays_buys[symbol]['percent_profit'] = percent_profit
        todays_buys[symbol]['buy_state'] = True
    return todays_buys
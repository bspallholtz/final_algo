from os import stat
import sqlite3
from sqlite3 import OperationalError
import os.path
import datetime

db_file = 'db/new_2.db'
if not os.path.isfile(db_file):
    f = open(db_file,"w+")
    f.close()
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS algo_record (symbol TEXT PRIMARY KEY UNIQUE, state TEXT, still_buy TEXT )")
    connection.commit()
    
def get_all_open():
    """Get all the open positions in the DB"""
    symbols = get_symbols()
    open_positions = []
    for symbol in symbols:
        state = detect_symbol_state(symbol)
        if state != 'open':
            continue
        open_positions.append(symbol)
    return open_positions
    
def get_symbols():
    """Get a list of symbols from the algo_record table"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT symbol from algo_record")
    data = cursor.fetchall()
    if len(data) == 0:
        return []
    symbols = []
    for symbol in data:
        symbols.append(symbol[0])
    return symbols
    
def detect_symbol_state(symbol):
    """Detect if the symbol has an open or closed position"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT state FROM algo_record where symbol = '{}'".format(symbol)
    cursor.execute(sql)
    state = cursor.fetchall()
    if len(state) == 0:
        return 'closed'
    return state[0][0]
    
def is_symbol_still_buy(symbol):
    """Get if a symbol is or is not a buy"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT still_buy FROM algo_record where symbol = '{}'".format(symbol)
    cursor.execute(sql)
    state = cursor.fetchall()
    if len(state) == 0:
        return False
    return state[0][0]

def get_all_buys():
    """Get all buys in the DB"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT symbol FROM algo_record where still_buy == 'True'"
    cursor.execute(sql)
    symbols = cursor.fetchall()
    final = []
    for symbol in symbols:
        final.append(symbol[0])
    return final
        

def get_tp(symbol):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT finviz_tp, tipranks_tp from {} order by id limit 1".format(symbol)
    cursor.execute(sql)
    return cursor.fetchall()[0]
    
def get_latest_data(symbol):
    """Get the last buy of a symbol"""
    connection = sqlite3.connect(db_file)
    try:
        cursor = connection.execute("SELECT * FROM {} limit 1".format(symbol))
    except OperationalError:
        return None
    names = list(map(lambda x: x[0], cursor.description))
    cursor = connection.execute("SELECT * FROM {} order by id limit 1".format(symbol))
    last_trade = list(cursor.fetchall()[0])
    data = dict(zip(names,last_trade))
    return data
    
def get_buy_price(symbol):
    """Get the last buy of a symbol"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT action_price FROM {} where action = 'buy' order by id desc limit 1".format(symbol)
    cursor.execute(sql)
    last_trade = cursor.fetchall()
    return last_trade[0][0]
    
def get_buy_date(symbol):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT action_date FROM {} where action = 'buy' order by id desc limit 1".format(symbol)
    cursor.execute(sql)
    last_trade = cursor.fetchall()
    return last_trade[0][0]
    
def update_buy_status(symbol, still_buy=False):
    """Update the status of a symbol as a BUY (True) or no longer a BUY (False)"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    symbols = get_symbols()
    if symbol in symbols:
        sql = "UPDATE algo_record SET still_buy = '{still_buy}' WHERE symbol = '{symbol}'".format(symbol=symbol, still_buy=still_buy)
        cursor.execute(sql)
        return connection.commit()
    elif still_buy is True:
        sql = "INSERT into algo_record (symbol,still_buy, state) VALUES ( '{}', '{}', 'open')".format(symbol,still_buy)
        cursor.execute(sql)
        return connection.commit()
    return False
    
def create_symbol_table(symbol):
    """Create a table for a particular symbol"""
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "CREATE TABLE IF NOT EXISTS {} \
        (\
            id INTEGER PRIMARY KEY, \
            action TEXT, \
            action_date TEXT, \
            action_price INTERGER,\
            rh_buy_analysts INTERGER, \
            rh_total_analysts INTERGER, \
            rh_percent_buy INTERGER, \
            yahoo_percent_buys INTERGER,\
            yahoo_number_analysts INTERGER,\
            yahoo_number_buy_analysts INTERGER,\
            finviz_recom TEXT,\
            finviz_tp INTERGER,\
            tipranks_smart_score INTERGER,\
            cp INTERGER\
        )".format(symbol)
    cursor.execute(sql)
    connection.commit()
    return True
    
def get_date(symbol):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT action_date from {} order by id desc limit 1".format(symbol)
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        return None
    return data[0][0]

def add_data(data):
    today = str(datetime.date.today())
    for symbol in data.keys():
        state = detect_symbol_state(symbol)
        create_symbol_table(symbol)
        if state == 'open':
            last_date = get_date(symbol)
            if last_date is None:
                create_symbol_table(symbol)
                execute_trade(symbol, data[symbol])
            elif last_date == today:
                update_row(data[symbol], symbol, today)
            else:
                execute_trade(symbol, data[symbol],'hold')
        else:
            create_symbol_table(symbol)
            execute_trade(symbol, data[symbol])
    
def update_row(data,symbol,date ):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "UPDATE {} set \
            rh_buy_analysts = {},\
            rh_total_analysts = {},\
            rh_percent_buy = {},\
            yahoo_percent_buys = {},\
            yahoo_number_analysts = {},\
            yahoo_number_buy_analysts = {},\
            finviz_recom = {},\
            finviz_tp = {},\
            tipranks_smart_score = {},\
            cp = {} where action_date = '{}'"\
        .format(\
            symbol,
            data['rh_buy_analysts'],\
            data['rh_total_analysts'],\
            data['rh_percent_buy'],\
            data['yahoo_percent_buys'],\
            data['yahoo_number_analysts'],\
            data['yahoo_number_buy_analysts'],\
            data['finviz_recom'],\
            data['finviz_tp'],\
            data['tipranks_smart_score'],\
            data['cp'],\
            date\
        )
    cursor.execute(sql)
    return connection.commit()
    return True

def execute_sell(symbol,cp):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "INSERT into {} (\
        action,\
        action_date,\
        action_price\
    ) VALUES ('sell',strftime('%Y-%m-%d','now'),{})".format(symbol,cp)
    cursor.execute(sql)
    connection.commit()
    return True

def execute_trade(symbol, data, action='buy'):
    if update_buy_status(symbol, still_buy=True) is False:
        return False
    if create_symbol_table(symbol) is False:
        return False
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "INSERT into {} (\
        action,\
        action_date,\
        action_price,\
        rh_buy_analysts,\
        rh_total_analysts,\
        rh_percent_buy,\
        yahoo_percent_buys,\
        yahoo_number_analysts,\
        yahoo_number_buy_analysts,\
        finviz_recom,\
        finviz_tp,\
        tipranks_smart_score,\
        cp\
    ) VALUES (\
        '{}',\
        strftime('%Y-%m-%d','now'),\
        {},{},{},{},{},{},{},{},{},{},{})".format(\
        symbol,\
        action,\
        data['cp'],\
        data['rh_buy_analysts'],\
        data['rh_total_analysts'],\
        data['rh_percent_buy'],\
        data['yahoo_percent_buys'],\
        data['yahoo_number_analysts'],\
        data['yahoo_number_buy_analysts'],\
        data['finviz_recom'],\
        data['finviz_tp'],\
        data['tipranks_smart_score'],\
        data['cp']
    )
    cursor.execute(sql)
    connection.commit()
    return True
    
def update_price(symbol, cp):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = 'UPDATE {} set cp = {}'.format(symbol,cp)
    try:
        cursor.execute(sql)
    except OperationalError:
        return False
    connection.commit()
    return True

def find_first_trade():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    dates = []
    for symbol in get_symbols():
        sql = 'SELECT action_date from {} limit 1'.format(symbol)
        try:
            cursor.execute(sql)
        except OperationalError:
            continue
        first_trade = cursor.fetchall()
        first_trade = first_trade[0]
        dates.append(first_trade)
    dates = sorted(dates)
    return dates[0][0]
    
def get_today_buys():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    today = str(datetime.date.today())
    open_symbols = get_all_open()
    trades = []
    init_symbol = open_symbols[0]
    cursor = connection.execute("SELECT * FROM {} limit 1".format(init_symbol))
    names = list(map(lambda x: x[0], cursor.description))
    for symbol in open_symbols:
        sql = 'SELECT * from {} where action_date = \'{}\' and action = \'buy\''.format(symbol,today)
        try:
            cursor.execute(sql)
        except OperationalError:
            continue
        trade = cursor.fetchall()
        if len(trade) == 0:
            continue
        trade = list(trade[0])
        data = dict(zip(names,trade))
        data['symbol'] = symbol
        if len(trade) > 0:
            trades.append(data)
    if len(trades) == 0:
        return None                   
    return trades
    
def set_to_closed(symbol):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "UPDATE algo_record SET state = 'closed' WHERE symbol = '{}'".format(symbol)
    cursor.execute(sql)
    connection.commit()
    return True
    
def get_closed_positions():
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT symbol from algo_record where state = 'closed'"
    cursor.execute(sql)
    symbols = cursor.fetchall()
    if len(symbols) == 0:
        return []
    data = []
    for symbol in symbols:
        symbol = symbol[0]
        data.append(symbol)
    return data
    
def get_action_data(symbol,action):
    connection = sqlite3.connect(db_file)
    cursor = connection.cursor()
    sql = "SELECT * from {} where action = '{}' limit 1".format(symbol,action)
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) > 1 or len(data) == 0:
        return False
    return data[0]    



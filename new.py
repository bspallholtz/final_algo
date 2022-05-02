
import concurrent.futures
import datetime
import json
import yahoo_lib as y

today = datetime.date.today().strftime("%m_%d_%Y")


rh_symbols = open('data/rh_data_{}.json'.format(today), 'r')
data = json.loads(rh_symbols.read())

def do_yahoo(symbol):
     return y.get_yahoo_rating(symbol,min_avg=80,min_analysts=5)

def third():
    results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = [executor.submit(do_yahoo, param) for param in list(data)]
        results = [f.result() for f in future]
    return results

print(third())
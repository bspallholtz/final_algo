from audioop import ratecv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import log_lib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import concurrent.futures
import selenium.common.exceptions


log = log_lib.write_log

options = Options()
options.add_argument("--headless")
options.add_argument('--user-data-dir=C:\\Users\\brian\\AppData\\Local\\Google\\Chrome\\User Test')
options.add_argument("--profile-directory=C:\\Users\\brian\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
options.add_argument("--disable-logging")
options.add_argument('log-level=3')


def batch(symbols=list,check=False,required_rating=1):
    return_symbols = []
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    for symbol in symbols:
        log('INFO', '{} - Starting zacks.com analysis on {}'.format(symbol,symbol))
        url = 'https://www.zacks.com/stock/quote/{}?q={}'.format(symbol,symbol)
        driver.get(url)
        time.sleep(5)
        try:
            data = driver.find_element_by_class_name("rank_view")
        except selenium.common.exceptions.NoSuchElementException:
            if check is True:
                return_symbols.append({symbol: 0})
                continue
            continue
        lines = data.text.splitlines()
        lines = list(line for line in (l.strip() for l in lines) if line)
        if len(lines) == 0:
            if check is True:
                return_symbols.append({symbol: 0})
            continue
        else:
            rating = int(lines[-1])
        if rating <= required_rating:
            log('DEBUG', '{} - zacks.com accepted {} with rating of {}'.format(symbol,symbol,rating))
            return_symbols.append({symbol: rating})
        else:
            log('DEBUG', '{} - zacks.com rejected {} with rating of {}'.format(symbol,symbol,rating))
            if check is True:
                return_symbols.append({symbol: rating})
    return return_symbols 



def individual(symbol,required_rating=1):
    log('INFO', '{} - Starting zacks.com analysis on {}'.format(symbol,symbol))
    url = 'https://www.zacks.com/stock/quote/{}?q={}'.format(symbol,symbol)
    driver.get(url)
    driver.implicitly_wait(6)
    time.sleep(10)
    data = driver.find_element_by_class_name("rank_view")
    lines = data.text.splitlines()
    lines = list(line for line in (l.strip() for l in lines) if line)
    rating = int(lines[-1])
    if rating <= required_rating:
        log('DEBUG', '{} - zacks.com accepted {} with rating of {}'.format(symbol,symbol,rating))
        return { symbol : rating }
    else:
        log('DEBUG', '{} - zacks.com rejected {} with rating of {}'.format(symbol,symbol,rating))
        return {symbol : False}
    return { symbol : False}

def third(symbols=list):
    print('Evaluating {} symbols'.format(len(symbols)))
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = [executor.submit(individual, param) for param in symbols]
        results = [f.result() for f in future]
    driver.quit()
    #for entry in results:
        #print(entry)
    return results

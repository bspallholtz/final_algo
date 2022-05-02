from os import get_inheritable
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import log_lib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import rh_lib as r

#driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

log = log_lib.write_log

options = Options()
options.add_argument("--headless")
options.add_argument("user-data-dir=/Users/spallhb/Library/Application Support/Google/Chrome/")
options.add_argument("--profile-directory=/Users/spallhb/Library/Application\ Support/Google/Chrome/Default")



def get_tip_data(symbol):
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    #driver = webdriver.Chrome('chromedriver.exe', options=options)
    url = 'https://www.tipranks.com/stocks/'+symbol+'/stock-analysis/'
    driver.get(url)
    time.sleep(5)
    ids = driver.find_elements_by_xpath('//*[@id]')
    for ii in ids:
        tag_name = ii.tag_name
        if tag_name == 'div':
            bar = driver.find_element_by_tag_name(ii.tag_name)
            data = bar.text
            break
    driver.quit()
    try:
         data
    except NameError:
        return False
    return data

def analyze_tip_data(data):
    lines = data.splitlines()
    for i,line in enumerate(lines):
        if line == 'SMART SCORE':
            smart_score = int(lines[i + 1])
    try:
        smart_score
    except NameError:
        smart_score = 0
    return smart_score
    exit()
    for i,line in enumerate(lines):
        if 'SMART SCORE' in line:
            smart_score = int(lines[i + 1])
            #smart_string = lines[i + 2]
        #if 'FUNDAMENTALS' in line:
            #fund = lines[i + 1]
            #tp = lines[i + 2]
            #if tp == 'Currently Not Enough Data Available':
                #tp = 0
            #else:
                #tp = lines[i + 2].split('$')[1]
            #sediment = lines[i + 3]
    #try: 
        #smart_string
    #except NameError: 
        #smart_string = None
    try:
        smart_score
    except NameError:
        smart_score = 0
    #try:
        #fund
    #except NameError:
        #fund = 0
    return smart_score
    return smart_string, int(smart_score), fund, float(tp), sediment

def new(symbols,total_symbols,min_per=0,update=False):
    rejected = 0
    final = {}
    for symbol in symbols:
        #driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        log('DEBUG', '{} - Starting TipRanks evaluation'.format(symbol))
        url = 'https://www.tipranks.com/stocks/'+symbol+'/stock-analysis/'
        print(url)
        continue
        driver.get(url)
        time.sleep(5)
        ids = driver.find_elements_by_xpath('//*[@id]')
        for ii in ids:
            tag_name = ii.tag_name
            if tag_name == 'div':
                bar = driver.find_element_by_tag_name(ii.tag_name)
                data = bar.text
                print(data)
                break
        try:
            data
        except NameError:
            rejected += 1
            log('DEBUG', '{} - Did not find TP data, rejected {}/{} symbols'.format(symbol,rejected,total_symbols))
            continue
        #smart_string, smart_score, fund, tp, sediment = analyze_tip_data(data)
        smart_score = analyze_tip_data(data)
        driver.quit()
        #if smart_string == 'NEUTRAL' or smart_string ==  'UNDERPERFORM' or smart_string is None:
            #rejected += 1
            #log('DEBUG', '{} - TP has a smart string of {} ,rejected {}/{} symbols'.format(symbol,smart_string,rejected,total_symbols))
            #if update is False:
                #continue
        if smart_score < 8:
            rejected += 1
            log('DEBUG', '{} - TP has a smart score of {} - rejected {}/{}'.format(symbol,smart_score,rejected,total_symbols))
            if update is False:
                continue
        #cp = r.get_price(symbol)
        #tp_per = round((((tp - cp) * 100) / cp), 2)
        #if tp_per < min_per:
            #rejected += 1
            #log('INFO', '{} - TipRanks TP is ${} the cp is ${} the upside is {}% which is less than {} , rejected {}/{} symbols'.format(symbol,tp,cp,tp_per,min_per,rejected,total_symbols))
            #if update is False:
                #continue
        #log('DEBUG', '{} - The symbol {} has the sediment {}'.format(symbol, symbol, sediment))
        #log('DEBUG', '{} - The symbol {} has the fundementals {}'.format(symbol,symbol, fund))
        #log('DEBUG', '{} - The symbol {} has the smart score of {}'.format(symbol,symbol, smart_score))
        #log('DEBUG', '{} - The symbol {} has {}'.format(symbol,symbol, smart_string))
        #log('DEBUG', '{} - Has a TipRank TP of ${} a CP of ${} for an upside of {}%'.format(symbol,tp,cp,tp_per))
        final[symbol] = {}
        #final[symbol]['tipranks_tp'] = tp
        #final[symbol]['tipranks_tp_percent'] = tp_per
        #final[symbol]['tipranks_smart_string'] = smart_string
        final[symbol]['tipranks_smart_score'] = smart_score
        #final[symbol]['tipranks_fundementals'] = fund
        #final[symbol]['tipranks_sediment'] = sediment
    return final

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import log_lib
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

log = log_lib.write_log

options = Options()
options.add_argument("--headless")
options.add_argument("user-data-dir=/Users/spallhb/Library/Application Support/Google/Chrome/")
options.add_argument("--profile-directory=/Users/spallhb/Library/Application\ Support/Google/Chrome/Default")

def analyze_tip_data(data):
    lines = data.splitlines()
    for i,line in enumerate(lines):
        if line == 'Smart Score':
            try:
                smart_score = int(lines[i + 1])
            except ValueError:
                print(smart_score)
                smart_score = 0
    try:
        smart_score
    except NameError:
        smart_score = 0
    return smart_score

def new(symbols,total_symbols,min_per=0,update=False):
    rejected = 0
    final = {}
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    for symbol in symbols:
        log('DEBUG', '{} - Starting TipRanks evaluation'.format(symbol))
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
        try:
            data
        except NameError:
            rejected += 1
            log('DEBUG', '{} - Did not find TP data, rejected {}/{} symbols'.format(symbol,rejected,total_symbols))
            continue
        smart_score = analyze_tip_data(data)
        if smart_score != 10:
            rejected += 1
            log('DEBUG', '{} - TP has a smart score of {} - rejected {}/{}'.format(symbol,smart_score,rejected,total_symbols))
            if update is False:
                continue
        final[symbol] = {}
        final[symbol]['tipranks_smart_score'] = smart_score    
    driver.quit()
    return final
        

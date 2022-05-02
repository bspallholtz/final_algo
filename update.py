import database_lib as d
import rh_lib as r
import yahoo_lib as y
for symbol in d.get_all_open():
    cp = r.get_price(symbol)
    d.update_price(symbol,cp)

for symbol in d.get_all_open():
    print('Working on {}'.format(symbol))
    if d.is_symbol_still_buy(symbol) == 'False':
        print('{} is no longer marked as a BUY'.format(symbol))
        buy_price = d.get_buy_price(symbol)
        cp = r.get_price(symbol)
        profit = round(( cp - buy_price),2)
        percent_profit = round((((cp - buy_price) / buy_price) * 100),2)
        print('{} currently has a return of {}%'.format(symbol,percent_profit))
        if percent_profit < -20:
            print('{} return is down 30% or more, selling')
            cp = r.get_price(symbol)
            d.execute_sell(symbol,cp)
            d.set_to_closed(symbol)
        if percent_profit > 100:
            print('{} return is up 100% or more, selling')
            cp = r.get_price(symbol)
            d.execute_sell(symbol,cp)
            d.set_to_closed(symbol)
        buy_data = d.get_action_data(symbol,'buy')
        if buy_data is False:
            print(symbol)
            print('{} failed to get buy data investigate why'.format(symbol))
            exit()
        buy_date = buy_data[2]
        buy_price = buy_data[3]
        high = y.get_high(buy_date,symbol)
        if high is False:
            print('{} failed to get the high price since buying this simple investigate'.format(symbol))
            exit()
        stop_loss = round((high * .7),2)
        cp = r.get_price(symbol)
        print('{} - CP: {}, buy price {}, buy date {}, high since buy {} , slp {}'.format(symbol,cp, buy_price, buy_date, high, stop_loss))
        if cp < stop_loss:
            print('{} cp of {} is lower than the SLP of {}'.format(symbol,cp,stop_loss))
            d.execute_sell(symbol,cp)
            d.set_to_closed(symbol)
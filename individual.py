import rh_lib as r
import log_lib as l
import finviz as f
import yahoo_lib as y

class Individual():
    """Check any individual stock against the algorithm"""
    def main(self, symbol):
        RobinHood().login()
        """Check any individual stock"""
        state, rh_buy_analysts, rh_total_analysts = RobinHood().get_rh_rating(symbol)
        if state is False:
            return None
        state, yahoo_total_analysts, yahoo_star  = Yahoo().get_yahoo_rating(symbol)
        if state is False:
            return None
        rh_percent_buy = round((rh_buy_analysts / rh_total_analysts) * 100,2)
        rh_percent_star = l().get_rh_percent_star(symbol, rh_percent_buy)
        rh_buy_star = l().get_rh_buy_star(symbol, rh_buy_analysts)
        recom, tp = FinViz().individual(symbol)
        try:
            tp = float(tp)
        except TypeError:
            return None
        try:
            recom = float(recom)
        except TypeError:
            return None 
        if recom <= 1.7:
            recom = 'strongbuy'
        elif recom <= 2.5:
            recom = 'betterbuy'
        an_recom_star = l().get_recom_star(recom)
        sh_price = RobinHood().get_price(symbol)
        tp_per = round(abs(((tp - sh_price) / sh_price) * 100),2) 
        tp_star = l().get_tp_star(tp_per)
        market_cap = RobinHood().get_cap(symbol)
        price_star = l().get_price_star(sh_price)
        cap_star = l().get_cap_star(market_cap)
        display_market_cap = "{:,}".format(market_cap)
        star = round(rh_percent_star  + rh_buy_star + tp_star + an_recom_star + price_star + cap_star + yahoo_star,2)
        message = '''


'''
        message = message + 'The symbol {symbol} has a market cap ${cap}, which is worth {star_cap} star(s) in the algorithm.'.format(symbol=symbol, cap=display_market_cap, star_cap=cap_star) + '\n\n'
        message = message + 'The symbol {} has {} analysts on RH with a \'BUY\' rating , which is worth {} star(s) in the algorithm.'.format(symbol, rh_buy_analysts, rh_buy_star) + '\n\n'
        message = message + 'The symbol has a share price of {share_price}, which is worth {star_price} star(s) in the algorithm'.format(share_price=sh_price, star_price=price_star) + '\n\n'
        message = message + 'The symbol has an Analysts recommendation from FinViz of {recom},  which is worth {recom_star} star(s) in the algorithm'.format(recom=recom,recom_star=an_recom_star) + '\n\n'
        message = message + 'The symbol has a Target Price of {tp}, versus it\'s current price of {share_price}, which represents a {tp_per} percent change up from today, which is worth {tp_star} stars in the algorithm'.format(tp=tp,share_price=sh_price,tp_per=tp_per,tp_star=tp_star) + '\n\n'            
        message = message + 'The symbol has {rh_percent_buy} percent of analysts on RobinHood rate the symbol a \'Buy\' which is worth {rh_percent_star} star(s) in the algorithm'.format(rh_buy_analysts=rh_buy_analysts, rh_total_analysts=rh_total_analysts, rh_percent_buy=rh_percent_buy, rh_percent_star=rh_percent_star) + '\n\n'
        message = message + 'The symbol has {yahoo_buy_analysts} analyst firms cover it from Yahoo, the Yahoo star rating ( based on the ratings from Yahoo ) is {yahoo_star_rating}, which is treated equally in the algorithm'.format(yahoo_buy_analysts=yahoo_total_analysts, yahoo_star_rating=yahoo_star) + '\n\n'
        message = message + 'Finally the symbol overall has a {total} star(s) in the algorithm'.format(total=star) + '\n\n'
        if star < 4:
            message = message + 'With a star rating of {star} the symbol would not be a buy'.format(star=star) + '\n\n'
        elif tp_per < 30:
            message = message + 'Because the Target price is less than 30% above the current price ,{tp_per}, this is an AUTOMATIC exclusion from a BUY status'.format(tp_per=tp_per)
        else:
            message = message + 'With a star rating of {star} the symbol would BE a buy and should in ALL BUY\'s page'.format(star=star) + '\n\n'
        return message
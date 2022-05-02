import smtplib
from email.message import EmailMessage
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import lib
import database_lib as d
import rh_lib as r
import yahoo_lib as y

msg = EmailMessage()
rh_username, rh_password,gmail_username, gmail_password, rh_mfa = lib.get_creds()

def send_message(to,message):
    msg['Subject'] = 'Here is my newsletter'
    msg['From'] = 'brian.stock.algo@gmail.com'
    msg['To'] = to
    msg.set_content(message,subtype='html')
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(gmail_username, gmail_password)
        smtp.send_message(msg)
    return True

first_date = d.find_first_trade()
voo_date = round(y.get_voo_price(first_date),2)
voo_current = r.get_price('VOO')
voo_profit = y.get_voo_profit(first_date)
total_open_positions = d.get_all_open()
total_costs = 0
total_current_value = 0
for symbol in total_open_positions:
    total_costs += d.get_buy_price(symbol)
    total_current_value += r.get_price(symbol)

closed_positons = d.get_closed_positions()
total_closed_positions = len(closed_positons)
for symbol in closed_positons:
    buy_data = d.get_action_data(symbol,'buy')
    buy_date = buy_data[2]
    buy_price = round(buy_data[3],2)
    sell_data = d.get_action_data(symbol,'sell')
    sell_date = sell_data[2]
    sell_price = round(sell_data[3],2)
    total_costs += buy_price
    total_current_value += sell_price
total_positions = len(total_open_positions) + len(closed_positons)
total_profit = round(total_current_value - total_costs,2)
total_percent = round((((total_current_value - total_costs) / total_costs) * 100),2)
alpha = round((((total_percent - voo_profit)/voo_profit) * 100),2)
total_costs = round(total_costs,2)
total_current_value = round(total_current_value,2)
current_buys = d.get_all_buys()
latest_symbol = d.get_all_buys()
if len(latest_symbol) == 0:
    latest_symbol = 'None'
else:
    latest_symbol = latest_symbol[0][-1].lower()
html = """
{table}
<p>Regards,</p>
<p>Brian</p>
</body></html>
"""
headers = ['Symbol','Buy Date','Buy Price','Current Price','Current Profit','Target Price','Upside']
data = []
for symbol in current_buys:
    foo = []
    buy_data = d.get_action_data(symbol,'buy')
    buy_date = buy_data[2]
    buy_price = round(buy_data[3],2)
    finviz_tp = buy_data[11]
    tipranks_tp = buy_data[12]
    cp = round(r.get_price(symbol),2)
    avg_tp = round(((finviz_tp + tipranks_tp) / 2),2)
    profit = round((cp - buy_price),2)
    upside = str(round((((avg_tp - cp) / cp) * 100),2)) + '%'
    foo.append(symbol)
    foo.append(buy_date)
    foo.append('$' + str(buy_price))
    foo.append('$' + str(cp))
    foo.append('$' + str(profit))
    foo.append('$' + str(avg_tp))
    foo.append(upside)
    data.append(foo)
html = html.format(table=tabulate(data, headers=headers, tablefmt="html"))

message = '''
<!DOCTYPE html>
<style>
    table {
        /* cellspacing */
        border-spacing: 0;
        border: 1px solid black;
    }
    th {
        border-spacing: 0;
        border-spacing: 0;
        border: 1px solid black;
        padding: 6px;
        /* This covers the th elements */
    }
    tr {
        border-spacing: 0;
        border: 1px solid black;
        padding: 6px;
        /* This covers the tr elements */
    }
    th, td {
        /* cellpadding */
        padding: 6px;
        border-spacing: 0;
        border: 1px solid black;
    
    }
</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script>
    function filterText()
        {
            var val = $('#filterText').val();
            if(val === "")
               return;
            if(val === "all")
              clearFilter();
            else
    
            $('.still_buy').each(function() {
              $(this).parent().toggle($(this).text()=== val);
            });
    
        }
       function clearFilter()
        {
            $('.filterText').val('');
            $('.row').show();
        }
</script>
<script>
    function filterTextTerm()
        {
            var val = $('#filterTextTerm').val();
            if(val === "")
               return;
            if(val === "all")
              clearFilterTerm();
            else
    
            $('.term').each(function() {
              $(this).parent().toggle($(this).text()=== val);
            });
    
        }
       function clearFilterTerm()
        {
            $('.filterTextTerm').val('');
            $('.row').show();
        }
</script>
    
<script src="https://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>'''

message = message + '''
<html>
    <body>
        This is an email report on my Stock Algorithm based on Analysts sediment data<br>
        This is for informational purposes only and all information below should be ignored<br>

<br>Glossary of terms:

<br>&emsp;CP = The current price of the stock or symbol
<br>&emsp;TP = The target price of the stock
<br>&emsp;RoR = Rate of Return or percentage of return of a symbol over a period of time
<br>&emsp;VOO = The Vanguard S&P 500 index fund symbol or "the market" used as a benchmark for the algorithm

<br><br>Performance of the Algorithm:
    <br>&emsp;This algorithm started trading on {first_date}
    <br>&emsp;VOO was trading for ${voo_date} on that date. Today it is trading for ${voo_current} for a RoR of {voo_profit}%
    <br>&emsp;Since {first_date} the algorithm has opened {total_positions} positions it has closed {total_closed_positions} positions leaving {total_open_positions} open
    <br>&emsp;Those combined open and closed positions cost = ${total_cost}. Those positions are worth ${total_current_value} today for a profit of ${total_profit} or {total_percent}% RoR
    <p style="font-weight: bold;">&emsp;The algorithm is generating a {alpha}%  Alpha or returns better than VOO over the same time period</p>
    <p style="font-weight: bold;">&emsp;If the above Alpah is NEGATIVE, don't buy any of these symbols because this "strategy" is generating worse returns with higher risk</p>


<br><br>Methodology:
    <br>&emsp;For a symbol to marked a BUY by the algorithm it must have ALL of the following be TRUE:
    <br>&emsp;- Data from all four sources
    <br>&emsp;- Minimum of five analysts covering the symbol
    <br>&emsp;- Minimum of 80% of the analysts marking the symbol as a BUY
    <br>&emsp;- Minimum of 30% TP above CP
    
<br><br>Examples of Data sources or filters for an example symbol {latest_symbol} 
    <br>&emsp;- Finviz - https://finviz.com/quote.ashx?t={latest_symbol} Search the page for "Recom"; itmust lower than 2 ( 1 = Strongest Buy, 5 = Strongest Sell); Search page for "Target Price" must be 30% higher than CP
    <br>&emsp;- RobinHood - https://robinhood.com/stocks/{latest_symbol} Search the page for "Analyst ratings"
    <br>&emsp;- Yahoo finance - https://finance.yahoo.com/quote/{latest_symbol}/analysis?p={latest_symbol} Look for 'No. of Analysis', 'Recommendation Trend', 'Recommendation Rating' and 'Analysts Price Targets'
    <br>&emsp;- TipRanks - https://www.tipranks.com/stocks/{latest_symbol}/stock-analysis should be self evident 
    <br>&emsp;- There are roughly 6K symbols publicly traded companies in the US, Finviz filters it down to ~750 symbols, RobinHood down to ~175, Yahoo ~45 , TipRanks ~5 
<br>

<br>The algorithm will hold Symbols marked as BUYs indefinitely, 
    <br>&emsp;But will sell a symbol that is NO longer marked as a BUY if ANY of the below conditions are TRUE:
    <br>&emsp;- The symbol is DOWN 30% or more since the algorithm opened a position
    <br>&emsp;- The symbol is UP 100% or more since the algorithm opened a position
    <br>&emsp;- The symbol hits a 30% trailing stop loss from the highest CP since the algorithm has opened the position

<br>
<br>And now the symbols currently marked as BUYs per the above methodology in order from oldest to newest
<br>
{html}

'''.format(\
    first_date=first_date,\
    voo_date=voo_date,\
    voo_current=voo_current,\
    voo_profit=voo_profit,\
    total_closed_positions=len(closed_positons),\
    total_open_positions=len(total_open_positions),\
    total_positions=total_positions,\
    total_cost=total_costs,\
    total_current_value=total_current_value,\
    total_profit=total_profit,\
    total_percent=total_percent,\
    alpha=alpha,\
    latest_symbol=latest_symbol,\
    html=html
)

send_message('brian.spallholtz@gmail.com',message)
#send_message('hfspro@yahoo.com',message)
#send_message('jss9631@gmail.com',message)
#send_message('mdellinger@gmail.com',message)
#send_message('jake.2001.oneill@gmail.com',message)
#send_message('robert.hempson@gmail.com',message)
#send_message('tein@thedigitalrealtors.com', message)
#send_message('rouleau09@gmail.com',message)
exit()

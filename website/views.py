"""Return the pathname of the KOS root directory."""

from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from . import db
import lib as l

db_file = 'db/new_2.db'

views = Blueprint('views', __name__)
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user, data=l.calculate_profit())

@views.route('/glossary', methods=['GET'])
@login_required
def glossary():
    return render_template("glossary.html", user=current_user)

@views.route('/methodology', methods=['GET'])
@login_required
def methodology():
    return render_template("methodology.html", user=current_user)

@views.route('/test', methods=['GET'])
@login_required
def test():
    return render_template("test.html", user=current_user)

@views.route('/today', methods=['GET'])
@login_required
def today():
    data = l.calculate_profit()
    data['rows'] = l.todays_buys()
    if data['rows'] is None:
        return render_template("today_none.html", user=current_user, data=data)
    return render_template("today_none.html", user=current_user, data=data)

@views.route('/closed', methods=['GET'])
@login_required
def closed():
    data = l.calculate_profit()
    closed = l.get_closed_profit()
    del closed['total_buy']
    del closed['total_sell']
    data['rows'] = closed
    return render_template('closed_profit.html', user=current_user,data=data)
    

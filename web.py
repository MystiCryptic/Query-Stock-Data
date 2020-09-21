from flask import Flask, request, render_template
import yfinance as yf
import time
import pandas as pd
from matplotlib.pylab import plt
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('search.html')


@app.route('/', methods=['POST'])
def send_stockdata():
    stock_code = request.form['text']

    stock_info = get_stock_data(stock_code)
    if stock_info.empty:
        return render_template('searchagain.html')
    else:
        df = data_cleaning(stock_info)
        filename = create_figure(df)
        msg = create_html(df, filename,stock_code)
    return msg


def get_stock_data(stock_code):
    stock = yf.Ticker(stock_code)
    df = stock.history()
    return df

def data_cleaning(df):
    df.reset_index(inplace=True)
    df = df.sort_values(by='Date').iloc[-10:]
    df['Date'] = df['Date'].dt.strftime("%m-%d")

    return df

def create_figure(df):
    df = df.set_index('Date').loc[:,'Close']
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(9, 6))
    df.plot(kind="line", linewidth=2, marker="o", ax=ax)
    ax.set_ylabel("Price")
    epoch = int(time.time())
    plt.savefig(os.getcwd()+f'\\static\\figure{epoch}.png', bbox_inches="tight")
    filename = f'figure{epoch}.png'

    return filename


def create_html(df, filename,stock_code):
    header = '''
    <html>
    <head>
    <style>
        table {
            width: 1000px;
            font-family: Helvetica, Arial, sans-serif;
            font-size: 12px;
            border-collapse: collapse;
            border-spacing: 0;
            color: #212529;
            width: auto;
        }
        td, th {border: 1px solid #CCC; height: 28px;}
        th{
            background: #F3F3F3;
            font-weight: bold;
            font-size: 11px;
            width: 85px;
        }
        tr{
            font-size: 1rem;
            font-weight: 400;
            line-height: 1.5;

            }
        td{
            text-align: center;
        }
        </style>
    </head>
    '''
    
    footer = '''
    <footer>
    <br>
    <br>
    <p><font size = "6">Last 10 days price chart</font></p>
    <img src="/static/{filename}">
    </footer>
    </body>
    </html>
    '''.format(filename=filename)
    
    msgtxt = header
    msgtxt += f'<center><font size = "6">Stock performance: {stock_code.upper()}</font><br><br>'
    msgtxt += df.style.hide_index().render()
    msgtxt += footer

    return msgtxt

app.run()
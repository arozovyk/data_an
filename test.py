import pandas as pd
import yfinance as yf
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Select, DateRangeSlider
from bokeh.layouts import column, row
from bokeh.io import curdoc

def get_crypto_data(ticker, start_date, end_date):
    crypto_data = yf.download(ticker, start=start_date, end=end_date)
    return crypto_data

def update(attr, old, new):
    ticker = crypto_select.value
    start_date = date_range_slider.value_as_date[0]
    end_date = date_range_slider.value_as_date[1]
    crypto_data = get_crypto_data(ticker, start_date, end_date)
    source.data = ColumnDataSource.from_df(crypto_data)

popular_cryptos = [
    'BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'XRP-USD',
    'SOL1-USD', 'DOGE-USD', 'DOT1-USD', 'AVAX-USD', 'LUNA1-USD'
]

crypto_select = Select(value='BTC-USD', title='Select Crypto:', options=popular_cryptos)
crypto_select.on_change('value', update)

date_range_slider = DateRangeSlider(title='Date Range:', value=('2020-01-01', '2021-09-01'),
                                    start='2015-01-01', end='2021-09-01')
date_range_slider.on_change('value', update)

initial_data = get_crypto_data('BTC-USD', '2020-01-01', '2021-09-01')
source = ColumnDataSource(initial_data)

p = figure(x_axis_type='datetime', width=800, height=400, title='Historical Crypto Prices', tools='pan,wheel_zoom,box_zoom,reset,save')
p.line(x='Date', y='Close', source=source, color='blue', legend_label='Close Price')
p.yaxis.axis_label = 'Price'

hover = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Close', '@Close{0.2f}')],
                  formatters={'@Date': 'datetime'})
p.add_tools(hover)

layout = column(row(crypto_select, date_range_slider), p)
curdoc().add_root(layout)
curdoc().title = 'Bokeh Crypto Dashboard'

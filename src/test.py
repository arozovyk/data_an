import pandas as pd
import yfinance as yf
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, TextInput, DateRangeSlider
from bokeh.layouts import column, row
from bokeh.io import curdoc


def get_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


def update(attr, old, new):
    ticker = stock_ticker.value
    start_date = date_range_slider.value_as_date[0]
    end_date = date_range_slider.value_as_date[1]
    stock_data = get_stock_data(ticker, start_date, end_date)
    source.data = ColumnDataSource.from_df(stock_data)


stock_ticker = TextInput(value='AAPL', title='Stock Ticker:')
stock_ticker.on_change('value', update)

date_range_slider = DateRangeSlider(title='Date Range:', value=('2020-01-01', '2021-09-01'),
                                    start='1962-01-02', end='2021-09-01')
date_range_slider.on_change('value', update)

initial_data = get_stock_data('AAPL', '2020-01-01', '2021-09-01')
source = ColumnDataSource(initial_data)

p = figure(x_axis_type='datetime', width=800, height=400,
           title='Historical Stock Prices', tools='pan,wheel_zoom,box_zoom,reset,save')

p.line(x='Date', y='Close', source=source,
       color='blue', legend_label='Close Price')
p.yaxis.axis_label = 'Price'

hover = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Close', '@Close{0.2f}')],
                  formatters={'@Date': 'datetime'})
p.add_tools(hover)

layout = column(row(stock_ticker, date_range_slider), p)
curdoc().add_root(layout)
curdoc().title = 'Bokeh Stock Dashboard'

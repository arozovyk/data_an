import pandas as pd
import datetime
import yfinance as yf
from ta.momentum import RSIIndicator
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Select, DateRangeSlider
from bokeh.layouts import layout, row, column
from bokeh.io import curdoc
from statsmodels.tsa.arima.model import ARIMA


def get_crypto_data(ticker, start_date, end_date):
    crypto_data = yf.download(ticker, start=start_date, end=end_date)
    return crypto_data


def fit_arima(data):
    model = ARIMA(data, order=(5, 1, 0))
    model_fit = model.fit()
    forecast_length = 30
    return model_fit.forecast(steps=forecast_length)


def calculate_rsi(data):
    rsi_indicator = RSIIndicator(data['Close'])
    rsi_values = rsi_indicator.rsi()
    return rsi_values


def update_data(attr, old, new):
    ticker = crypto_select.value
    start_date = date_range_slider.value_as_date[0]
    end_date = date_range_slider.value_as_date[1]
    crypto_data = get_crypto_data(ticker, start_date, end_date)
    update_data_sources(crypto_data)


def update_data_sources(crypto_data):
    source.data = ColumnDataSource.from_df(crypto_data)

    arima_forecast = fit_arima(crypto_data['Close'])
    rsi_values = calculate_rsi(crypto_data)

    total_volume = crypto_data['Volume']
    volume_dates = crypto_data.index

    last_date = crypto_data.index[-1]
    future_dates = pd.date_range(
        last_date + datetime.timedelta(days=1), periods=30, closed='right')

    arima_source.data = {'Date': future_dates, 'Forecast': arima_forecast}
    volume_source.data = {'Date': volume_dates, 'Volume': total_volume}
    rsi_source.data = {'Date': volume_dates, 'RSI': rsi_values}

    p_arima.x_range.start = p.x_range.end
    p_arima.x_range.end = (
        datetime.datetime.fromtimestamp(
            p.x_range.end / 1000) + datetime.timedelta(days=30)).timestamp() * 1000


popular_cryptos = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'XRP-USD',
                   'SOL1-USD', 'DOGE-USD', 'DOT1-USD', 'AVAX-USD', 'LUNA1-USD']

crypto_select = Select(
    value='BTC-USD', title='Select Crypto:', options=popular_cryptos)
crypto_select.on_change('value', update_data)

date_range_slider = DateRangeSlider(title='Date Range:', value=('2020-01-01', '2023-05-07'),
                                    start='2015-01-01', end='2023-05-07')
date_range_slider.on_change('value', update_data)

initial_data = get_crypto_data('BTC-USD', '2022-01-01', '2023-05-07')
source = ColumnDataSource(initial_data)

arima_forecast = fit_arima(initial_data['Close'])
last_date = initial_data.index[-1]
future_dates = pd.date_range(
    last_date + datetime.timedelta(days=1), periods=30, closed='right')
arima_source = ColumnDataSource(
    data={'Date': future_dates, 'Forecast': arima_forecast})

total_volume = initial_data['Volume']
volume_dates = initial_data.index
volume_source = ColumnDataSource(
    data={'Date': volume_dates, 'Volume': total_volume})

rsi_values = calculate_rsi(initial_data)
rsi_source = ColumnDataSource(data={'Date': volume_dates, 'RSI': rsi_values})

p = figure(x_axis_type='datetime', width=900, height=400,
           title='Historical Crypto Prices', tools='pan,wheel_zoom,box_zoom,reset,save')
p.line(x='Date', y='Close', source=source,
       color='blue', legend_label='Close Price')
p.yaxis.axis_label = 'Price'

initial_start_date = initial_data.index.min()
p.x_range.start = initial_start_date.timestamp() * 1000

hover = HoverTool(tooltips=[
                  ('Date', '@Date{%F}'), ('Close', '@Close{0.2f}')], formatters={'@Date': 'datetime'})
p.add_tools(hover)
p_volume = figure(x_axis_type='datetime', width=900, height=200,
                  title='Total Traded Volume', tools='pan,wheel_zoom,box_zoom,reset,save')
p_volume.vbar(x='Date', top='Volume', source=volume_source,
              width=pd.Timedelta(days=1), color='purple')
p_volume.yaxis.axis_label = 'Volume'

hover_volume = HoverTool(tooltips=[(
    'Date', '@Date{%F}'), ('Volume', '@Volume{0.00a}')], formatters={'@Date': 'datetime'})
p_volume.add_tools(hover_volume)
p_arima = figure(x_axis_type='datetime', width=900, height=200,
                 title='ARIMA Forecast', tools='pan,wheel_zoom,box_zoom,reset,save')
p_arima.line(x='Date', y='Forecast', source=arima_source,
             color='red', legend_label='ARIMA Forecast')
p_arima.yaxis.axis_label = 'Price'

hover_arima = HoverTool(tooltips=[(
    'Date', '@Date{%F}'), ('Forecast', '@Forecast{0.2f}')], formatters={'@Date': 'datetime'})
p_arima.add_tools(hover_arima)
p_rsi = figure(x_axis_type='datetime', width=900, height=200,
               title='Relative Strength Index (RSI)', tools='pan,wheel_zoom,box_zoom,reset,save')
p_rsi.line(x='Date', y='RSI', source=rsi_source,
           color='green', legend_label='RSI')
p_rsi.yaxis.axis_label = 'RSI'
p_rsi.y_range.start = 0
p_rsi.y_range.end = 100
hover_rsi = HoverTool(tooltips=[(
    'Date', '@Date{%F}'), ('RSI', '@RSI{0.00}')], formatters={'@Date': 'datetime'})
p_rsi.add_tools(hover_rsi)

layout = row(
    column(crypto_select, date_range_slider, p, p_volume), column(p_arima, p_rsi))

curdoc().add_root(layout)
curdoc().title = 'Bokeh Crypto Dashboard with ARIMA and RSI'

import pandas as pd
import datetime
import yfinance as yf
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Select, DateRangeSlider
from bokeh.layouts import layout, row, column
from bokeh.io import curdoc
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model


def get_crypto_data(ticker, start_date, end_date):
    crypto_data = yf.download(ticker, start=start_date, end=end_date)
    return crypto_data


def fit_arima(data):
    model = ARIMA(data, order=(5, 1, 0))
    model_fit = model.fit()
    forecast_length = 30
    return model_fit.forecast(steps=forecast_length)


def fit_garch(data):
    model = arch_model(data, vol='Garch', p=1, q=1,
                       mean='Constant', dist='Normal')
    model_fit = model.fit(disp='off')
    forecast_length = 30
    return model_fit.forecast(start=0, horizon=forecast_length).variance.iloc[-1]


def update(attr, old, new):
    ticker = crypto_select.value
    start_date = date_range_slider.value_as_date[0]
    end_date = date_range_slider.value_as_date[1]
    crypto_data = get_crypto_data(ticker, start_date, end_date)
    source.data = ColumnDataSource.from_df(crypto_data)
    
    arima_forecast = fit_arima(crypto_data['Close'])
    garch_volatility = fit_garch(crypto_data['Close'])
    
    last_date = crypto_data.index[-1]
    future_dates = pd.date_range(last_date + datetime.timedelta(days=1), periods=30, closed='right')
    
    arima_source.data = {'Date': future_dates, 'Forecast': arima_forecast}
    garch_source.data = {'Date': future_dates, 'Volatility': garch_volatility}

    p_arima.x_range.start = p.x_range.start
    p_arima.x_range.end = (datetime.datetime.fromtimestamp(p.x_range.start / 1000).replace(day=1) + datetime.timedelta(days=31)).timestamp() * 1000
    p_garch.x_range.start = p.x_range.start
    p_garch.x_range.end = (datetime.datetime.fromtimestamp(p.x_range.start / 1000).replace(day=1) + datetime.timedelta(days=31)).timestamp() * 1000




popular_cryptos = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'XRP-USD',
                   'SOL1-USD', 'DOGE-USD', 'DOT1-USD', 'AVAX-USD', 'LUNA1-USD']

crypto_select = Select(
    value='BTC-USD', title='Select Crypto:', options=popular_cryptos)
crypto_select.on_change('value', update)

date_range_slider = DateRangeSlider(title='Date Range:', value=('2020-01-01', '2023-05-07'),
                                    start='2015-01-01', end='2023-05-07')
date_range_slider.on_change('value', update)

initial_data = get_crypto_data('BTC-USD', '2022-01-01', '2023-05-07')
source = ColumnDataSource(initial_data)

arima_source = ColumnDataSource(data={'Date': [], 'Forecast': []})
garch_source = ColumnDataSource(data={'Date': [], 'Volatility': []})

p = figure(x_axis_type='datetime', width=800, height=400,
           title='Historical Crypto Prices', tools='pan,wheel_zoom,box_zoom,reset,save')
p.line(x='Date', y='Close', source=source,
       color='blue', legend_label='Close Price')
p.yaxis.axis_label = 'Price'

initial_start_date = initial_data.index.min()
p.x_range.start = initial_start_date.timestamp() * 1000


hover = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Close', '@Close{0.2f}')],
                  formatters={'@Date': 'datetime'})
p.add_tools(hover)

# ARIMA plot
p_arima = figure(x_axis_type='datetime', width=800, height=400, title='ARIMA Forecast',
                 tools='pan,wheel_zoom,box_zoom,reset,save')
p_arima.line(x='Date', y='Forecast', source=arima_source,
             color='red', legend_label='ARIMA Forecast')
p_arima.yaxis.axis_label = 'Price'

hover_arima = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Forecast', '@Forecast{0.2f}')],
                        formatters={'@Date': 'datetime'})
p_arima.add_tools(hover_arima)
 

# GARCH plot
p_garch = figure(x_axis_type='datetime', width=800, height=400, title='GARCH Volatility',
                 tools='pan,wheel_zoom,box_zoom,reset,save')
p_garch.line(x='Date', y='Volatility', source=garch_source,
             color='green', legend_label='GARCH Volatility')
p_garch.yaxis.axis_label = 'Volatility'

hover_garch = HoverTool(tooltips=[('Date', '@Date{%F}'), ('Volatility', '@Volatility{0.2f}')],
                        formatters={'@Date': 'datetime'})
p_garch.add_tools(hover_garch)
p_garch.x_range.start = p.x_range.start
p_arima.x_range.end = (datetime.datetime.fromtimestamp(p.x_range.start / 1000).replace(day=1) + datetime.timedelta(days=31)).timestamp() * 1000

layout = row(column(crypto_select, date_range_slider),
             column(p, p_arima, p_garch))

curdoc().add_root(layout)
curdoc().title = 'Bokeh Crypto Dashboard with ARIMA and GARCH'

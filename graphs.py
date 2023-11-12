import yfinance as yf
import plotly.graph_objects as go
import plotly
import json
import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

from keras.models import Sequential
from keras.layers import LSTM, Dense

def show_graph(option): # function to draw graph of historical stock prices with given stock and time period
    ticker = yf.Ticker(option)
    historical = ticker.history(period='max', interval='1mo', rounding=True) # all-time stock prices
    week = ticker.history(period='5d', interval='1h', rounding=True)
    print(week)

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=historical.index,
                                 open=historical['Open'],
                                 high=historical['High'],
                                 low=historical['Low'],
                                 close=historical['Close'],
                                 name='market data'))
    fig.update_layout(title=option + " share price", yaxis_title='Stock Price') # title and axis label
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([ # buttons to adjust time interval
                  dict(count=6, label='6mo', step="month", stepmode="backward"),
                  dict(count=1, label='1y', step="year", stepmode="backward"),
                  dict(count=2, label='2y', step="year", stepmode="backward"),
                  dict(count=5, label='5y', step="year", stepmode="backward"),
                  dict(step="all")
            ])
        )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON

def heatmap(option): ## UNFINISHED
    ticker = yf.Ticker(option)
    historical = ticker.history(period='max', interval='1mo', rounding=True) # all-time stock prices

    fig = plotly.subplots.make_subplots(rows=3, cols=1)
    fig.add_trace(go.Candlestick(x=historical.index,
                                 open=historical['Open'],
                                 high=historical['High'],
                                 low=historical['Low'],
                                 close=historical['Close'],
                                 name='market data'),
                row=1, col=1)
    fig.add_trace(go.Scatter(x=historical.index))

def forecast_lstm(option, period):
    time_step_dict = {"1y": [60, 30], "1m": [15, 5], "5d": [5, 1]} # decides timesteps used
    ticker = yf.Ticker(option)
    historical = ticker.history(period=period, rounding=True)
    df = historical
    historical.fillna(historical.mean())
    historical = np.array(historical['Close'])

    sc = MinMaxScaler(feature_range=(0, 1))
    scaled_stocks = sc.fit_transform(historical.reshape(-1, 1))

    lookback_time_steps, forecast_time_steps = time_step_dict.get(period)[0], time_step_dict.get(period)[1]
    X_train = []
    y_train = []

    for i in range(lookback_time_steps, len(historical) - forecast_time_steps + 1):
        X_train.append(scaled_stocks[i-lookback_time_steps:i])
        y_train.append(scaled_stocks[i:i+forecast_time_steps])

    X_train, y_train = np.array(X_train), np.array(y_train)

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback_time_steps, 1)))
    model.add(LSTM(units=50))
    model.add(Dense(units=forecast_time_steps))
    model.summary()

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, batch_size=1, epochs=3)

    # generate forecasts
    X_forecast = scaled_stocks[- lookback_time_steps:] # create testing dataset
    X_forecast = X_forecast.reshape(1, lookback_time_steps, 1) # reshape testing dataset

    y_forecast = model.predict(X_forecast).reshape(-1, 1) # predicts label of testing dataset and reshapes array
    y_forecast = sc.inverse_transform(y_forecast) # scales data to original transformations

    # dataframe
    past = df[['Close']].reset_index()
    past.rename(columns={'index': 'Date', 'Close': 'Historical'}, inplace=True)
    past['Date'] = pd.to_datetime(past['Date'])
    past['Forecast'] = np.nan
    past['Forecast'].iloc[-1] = past['Historical'].iloc[-1]

    future = pd.DataFrame(columns=['Date', 'Historical', 'Forecast'])
    future['Date'] = pd.date_range(start=past['Date'].iloc[-1] + pd.Timedelta(days=1), periods=forecast_time_steps)
    future['Forecast'] = y_forecast.flatten()
    future['Historical'] = np.nan

    results = pd.concat([past, future], ignore_index=True) # appends datasets together
    print(results) # for debugging

    # graph
    fig = go.Figure()
    # adding scatter graph for historical data
    fig.add_trace(go.Scatter(x=results.Date, y=results.Historical, mode='lines', name='Previous'))
    # adding scatter graph for forecasted data
    fig.add_trace(go.Scatter(x=results.Date, y=results.Forecast, mode='lines', name='Forecast'))
    # adding title, legend and axis labels
    fig.update_layout(
        title=option + " Time Series Forecasting",
        xaxis_title="Date/Time",
        yaxis_title="Price",
        legend_title="Legend",
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # create JSON object to display graph in HTML

    forecasts = future[['Date', 'Forecast']] # creates new Pandas dataframe with only Date and Forecast columns
    return [graphJSON, forecasts] # return graph JSON and forecasts dataframe to generate CSV

def get_csv(dataframe):
    return dataframe.to_csv("./static/forecasts.csv", index=False) # creates CSV file within static directory (hosted by Flask server)
# Script for LSTM model
# Written by Maria Achim
# Started on 6th September 2023

import numpy as np # for multi-dimensional arrays
import math # calculating MSE, MAE and RMSE
import pandas as pd
import plotly.graph_objects as go # plotting graph
import yfinance as yf # data API

from sklearn.preprocessing import MinMaxScaler # for scaling data in preprocessing stage

# creating LSTM model
from keras.models import Sequential
from keras.layers import LSTM, Dense

time_step_dict = {"1y": [60, 30], "1m": [15, 5], "5d": [5, 1]}

model = Sequential()

def forecast_lstm(stock, period):
    ticker = yf.Ticker(stock)
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

    # graph
    fig = go.Figure()
    # adding scatter graph for historical data
    fig.add_trace(go.Scatter(x=results.Date, y=results.Historical, mode='lines', name='Previous'))
    # adding scatter graph for forecasted data
    fig.add_trace(go.Scatter(x=results.Date, y=results.Forecast, mode='lines', name='Forecast'))
    # adding title, legend and axis labels
    fig.update_layout(
        title="Time Series Forecasting",
        xaxis_title="Date/Time",
        yaxis_title="Price",
        legend_title="Legend",
    )
    fig.show() # show graph

forecast_lstm("AAPL", "1y")
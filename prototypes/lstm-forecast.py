# Script to show LSTM algorithm prototype for forecasting closing stock prices
# Written by Maria Achim
# Started on 8th September

import numpy as np # for multi-dimensional arrays
import pandas as pd
import plotly.graph_objects as go # plotting graph
import yfinance as yf # data API

from sklearn.preprocessing import MinMaxScaler # for scaling data in preprocessing stage
import tensorflow as tf

# creating LSTM model
from keras.models import Sequential
from keras.layers import LSTM, Dense

tf.random.set_seed(0) # makes code reproducible

# preprocessing
ticker = yf.Ticker('AMZN') # Apple stocks
historical = ticker.history(start="2023-01-01", end="2023-09-01", rounding=True) # gets data from past year
actual_data = ticker.history(start="2023-01-01", end="2023-11-01", rounding=True)

df = historical # for dataframe manipulation when plotting graph
historical.fillna(historical.mean()) # standardises data so there are no null values
historical = np.array(historical['Close']) # get close prices only

sc = MinMaxScaler(feature_range=(0, 1)) # scales each feature to be in the given range
aapl_scaled = sc.fit_transform(historical.reshape(-1, 1)) # fits data to scaler and transforms

lookback_time_steps = 60 # how many previous days are counted
forecast_time_steps = 30 # how far into the future forecasting occurs

# preparing data
X_train = []
y_train = []

# adding data to training datasets
for i in range(lookback_time_steps, len(historical) - forecast_time_steps + 1):
    X_train.append(aapl_scaled[i-lookback_time_steps:i])
    y_train.append(aapl_scaled[i:i+forecast_time_steps])

X_train, y_train = np.array(X_train), np.array(y_train) # cast to numpy array

# LSTM architecture
model = Sequential() # stack of layers where each layer has one input tensor and one output tensor
model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback_time_steps, 1))) # stacking LSTM layers for greater complexity
model.add(LSTM(units=50))
model.add(Dense(units=forecast_time_steps)) # dense layer - each neuron is connected to neurons from next layer
model.summary() # prints summary of model in terminal

# training LSTM model
model.compile(optimizer='adam', loss='mean_squared_error')
# adam - gradient descent algorithm
# MSE - predicts average squared difference between predicted and actual values
model.fit(X_train, y_train, batch_size=1, epochs=3) # trains model
# batch_size - number of samples to work through before updating internal model parameters
# epochs - number of times the algorithm works through the dataset

# generate forecasts
X_forecast = aapl_scaled[- lookback_time_steps:] # create testing dataset
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
# adding candlestick for actual data
fig.add_trace(go.Candlestick(x=actual_data.index, # candlestick chart - typically used for stocks
                open=actual_data['Open'],
                high=actual_data['High'],
                low=actual_data['Low'],
                close=actual_data['Close'],
                name='Actual Prices'))
# adding title, legend and axis labels
fig.update_layout(
    title="Time Series Forecasting",
    xaxis_title="Date/Time",
    yaxis_title="Price",
    legend_title="Legend",
)
fig.show() # show graph
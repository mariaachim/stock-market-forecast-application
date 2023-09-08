# Script to show LSTM algorithm prototype for forecasting closing stock prices
# Written by Maria Achim
# Started on 8th September

import numpy as np # for multi-dimensional arrays
import pandas as pd
import math # calculating MSE, MAE and RMSE
import plotly.graph_objects as go # plotting graph
import yfinance as yf # data API

from sklearn.preprocessing import MinMaxScaler # for scaling data in preprocessing stage
import tensorflow as tf

# creating LSTM model
from keras.models import Sequential
from keras.layers import LSTM, Dense


pd.options.mode.chained_assignment = None
tf.random.set_seed(0)

# preprocessing
ticker = yf.Ticker('AAPL')
historical = ticker.history(period='1y', rounding=True)
df = yf.download(tickers=['AAPL'], period='1y')
historical.fillna(historical.mean()) # standardises data so there are no null values
data = historical # for graph
historical = np.array(historical['Close']) # get close prices only

sc = MinMaxScaler(feature_range=(0, 1)) # scales each feature to be in the given range
aapl_scaled = sc.fit_transform(historical.reshape(-1, 1)) # fits data to scaler and transforms

lookback_time_steps = 60
forecast_time_steps = 30

# preparing data
X = []
y = []

for i in range(lookback_time_steps, len(historical) - forecast_time_steps + 1):
    X.append(aapl_scaled[i - lookback_time_steps: i])
    y.append(aapl_scaled[i: i + forecast_time_steps])

X = np.array(X)
y = np.array(y)

# LSTM architecture
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback_time_steps, 1)))
model.add(LSTM(units=50))
model.add(Dense(forecast_time_steps))

model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X, y, batch_size=1, epochs=3)

# generate forecasts
X_ = aapl_scaled[- lookback_time_steps:]
X_ = X_.reshape(1, lookback_time_steps, 1)

y_ = model.predict(X_).reshape(-1, 1)
y_ = sc.inverse_transform(y_)

# dataframe
past = df[['Close']].reset_index()
past.rename(columns={'index': 'Date', 'Close': 'Actual'}, inplace=True)
past['Date'] = pd.to_datetime(past['Date'])
past['Forecast'] = np.nan
past['Forecast'].iloc[-1] = past['Actual'].iloc[-1]

future = pd.DataFrame(columns=['Date', 'Actual', 'Forecast'])
future['Date'] = pd.date_range(start=past['Date'].iloc[-1] + pd.Timedelta(days=1), periods=forecast_time_steps)
future['Forecast'] = y_.flatten()
future['Actual'] = np.nan

results = pd.concat([past, future], ignore_index=True)
print(results)

# graph
fig = go.Figure()
fig.add_trace(go.Scatter(x=results.Date, y=results.Actual, mode='lines', name='Previous'))
fig.add_trace(go.Scatter(x=results.Date, y=results.Forecast, mode='lines', name='Forecast'))
fig.update_layout(
    title="Time Series Forecasting",
    xaxis_title="Date/Time",
    yaxis_title="Price",
    legend_title="Legend",
)
fig.show()
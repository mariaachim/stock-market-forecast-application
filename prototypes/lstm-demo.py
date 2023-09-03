import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import math

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error # unused module

from keras.models import Sequential
from keras.layers import LSTM, Dense

# preprocessing
ticker = yf.Ticker('AAPL')
historical = ticker.history(period='max', interval='1mo', rounding=True)
historical.fillna(historical.mean())
data = historical # for graph
historical = np.array(historical['Close'])

sc = MinMaxScaler(feature_range=(0, 1))
aapl_scaled = sc.fit_transform(historical.reshape(-1, 1))

# preparing training data
training_data_len = math.ceil(len(historical) * 0.8)
train_data = aapl_scaled[0: training_data_len, :]

X_train = []
y_train = []

for i in range(60, len(train_data)):
    X_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# preparing testing data
test_data = aapl_scaled[training_data_len-60:, :]
X_test = []
y_test = historical[training_data_len:]

for i in range(60, len(test_data)):
    X_test.append(test_data[i-60:i, 0])

X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# LSTM architecture
model = Sequential()
model.add(LSTM(100, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(LSTM(100, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))
model.summary()

# training LSTM model
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(X_train, y_train, batch_size=1, epochs=3)

# model predictions
predictions = model.predict(X_test)
predictions = sc.inverse_transform(predictions)
RMSE = np.sqrt(np.mean(predictions - y_test) ** 2)
print(RMSE)

# graph
train = data[:training_data_len]
validation = data[training_data_len:]
validation['Predictions'] = predictions
train.reset_index(inplace = True)
validation.reset_index(inplace = True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=train.Date, y=train.Close, mode='lines', name='Actual Price (Training Dataset)'))
fig.add_trace(go.Scatter(x=validation.Date, y=validation.Close, mode='lines', name='Actual Price'))
fig.add_trace(go.Scatter(x=validation.Date, y=validation.Predictions, mode='lines', name='Predicted Price'))
fig.update_layout(
    title="Time Series Forecasting using LSTM",
    xaxis_title="Date-Time",
    yaxis_title="Values",
    legend_title="Legend",
)
fig.show()
# Script to show LSTM algorithm prototype
# Written by Maria Achim
# Started on 2nd September 2023

import numpy as np # for multi-dimensional arrays
import math # calculating MSE, MAE and RMSE
import plotly.graph_objects as go # plotting graph
import yfinance as yf # data API

from sklearn.preprocessing import MinMaxScaler # for scaling data in preprocessing stage

# creating LSTM model
from keras.models import Sequential
from keras.layers import LSTM, Dense

# preprocessing
ticker = yf.Ticker('AAPL')
historical = ticker.history(period='max', interval='1mo', rounding=True)
historical.fillna(historical.mean()) # standardises data so there are no null values
data = historical # for graph
historical = np.array(historical['Close']) # get close prices only

sc = MinMaxScaler(feature_range=(0, 1)) # scales each feature to be in the given range
aapl_scaled = sc.fit_transform(historical.reshape(-1, 1)) # fits data to scaler and transforms

time_steps = 60

# preparing training data
training_data_len = math.ceil(len(historical) * 0.8) # last index for 80% of data
train_data = aapl_scaled[0: training_data_len, :] # training data

X_train = [] # input
y_train = [] # labels/outputs

# 60 time steps - how many prior days are considered when predicting the closing price of next day
for i in range(time_steps, len(train_data)):
    X_train.append(train_data[i-time_steps:i, 0])
    y_train.append(train_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train) # cast to numpy array
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1)) # changes dimensionality of array

# preparing testing data
test_data = aapl_scaled[training_data_len-time_steps:, :] # gets last 20% of data for testing
X_test = [] # inputs
y_test = historical[training_data_len:] # labels/outputs

# 60 time steps - use last 60 days to predict
for i in range(time_steps, len(test_data)):
    X_test.append(test_data[i-time_steps:i, 0])

X_test = np.array(X_test) # cast to numpy array
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1)) # changes dimentionality of array

# LSTM architecture
model = Sequential() # stack of layers where each layer has one input tensor and one output tensor
model.add(LSTM(units=100, return_sequences=True, input_shape=(X_train.shape[1], 1))) # stacking LSTM layers for greater complexity
model.add(LSTM(units=100, return_sequences=False))
model.add(Dense(units=25)) # dense layer - each neuron is connected to neurons from next layer
model.add(Dense(units=1))
model.summary() # prints summary of model in terminal

# training LSTM model
model.compile(optimizer='adam', loss='mean_squared_error') 
# adam - gradient descent algorithm
# MSE - predicts average squared difference between predicted and actual values 
model.fit(X_train, y_train, batch_size=1, epochs=3) # trains model
# batch_size - number of samples to work through before updating internal model parameters
# epochs - number of times the algorithm works through the dataset

# model predictions
predictions = model.predict(X_test) # predicts label of testing dataset
predictions = sc.inverse_transform(predictions) # scales data to original transformations
RMSE = np.sqrt(np.mean(predictions - y_test) ** 2) # calculates root mean squared error
MSE = RMSE ** 2 # calculates mean squared error
MAE = np.mean(abs(predictions - y_test)) # calculates mean absolute error
# printing errors
print("Root mean squared error: " + str(RMSE))
print("Mean squared error: " + str(MSE))
print("Mean absolute error: " + str(MAE))

# graph
train = data[:training_data_len] # gets training data
validation = data[training_data_len:] # gets testing data
validation['Predictions'] = predictions # gets predictions
train.reset_index(inplace = True) # use default index for dataframe
validation.reset_index(inplace = True)

fig = go.Figure() # creates plot
# adding scatter graph for actual prices from training dataset
fig.add_trace(go.Scatter(x=train.Date, y=train.Close, mode='lines', name='Actual Price (Training Dataset)'))
# adding scatter graph for actual prices from testing dataset
fig.add_trace(go.Scatter(x=validation.Date, y=validation.Close, mode='lines', name='Actual Price (Testing Dataset)'))
# adding scatter graph for predicted prices
fig.add_trace(go.Scatter(x=validation.Date, y=validation.Predictions, mode='lines', name='Predicted Price'))
# adding title, legend and axis labels
fig.update_layout(
    title="Time Series Forecasting using LSTM",
    xaxis_title="Date-Time",
    yaxis_title="Values",
    legend_title="Legend",
)
fig.show() # show graph
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import plotly
import json
import numpy as np
import pandas as pd
import math

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
                                 name='Market Data'))
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

def trendlines(option):
    ticker = yf.Ticker(option)
    historical = ticker.history(period='2mo', interval='1d', rounding=True) # 2 months of historical data
    scatter = px.scatter(historical, x=historical.index, y=historical['Close'], trendline='ols') # generate trendline from plotting scatter graph
    trendline = scatter.data[1] # only get trendline generated
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=historical.index,
                                 open=historical['Open'],
                                 high=historical['High'],
                                 low=historical['Low'],
                                 close=historical['Close'],
                                 name='Market Data'))
    fig.add_trace(trendline) # display trendline over candlestick chart
    fig.update_layout(title=option + " share price", yaxis_title='Stock Price', autosize=False, width=800, height=500) # title and axis label
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # export to JSON
    return graphJSON

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

def heatmap(favourites):
    # downloading market from previous two days
    returns = yf.download(tickers=favourites, period='2d', interval='1d', group_by='ticker', auto_adjust=True, prepost=True, threads=True, proxy=None)
    returns = returns.iloc[:, returns.columns.get_level_values(1) == 'Close'] # getting Close prices
    returns.columns = returns.columns.droplevel(1) # remove row with "Close" label

    returns = round(returns.pct_change()*100, 2) # calculating percentage change between days
    returns = returns.iloc[1:].values.tolist()[0] # remove date and convert dataframe to list

    # this code is used to change to formatting of heatmap
    num_rows = round(math.sqrt(len(favourites))) # calculate optimal number of rows based on number of tickers
    heatmap_names_list = [favourites[i : i+num_rows] for i in range(0, len(favourites), num_rows)] # split names into sublists
    heatmap_returns_list = [returns[i : i+num_rows] for i in range(0, len(returns), num_rows)] # split percentage change into sublists
    print(heatmap_returns_list)

    # generate heatmap
    fig = go.Figure(data=go.Heatmap(
                        z=heatmap_returns_list,
                        text=heatmap_names_list,
                        texttemplate="%{text}",
                        textfont={"size":20},
                        colorscale="RdYlGn"
    ))

    fig.update_layout(title="Favourites Heatmap", autosize=False, width=1000, height=750) # title and axis label
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # export to JSON
    return graphJSON

def compare_favourites(favourites):
    # downloading historical market data from past year
    historical = yf.download(tickers=favourites, period='1y', interval='1d', group_by='ticker', auto_adjust=True, prepost=True, threads=True, proxy=None)
    historical = historical.iloc[:, historical.columns.get_level_values(1) == 'Close'] # getting Close prices
    print(historical)

    fig = go.Figure()

    # creates new trace for each favourites entry
    for i in range(len(favourites)):
        fig.add_trace(go.Scatter(x=historical[favourites[i]].index, y=historical[favourites[i]]['Close'], name=favourites[i]))

    fig.update_layout(title="Stock Comparison", autosize=False, width=800, height=500) # title and axis label
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # export to JSON
    return graphJSON
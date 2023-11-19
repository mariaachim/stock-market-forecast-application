import math
import yfinance as yf
import plotly.graph_objects as go

symbols = ["AMZN", "AAPL", "TLSA", "MSFT", "GS", "META", "GOOGL"] # hardcoding tickers to use

# downloading market from previous two days
returns = yf.download(tickers=symbols, period='2d', interval='1d', group_by='ticker', auto_adjust=True, prepost=True, threads=True, proxy=None)
returns = returns.iloc[:, returns.columns.get_level_values(1) == 'Close'] # getting Close prices
returns.columns = returns.columns.droplevel(1) # remove row with "Close" label

returns = round(returns.pct_change()*100, 2) # calculating percentage change between days
returns = returns.iloc[1:].values.tolist()[0] # remove date and convert dataframe to list

# this code is used to change to formatting of heatmap
num_rows = round(math.sqrt(len(symbols))) # calculate optimal number of rows based on number of tickers
heatmap_names_list = [symbols[i : i+num_rows] for i in range(0, len(symbols), num_rows)] # split names into sublists
heatmap_returns_list = [returns[i : i+num_rows] for i in range(0, len(returns), num_rows)] # split percentage change into sublists

# generate heatmap
fig = go.Figure(data=go.Heatmap(
                    z=heatmap_returns_list,
                    text=heatmap_names_list,
                    texttemplate="%{text}",
                    textfont={"size":20},
                    colorscale="RdYlGn"
))

fig.show() # show heatmap
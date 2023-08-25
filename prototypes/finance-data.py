import yfinance as yf
import plotly.graph_objects as go

option = "AAPL" # hardcoded variable for stock
aapl = yf.Ticker(option) # stock symbol that descibes information about company stock

aapl_historical = aapl.history(period='7d', interval='15m', rounding=True) # getting data from the past 7 days every 15 mins

fig = go.Figure()
fig.add_trace(go.Candlestick(x=aapl_historical.index, # candlestick chart - typically used for stocks
                open=aapl_historical['Open'],
                high=aapl_historical['High'],
                low=aapl_historical['Low'],
                close=aapl_historical['Close'],
                name='market data'))
fig.update_layout(title = option + " share price", yaxis_title='Stock Price') # setting axis label and title
fig.update_xaxes( # ability to select different time ranges
    rangeslider_visible=True,
    rangeselector=dict(
        buttons=list([
            dict(count=15, label='15m', step="minute", stepmode="backward"),
            dict(count=45, label='45m', step="minute", stepmode="backward"),
            dict(count=1, label='1h', step="hour", stepmode="backward"),
            dict(count=6, label='6h', step="hour", stepmode="backward"),
            dict(step="all")
        ])
    )
)

fig.show()
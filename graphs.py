import yfinance as yf
import plotly.graph_objects as go
import plotly
import json

def show_graph(option): # function to draw graph of historical stock prices with given stock and time period
    ticker = yf.Ticker(option)
    historical = ticker.history(period='max', interval='1mo', rounding=True) # all-time stock prices

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
                  dict(count=15, label='15m', step="minute", stepmode="backward"),
                  dict(count=45, label='45m', step="minute", stepmode="backward"),
                  dict(count=1, label='1h', step="hour", stepmode="backward"),
                  dict(count=6, label='6h', step="hour", stepmode="backward"),
                  dict(step="all")
            ])
        )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
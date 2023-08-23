import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

aapl = yf.Ticker("aapl")

aapl_historical = aapl.history(period='5d', interval='15m', rounding=True)

fig = go.Figure()
fig.add_trace(go.Candlestick(x=aapl_historical.index,
                open=aapl_historical.Open,
                high=aapl_historical.High,
                low=aapl_historical.Low,
                close=aapl_historical.Close))
fig.update_xaxes(
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
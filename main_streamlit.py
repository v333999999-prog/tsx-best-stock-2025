
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="TSX Top Momentum", layout="wide")

TSX_TICKERS_CSV = "data/tsx_tickers.csv"
LOOKBACK_MINUTES = st.sidebar.number_input("Momentum lookback (minutes)", 5, 1440, 60)
REFRESH_SECONDS = st.sidebar.number_input("Auto refresh (seconds)", 10, 600, 30)
TOP_N = 1

st.title("🇨🇦 TSX — Top Momentum Stock")

@st.cache_data(ttl=60)
def load_tickers():
    try:
        df = pd.read_csv(TSX_TICKERS_CSV)
        return df['ticker'].astype(str).tolist()
    except Exception:
        return ["BNS.TO","RY.TO","TD.TO","BMO.TO","ENB.TO"]

def fetch_recent_close(ticker, period_minutes):
    end = datetime.utcnow()
    start = end - timedelta(minutes=period_minutes + 10)
    try:
        data = yf.download(ticker, start=start, end=end, interval="1m", progress=False, threads=False)
        if data.empty:
            data = yf.download(ticker, period="2d", interval="5m", progress=False, threads=False)
    except:
        data = yf.download(ticker, period="2d", interval="5m", progress=False, threads=False)
    return data

def compute_momentum_score(df, lookback_minutes):
    if df is None or df.empty:
        return None
    df = df.dropna(subset=['Close'])
    if df.empty:
        return None
    last = df['Close'].iloc[-1]
    times = pd.to_datetime(df.index)
    cutoff = times.max() - pd.Timedelta(minutes=lookback_minutes)
    past_rows = df[times <= cutoff]
    past = df['Close'].iloc[-1] if past_rows.empty else past_rows['Close'].iloc[-1]
    score = (last / past - 1) * 100.0
    return {'score': score, 'last': float(last), 'past': float(past)}

def compute_trade_params(last_price):
    entry = last_price
    stop = round(max(last_price * 0.995, last_price - 0.50), 2)
    target = round(last_price * 1.02, 2)
    return entry, stop, target

tickers = load_tickers()
results = []

for t in tickers:
    try:
        df = fetch_recent_close(t, LOOKBACK_MINUTES)
        res = compute_momentum_score(df, LOOKBACK_MINUTES)
        if res:
            res.update({'ticker': t})
            results.append(res)
    except:
        pass

if not results:
    st.warning("No data available right now.")
    st.stop()

df_res = pd.DataFrame(results).sort_values("score", ascending=False).reset_index(drop=True)
top = df_res.head(TOP_N).iloc[0]
ticker = top['ticker']
score = round(top['score'], 2)
last_price = top['last']
entry, stop, target = compute_trade_params(last_price)

col1, col2 = st.columns([2,3])
with col1:
    st.metric("Top Momentum Stock", ticker, delta=f"{score}%")
    st.write(f"Last Price: {last_price:.2f} CAD")
    st.write(f"Entry: **{entry:.2f}**")
    st.write(f"Stop-loss: **{stop:.2f}**")
    st.write(f"Target: **{target:.2f}**")
with col2:
    st.subheader("Top Momentum Table")
    st.dataframe(df_res[['ticker','score','last','past']].rename(columns={'last':'last_close','past':'close_past'}).round(3).head(20))

st.markdown("---")
st.caption(f"Auto-refresh every {REFRESH_SECONDS} seconds. Data: Yahoo Finance")

if REFRESH_SECONDS > 0:
    st.write(f"<script>setTimeout(()=>{{window.location.reload()}},{REFRESH_SECONDS*1000});</script>", unsafe_allow_html=True)

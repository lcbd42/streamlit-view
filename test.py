import ccxt
import time
import streamlit as st

# 바이낸스 선물 거래소 인스턴스 생성
exchange = ccxt.binance({
    'options': {
        'defaultType': 'future',
    }
})

# 모든 선물 시장(거래 페어) 정보 가져오기
markets = exchange.load_markets()
usdt_pairs = [market for market in markets if market.startswith('A') and market.endswith('/USDT')]
usdt_pairs.sort()

previous_prices = {pair: None for pair in usdt_pairs}
one_minute_ago_prices = {pair: None for pair in usdt_pairs}

removed_pairs = []

def fetch_and_display_prices():
    global removed_pairs
    global usdt_pairs
    global one_minute_ago_prices
    current_prices = {}

    for pair in usdt_pairs:
        try:
            ticker = exchange.fetch_ticker(pair)
            current_prices[pair] = ticker['last']
        except Exception as e:
            current_prices[pair] = None

    removed_pairs = [pair for pair in usdt_pairs if current_prices[pair] is None]
    valid_pairs = {pair: current_prices[pair] for pair in usdt_pairs if current_prices[pair] is not None}

    st.title("'A'로 시작하는 USDT Pairs Prices (Futures)")

    if not valid_pairs:
        st.write("No valid data available for the selected pairs.")
    else:
        for pair in valid_pairs:
            previous_price = previous_prices.get(pair)
            current_price = valid_pairs[pair]
            one_minute_ago_price = one_minute_ago_prices.get(pair)

            if previous_price is not None:
                if abs((current_price - previous_price) / previous_price) >= 0.01:
                    st.write(f'{pair}: {previous_price} USDT -> {current_price} USDT')
                
                if one_minute_ago_price is not None and abs((current_price - one_minute_ago_price) / one_minute_ago_price) >= 0.01:
                    change_rate = ((current_price - one_minute_ago_price) / one_minute_ago_price) * 100
                    st.write(f"1분 변동률: {change_rate:.2f}%")
            else:
                st.write(f'{pair}: (N/A), {current_price} USDT')

            previous_prices[pair] = current_price

    st.write(f"\nValid pairs count: {len(valid_pairs)}")
    st.write(f"Removed pairs count: {len(removed_pairs)}")

    one_minute_ago_prices = current_prices.copy()

# Streamlit 실시간 업데이트 설정
while True:
    fetch_and_display_prices()
    time.sleep(60)


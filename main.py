import streamlit as st
import pandas as pd
from datetime import time
from get_stock_data import *


@st.cache_data(ttl=5)
def get_option_prices(code, start_date, end_date):
    ret, option_chain = quote_context.get_option_chain(code=code, start=start_date, end=end_date,
                                                       option_type=OptionType.CALL)
    if ret != RET_OK:
        st.write('error:', options_expiration)
        st.stop()
    option_chain = option_chain.loc[(option_chain["strike_price"] > strike_price_range[0])
                                    & (option_chain["strike_price"] < strike_price_range[1])]
    # st.write(option_chain)

    options_code = option_chain["code"].values.tolist()
    options_strike = option_chain["strike_price"].values.tolist()
    # st.write(options_code)
    ret, message = quote_context.subscribe(code_list=options_code,
                                           subtype_list=[SubType.ORDER_BOOK, TRADING_PERIOD],
                                           subscribe_push=False)
    if ret != RET_OK:
        st.write('error:', message)
        st.stop()

    strike_price = list()
    bid_price = list()
    for index, c_option in enumerate(options_code):
        ret, data = quote_context.get_order_book(c_option, num=3)  # 获取一次 3 档实时摆盘数据
        if ret != RET_OK:
            st.write('error:', data)
            st.stop()
        bp = float(data['Bid'][0][0] if len(data['Bid']) != 0 else 0)
        ap = float(data['Ask'][0][0] if len(data['Ask']) != 0 else 0)
        mp = ((bp if bp > 0 else ap) + (ap if ap > 0 else bp)) / 2
        sp = options_strike[index]
        if mp != 0:
            strike_price.append(sp)
            bid_price.append(mp)

    series = pd.Series(bid_price, index=strike_price, name="price")
    return series


if __name__ == '__main__':
    with st.container():
        col1, col2 = st.columns([2, 2])
        with col1:
            code = st.selectbox("Which stock would you like to see?",
                                code_cfg.keys())
            ret, options_expiration = quote_context.get_option_expiration_date(code=code)
        with col2:
            st.button("Start")
    if ret != RET_OK:
        st.write('error:', options_expiration)
        st.stop()
    # dates = st.multiselect(
    #     'Which expiration date would you like ?',
    #     options_expiration)
    strike_time_list = options_expiration['strike_time'].tolist()
    start_date, end_date = st.select_slider(
        'Select a range of expiration date:',
        options=strike_time_list,
        value=(strike_time_list[0], strike_time_list[1]))

    # 选择价格范围
    strike_price_range = st.slider(
        'Select a range of strike price', code_cfg[code][0], code_cfg[code][1], code_cfg[code][2])

    # 遍历dates
    option_price = pd.DataFrame()
    for date in [start_date, end_date]:
        series = get_option_prices(code, date, date)
        option_price[date] = series
    st.line_chart(option_price)

    option_t = option_price.T
    # 遍历option_t的列名
    stp = st.multiselect(
        'Select you strike prices',
        option_t.columns)
    option_t = option_t[stp]
    st.line_chart(option_t)

    ret, data = quote_context.query_subscription()
    if ret == RET_OK:
        data
    else:
        print('error:', data)

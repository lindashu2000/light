import streamlit as st
import pandas as pd
from datetime import time
from get_stock_data import *
from stock_cfg import *
from plot import *

if __name__ == '__main__':
    with st.container():
        col1, col2 = st.columns([2, 2])
        with col1:
            code = st.selectbox("Which stock would you like to see?",
                                code_cfg.keys())
            ret, options_expiration = quote_context.get_option_expiration_date(code=code)
        with col2:
            if ret != RET_OK:
                st.write('error:', options_expiration)
                st.stop()
            dates = st.multiselect(
                'Which expiration date would you like ?',
                options_expiration)

    # 选择价格范围
    strike_price_range = st.slider(
        'Select a range of strike price', code_cfg[code][0], code_cfg[code][1], code_cfg[code][2])

    # 遍历dates
    option_chain = pd.DataFrame()
    for date in dates:
        ret, option_chain = quote_context.get_option_chain(code=code, start=date, end=date,
                                                           option_type=OptionType.CALL)
        if ret != RET_OK:
            st.write('error:', options_expiration)
            st.stop()
        option_chain = option_chain.loc[(option_chain["strike_price"] > strike_price_range[0])
                                        & (option_chain["strike_price"] < strike_price_range[1])]
        st.write(option_chain)

        options_code = option_chain["code"].values.tolist()
        st.write(options_code)
        ret, message = quote_context.subscribe(code_list=options_code,
                                               subtype_list=[SubType.ORDER_BOOK, TRADING_PERIOD],
                                               subscribe_push=False)
        if ret != RET_OK:
            st.write('error:', message)
            st.stop()

        strike_price = list()
        bid_price = list()
        for c_option in options_code:
            ret, data = quote_context.get_order_book(c_option, num=3)  # 获取一次 3 档实时摆盘数据
            if ret != RET_OK:
                st.write('error:', data)
                st.stop()
            bp = float(data['Bid'][0][0])
            ap = float(data['Ask'][0][0])
            mp = ((bp if bp > 0 else ap) + (ap if ap > 0 else bp)) / 2
            sp = int(c_option[-6:]) / 1000
            if mp != 0:
                strike_price.append(sp)
                bid_price.append(mp)

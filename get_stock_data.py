from futu import *

############################ 全局变量设置 ############################
FUTUOPEND_ADDRESS = '127.0.0.1'  # FutuOpenD 监听地址
FUTUOPEND_PORT = 11111  # FutuOpenD 监听端口

TRADING_ENVIRONMENT = TrdEnv.SIMULATE  # 交易环境：真实 / 模拟
TRADING_MARKET = TrdMarket.HK  # 交易市场权限，用于筛选对应交易市场权限的账户
TRADING_PWD = '123456'  # 交易密码，用于解锁交易
TRADING_PERIOD = KLType.K_1M  # 信号 K 线周期
TRADING_SECURITY = 'HK.TCH230330C390000'  # 交易标的
FAST_MOVING_AVERAGE = 1  # 均线快线的周期
SLOW_MOVING_AVERAGE = 3  # 均线慢线的周期

code_cfg = {'HK.00700': [200, 600, (300, 500)],
            'HK.09988': [70, 150, (80, 120)],
            'US.FUTU': [30, 80, (40, 65)]}

quote_context = OpenQuoteContext(host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT)  # 行情对象
trade_context = OpenSecTradeContext(filter_trdmarket=TRADING_MARKET, host=FUTUOPEND_ADDRESS, port=FUTUOPEND_PORT,
                                    security_firm=SecurityFirm.FUTUSECURITIES)  # 交易对象，根据交易品种修改交易对象类型


def subscribe_option_prices(code, start_date, end_date, min_price, max_price):
    ret, option_chain = quote_context.get_option_chain(code=code, start=start_date, end=end_date,
                                                       option_type=OptionType.CALL)
    if ret != RET_OK:
        return ret, "error: get_option_chain"
    option_chain = option_chain.loc[(option_chain["strike_price"] >= min_price)
                                    & (option_chain["strike_price"] <= max_price)]
    print("option_chain" + option_chain)

    options_code = option_chain["code"].values.tolist()

    options_strike = option_chain["strike_price"].values.tolist()
    ret, message = quote_context.subscribe(code_list=options_code,
                                           subtype_list=[SubType.ORDER_BOOK, TRADING_PERIOD],
                                           subscribe_push=False)
    if ret != RET_OK:
        return ret, message
    return RET_OK


def get_option_prices(code, start_date, end_date, min_price, max_price):
    ret, option_chain = quote_context.get_option_chain(code=code, start=start_date, end=end_date,
                                                       option_type=OptionType.CALL)
    if ret != RET_OK:
        return ret, "error: get_option_chain"
    option_chain = option_chain.loc[(option_chain["strike_price"] >= min_price)
                                    & (option_chain["strike_price"] <= max_price)]
    # st.write(option_chain)

    options_code = option_chain["code"].values.tolist()
    options_strike = option_chain["strike_price"].values.tolist()
    # st.write(options_code)
    ret, message = quote_context.subscribe(code_list=options_code,
                                           subtype_list=[SubType.ORDER_BOOK, TRADING_PERIOD],
                                           subscribe_push=False)
    if ret != RET_OK:
        return ret, message

    strike_price = list()
    bid_price = list()
    for index, c_option in enumerate(options_code):
        ret, data = quote_context.get_order_book(c_option, num=3)  # 获取一次 3 档实时摆盘数据
        if ret != RET_OK:
            return ret, data

        bp = float(data['Bid'][0][0])
        ap = float(data['Ask'][0][0])
        mp = ((bp if bp > 0 else ap) + (ap if ap > 0 else bp)) / 2
        sp = options_strike[index]
        if mp != 0:
            strike_price.append(sp)
            bid_price.append(mp)

    series = pd.Series(bid_price, index=strike_price, name="price")
    return series

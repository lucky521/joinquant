# 导入函数库
import jqdata

# 初始化函数，设定基准等等
def initialize(context):
    # 设定基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error') 
    
    ### 设置账户类型 ###
    
    ## 设置三个账户，各账户资金为策略总资金的三分之一
    init_cash = context.portfolio.starting_cash/3

    # 设定subportfolios[0]为 股票和基金账户，初始资金为 init_cash 变量代表的数值
    # 设定subportfolios[1]为 金融期货账户，初始资金为 init_cash 变量代表的数值
    # 设定subportfolios[2]为 融资融券账户，初始资金为 init_cash 变量代表的数值
    set_subportfolios([SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='index_futures'),\
                       SubPortfolioConfig(cash=init_cash, type='stock_margin')])

    ### 股票、期货、融资融券相关设定使用默认设置，这里暂不做设定 ###

    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
      # 开盘前运行
    run_daily(before_market_open, time='before_open', reference_security='000300.XSHG') 
      # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
      # 收盘后运行
    run_daily(after_market_close, time='after_close', reference_security='000300.XSHG')


## 开盘前运行函数     
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：'+str(context.current_dt.time()))

    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    send_message('美好的一天~')

    ## 要操作的股票(g.为全局变量)：
    # 股票代码（万科A）
    g.stock = '000002.XSHE'
    # 融资融券代码（平安银行）
    g.rzrq = '000001.XSHE'
    # 股指期货代码（下月合约）
    g.ccfx = get_stock_index_futrue_code(context,'IF',month='next_month')

## 开盘时运行函数
def market_open(context):
    # 确定时间是周几
    weekday = context.current_dt.isoweekday()
    log.info('今天是周 %s' % weekday)

    # 操作代码
    stock = g.stock
    rzrq = g.rzrq
    ccfx = g.ccfx

    ## 操作判定
    if weekday == 1:
        # 股票操作
        log.info('买入1000股万科A')
        order(stock, 1000, pindex=0)

        # 期货操作
        log.info('做多1手下月合约')
        order(ccfx, 1, side='long', pindex=1)

        # 融资操作
        log.info('融资买入1000股平安银行')
        margincash_open(rzrq, 1000, pindex=2)
        
    elif weekday == 2:
        # 股票操作
        log.info('卖出1000股万科A')
        order(stock, -1000, pindex=0)

        # 期货操作
        log.info('平多仓：下月合约')
        order_target(ccfx, 0, side='long', pindex=1)

        # 融资操作
        log.info('卖券还款1000股平安银行')
        margincash_close(rzrq, 1000, pindex=2)
    
    elif weekday == 3:
        # 期货操作
        log.info('做空1手下月合约')
        order(ccfx, 1, side='short', pindex=1)

        # 融资操作
        log.info('融券卖出1000股平安银行')
        marginsec_open(rzrq, 1000, pindex=2)

    elif weekday == 4:
       # 期货操作
        log.info('平仓：下月合约')
        order_target(ccfx, 0, side='short', pindex=1)

        # 融券操作
        log.info('买券还券1000股平安银行')
        marginsec_close(rzrq, 1000, pindex=2)


## 收盘后运行函数  
def after_market_close(context):
    log.info(str('函数运行时间(after_market_close):'+str(context.current_dt.time())))
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：'+str(_trade))
    log.info('一天结束')
    log.info('##############################################################')

    
    
########################## 获取期货合约信息，请保留 #################################

# 获取当天时间正在交易的股指期货合约
def get_stock_index_futrue_code(context,symbol,month='current_month'):
    '''
    获取当天时间正在交易的股指期货合约。其中:
    symbol:
            'IF' #沪深300指数期货
            'IC' #中证500股指期货
            'IH' #上证50股指期货
    month:
            'current_month' #当月
            'next_month'    #隔月
            'next_quarter'  #下季
            'skip_quarter'  #隔季
    '''
    display_name_dict = {'IC':'中证500股指期货','IF':'沪深300指数期货','IH':'上证50股指期货'}
    month_dict = {'current_month':0, 'next_month':1, 'next_quarter':2, 'skip_quarter':3}

    display_name = display_name_dict[symbol]
    n = month_dict[month]
    dt = context.current_dt.date()
    a = get_all_securities(types=['futures'], date=dt)
    try:
        df = a[(a.display_name == display_name) & (a.start_date <= dt) & (a.end_date >= dt)]
        return df.index[n]
    except:
        return 'WARRING: 无此合约'

# 获取当天时间正在交易的国债期货合约
def get_treasury_futrue_code(context,symbol,month='current'):
    '''
    获取当天时间正在交易的国债期货合约。其中:
    symbol:
            'T' #10年期国债期货
            'TF' #5年期国债期货
    month:
            'current' #最近期
            'next'    #次近期
            'skip'    #最远期
    '''
    display_name_dict = {'T':'10年期国债期货','TF':'5年期国债期货'}
    month_dict = {'current':0, 'next':1, 'skip':2}

    display_name = display_name_dict[symbol]
    n = month_dict[month]
    dt = context.current_dt.date()
    a = get_all_securities(types=['futures'], date=dt)
    try:
        df = a[(a.display_name == display_name) & (a.start_date <= dt) & (a.end_date >= dt)]
        return df.index[n]
    except:
        return 'WARRING: 无此合约'

# 获取金融期货合约到期日
def get_CCFX_end_date(fature_code):
    # 获取金融期货合约到期日
    return get_security_info(fature_code).end_date

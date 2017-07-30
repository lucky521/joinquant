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
    
    ### 融资融券相关设定 ###
    # 设置账户类型: 融资融券账户
    set_subportfolios([SubPortfolioConfig(cash=context.portfolio.cash, type='stock_margin')])
    
    ## 融资相关设定
    # 设定融资利率: 年化8%, 默认8%
    set_option('margincash_interest_rate', 0.08)
    # 设置融资保证金比率: 150%, 默认100%
    set_option('margincash_margin_rate', 1.5)
    
    ## 融券相关设定
    # 设定融券利率: 年化10%, 默认10%
    set_option('marginsec_interest_rate', 0.10)
    # 设定融券保证金比率: 150%, 默认100%
    set_option('marginsec_margin_rate', 1.5)
    
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

    # 要操作的股票（g.为全局变量）
    # 融资买入的股票代码（中国银行）
    g.rz_stock = '601988.XSHG'
    # 融券卖出的股票代码（平安银行）
    g.rq_stock = '000001.XSHE'

## 开盘时运行函数
def market_open(context):
    # 确定时间是周几
    weekday = context.current_dt.isoweekday()
    log.info("今天是周 %s" % weekday)
    # 融资买入的股票代码（中国银行）
    rz_stock = g.rz_stock
    # 融券卖出的股票代码（平安银行）
    rq_stock = g.rz_stock

    # 操作判定
    if weekday in (1, 2):
        # 融资操作
        log.info("融资买入10000股中国银行")
        margincash_open(rz_stock, 10000)

        # 融券操作
        log.info("融券卖出10000股平安银行")
        marginsec_open(rq_stock, 10000)
        
    elif weekday == 3:
        # 融资操作
        log.info("卖券还款10000股中国银行")
        margincash_close(rz_stock, 10000)

        # 融券操作
        log.info("买券还券10000股平安银行")
        marginsec_close(rq_stock, 10000)
        
    elif weekday == 4:
        # 融资操作
        log.info("直接还钱10000元")
        margincash_direct_refund(10000)

        # 融券操作
        log.info("买入10000股平安银行, 然后直接还券10000股平安银行")
        order(rq_stock, 10000, side='long')
        marginsec_direct_refund(rq_stock, 10000) 

## 收盘后运行函数  
def after_market_close(context):
    # 查看融资融券账户相关相关信息(更多请见API-对象-SubPortfolio)
    p = context.portfolio.subportfolios[0]
    log.info('- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    log.info('查看融资融券账户相关相关信息(更多请见API-对象-SubPortfolio)：')
    log.info('总资产：',p.total_value)
    log.info('净资产：',p.net_value)
    log.info('总负债：',p.total_liability)
    log.info('融资负债：',p.cash_liability)
    log.info('融券负债：',p.sec_liability)
    log.info('利息总负债：',p.interest)
    log.info('可用保证金：',p.available_margin)
    log.info('维持担保比例：',p.maintenance_margin_rate)
    log.info('账户所属类型：',p.type)
    log.info('##############################################################')


    
    
    

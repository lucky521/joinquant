# joinquant 量化交易

## 基础函数

    get_all_securities
    get_industry_stocks
    get_fundamentals
   
   
## 需要实现的接口方法

    initialize(context)   初始化时调用一次。Context对象, 存放有当前的账户/股票持仓信息。
    
    run_monthly(func, monthday, time='open', reference_security)  定期运行函数

    run_weekly(func, weekday, time='open', reference_security)
    
    run_daily(func, time='open', reference_security)
    
    handle_data(context, data)    
    

## 数据源

    get_all_securities(['futures'])
    深交所股票代码后缀为 XSHE
    上交所股票代码后缀为 XSHG 


## 其他

### 基准收益

默认使用沪深300指数的收益作为基准收益。沪深300指数编制目标是反映中国证券市场股票价格变动的概貌和运行状况，并能够作为投资业绩的评价标准，为指数化投资和指数衍生产品创新提供基础条件。

### 未来函数

回测时使用未来数据的函数。

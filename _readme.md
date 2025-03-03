

## Page 1 LivePositon

1. 使用 oms db 的持仓数据，显示各产品的各品种持仓市值图
2. 81Server AGP.FixedIntervalScheduler 定时执行获取各个 oms db 的持仓数据
3. 开盘期间，每间隔 2 分钟运行一次


## Page 2 PnLTracking

1. PM vs Live / Paper 的 perInitX 对比图
2. 数据在 98Server 上生成
3. 81Server AGP.FixedIntervalScheduler 定时执行获 Tracking 数据
4. T+1 08:30 更新


## Page 3 Ticker

1. 各品种的基本合约信息，如 手续费率、保证金率等。 general ticker info 
2. 通过 wind 获取
3. 20:30 更新


## Page 5 CancelRate

1. 分品种计算 下单量 / 成交量 指标
2. 数据在 98Server 上生成， _DailyRun.9.AGP.OrderFilledRateCheck_OmsDB
3. 81Server 直接读取共享文件夹中的文件
4. 21:10 更新


## Page 6 Position-LongShortValue

1. 产品/组合 多空持仓市值的日数据线，按每日收盘持仓市值计算
2. 数据在 81Server 上生成， AGP.TradingReview.HoldingPositionAnalysis 
3. 从 QMReport DB 下载持仓数据；从 DSDataDB 中下载 DailyBar 数据；计算持仓市值
4. DSDataDB 中的 DailyBar 数据，在 81Server 中生成 AGP.DS.GenDailyBar
5. T+1 09:50 更新


## Page 7 Commission

1. 每日佣金情况
2. 数据在 98Server 上生成， _DailyRun.8.TradesFrequencyCheck_fromQMReportCenter ， 使用 QMReport 数据
3. T+1 08:00 更新

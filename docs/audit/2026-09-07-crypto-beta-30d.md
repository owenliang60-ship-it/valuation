# Crypto BTC Beta 30D 验收

已确认业务口径：币安USDT永续，昨日完整UTC交易日成交额前50，连续31收盘价产生30日简单收益率；beta降序，附相关系数。

- 本地 beta + crypto suite：30 passed。
- 云端 Python3.10 真实 dry-run：as_of=2026-09-06，528/528排名数据齐全，50入选、46有效，补K线24次。未发Telegram，未修改共享行情缓存。
- 独立 numpy.linalg.lstsq（含截距）对拍46个；最大beta差1.3322676295501878e-15，相关系数差<1e-10。
- 无效四个：MARSCOIN、PONS、哈基米、牛来；历史不足31日/缺日，保留排名位置显示N/A。
- 主线程单遍review：补Telegram旧Markdown特殊字符转义及daily异常冒泡测试，未留阻断项。
- 原daily入口SHA256：6df8b32566b01c65f996d2003a6a2ed199b4d7c8e789baaa4768e4ad6fa144e8。

## 部署步骤
Finance git版本部署后，在Quant现有cron锁下，验证旧入口哈希，备份入口，再复制薄适配器及新入口；原08:06 cron不变。回滚从备份恢复daily入口即可。

正式定时运行尚未自然触发；本次不额外手动发送榜单。

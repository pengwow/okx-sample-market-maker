# OKX示例做市商

## 概述
这是一个非官方的Python做市商示例，使用[OKX V5 API](https://www.okx.com/docs-v5/en/#overview)，基于[OKX V5 API PYTHON SDK](https://github.com/okxapi/python-okx)开发。

本项目旨在为用户提供一种解决方案，帮助构建一个能够精确及时地订阅市场数据更新、订单更新以及账户和持仓更新的交易系统，基于策略思想通过订单管理流程发送订单操作请求，并在交易系统之上编写任意自定义策略逻辑。本项目纯粹用于展示或研究目的。强烈建议用户在任何开发过程中使用[模拟交易环境](https://www.okx.com/docs-v5/en/#overview-demo-trading-services)。本项目不保证任何追求盈利的策略或提供流动性的义务。

本项目与OKX交易机器人功能无关。如需使用多种策略轻松进行交易，请参考[OKX交易机器人](https://www.okx.com/trading-bot)。

## 入门指南
### 先决条件
```python version：>=3.9```
```WebSocketAPI： websockets package advise version 6.0```
```python-okx>=0.1.9```
```autobahn~=23.1.2```
```shortuuid~=1.0.11```
```Twisted~=22.10.0```
```PyYAML~=6.0```

### 快速开始
1. 将本项目克隆到本地开发环境。点击页面右上角的Code按钮，按照说明进行git克隆。
2. 打开项目文件夹okx-sample-market-maker。通过命令```pip install -r requirements.txt```安装依赖。强烈建议使用```virtualenv```创建Python虚拟环境。
3. 在OKX账户中切换到模拟交易模式。在模拟交易模式下生成模拟交易API密钥。有关OKX模拟交易环境的介绍，请参考[如何在OKX上练习加密货币交易](https://www.okx.com/learn/how-to-practice-trading-crypto-on-okx-with-demo-trading)。
4. 将API密钥凭证放入```okx_market_market/settings.py```中的```API_KEY```、```API_SECRET_KEY```和```API_SECRET_KEY```部分。建议将```IS_PAPER_TRADING```设置为True。
5. ```okx_market_market/settings.py```中的```TRADING_INSTRUMENT_ID```默认设置为*BTC-USDT-SWAP*，```TRADING_MODE```为*cross*。如果想交易其他标的，可以随意更改此字段。要获取有效的交易标的ID，请参考[OKX公共API](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-instruments)。OKX的一些有效InstId示例：```BTC-USDT / BTC-USDT-SWAP / BTC-USDT-230630 / BTC-USD-230623-22000-C```。关于交易模式（cash/isolated/cross）的选择，请参考下面的“交易标的与交易模式”部分。
6. ```okx_market_market/params.yaml```存储了一组可在策略运行时动态加载的策略参数。在点击运行按钮之前，请务必检查这些参数。有些参数如```single_size_as_multiple_of_lot_size```与交易标的相关，需要用户自行判断。
7. 点击运行按钮！从IDE或命令行运行主脚本```okx_market_maker/run_sample_market_maker.py```来启动示例做市商。在命令行中，只需运行```python3 -m okx_market_maker.run_sample_market_maker```。


### 交易标的与交易模式
```Trade Mode, when placing an order, you need to specify the trade mode.
Non-margined:
- SPOT and OPTION buyer: cash
Single-currency margin account:
- Isolated MARGIN: isolated
- Cross MARGIN: cross
- SPOT: cash
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
Multi-currency margin account:
- Isolated MARGIN: isolated
- Cross SPOT: cross
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
Portfolio margin:
- Isolated MARGIN: isolated
- Cross SPOT: cross
- Cross FUTURES/SWAP/OPTION: cross
- Isolated FUTURES/SWAP/OPTION: isolated
```

### 输出
```PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26441.4
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26414.9
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26388.4
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26362.0
PLACE ORDER limit buy BTC-USDT-SWAP 2.0 @ 26335.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26494.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26521.0
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26547.5
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26573.9
PLACE ORDER limit sell BTC-USDT-SWAP 2.0 @ 26600.4
==== Risk Summary ====
Time: 2023-06-23 15:37:53
Inception: 2023-06-23 15:37:21
P&L since inception (USD): 10.89
Asset Value Change since inception (USD): -51.25
Trading Instrument: BTC-USDT-SWAP (SWAP)
Trading Instrument Exposure (BTC): -0.0060
Trading Instrument Exposure (USDT): -179.91
Net Traded Position: -6
Net Trading Volume: 18
==== End of Summary ====
AMEND ORDER orderaFZBngCqMjsxVHjDtD2TBC with new size 0 or new price 26444.7, req_id is amend9J9HQCeQbuCrRRDS4LLzpk
AMEND ORDER order7edCnqJf8LSaASr7aUF8Ep with new size 0 or new price 26418.2, req_id is amendhqggfxytoEgwZWRmGN4otE
AMEND ORDER orderSp6zyec6vk6reducoebAw8 with new size 0 or new price 26391.7, req_id is amendYnBrazuLpuzScAA4hcHkFd
AMEND ORDER order4xSjPPTyiCosUfX7M4dYcT with new size 0 or new price 26365.3, req_id is amendaYCTkuci8VSUE4WqhCSuNt
AMEND ORDER order68zeuyF56N4NH6FqKsnHbU with new size 0 or new price 26338.8, req_id is amendhupm2b54yQm92qab3oGzcw
AMEND ORDER orderL4mncCFYWPCagUEYQkxeuQ with new size 0 or new price 26497.8, req_id is amendgEYsEvmbYt6yMVHsLNXs3X
AMEND ORDER orderTFLxbR9tTPLU8kE4HXxJ5w with new size 0 or new price 26524.3, req_id is amend2AjcdkrPvbKWBSfnLr89Xx
AMEND ORDER orderVrGqNDiF2fiAj6J2Nedv4J with new size 0 or new price 26550.8, req_id is amendTPLgHMPj25vfoh3kSaqdfB
AMEND ORDER ordermFnP2ZKhhkeK8YBw4M35cT with new size 0 or new price 26577.2, req_id is amendU5HC3greWaN6HqGvfQgLNN
AMEND ORDER orderEY4tUgAFzYtqea4qTbbTdC with new size 0 or new price 26603.7, req_id is amendJsqVtyBMp6pfsrrsR79kch
...
KeyboardInterrupt

CANCELING ORDER orderaFZBngCqMjsxVHjDtD2TBC
CANCELING ORDER order7edCnqJf8LSaASr7aUF8Ep
CANCELING ORDER orderSp6zyec6vk6reducoebAw8
CANCELING ORDER order4xSjPPTyiCosUfX7M4dYcT
CANCELING ORDER order68zeuyF56N4NH6FqKsnHbU
CANCELING ORDER orderL4mncCFYWPCagUEYQkxeuQ
CANCELING ORDER orderTFLxbR9tTPLU8kE4HXxJ5w
CANCELING ORDER orderVrGqNDiF2fiAj6J2Nedv4J
CANCELING ORDER ordermFnP2ZKhhkeK8YBw4M35cT
CANCELING ORDER orderEY4tUgAFzYtqea4qTbbTdC
```

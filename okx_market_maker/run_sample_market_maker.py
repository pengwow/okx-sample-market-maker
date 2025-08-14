"""
OKX做市商项目入口文件

本程序实现了一个基于OKX交易所的量化做市策略，通过以下核心服务协同工作：
1. 市场数据服务：获取实时行情和订单簿数据
2. 订单管理服务：处理订单创建、修改和取消
3. 头寸管理服务：监控账户余额和持仓风险
4. 策略模块：实现做市逻辑，包括订单定价、风险控制和盈亏计算

做市商通过在订单簿的买卖两侧同时挂单提供流动性，赚取买卖价差。
本示例采用简单的网格做市策略，在基准价格上下设置多个挂单价位。
"""
import asyncio
import logging
from okx_market_maker.market_data_service.WssMarketDataService import WssMarketDataService
from okx_market_maker.order_management_service.WssOrderManagementService import WssOrderManagementService
from okx_market_maker.position_management_service.WssPositionManagementService import WssPositionManagementService
from okx_market_maker.strategy.SampleMM import SampleMM
from okx_market_maker.settings import API_KEY, API_KEY_SECRET, API_PASSPHRASE, IS_PAPER_TRADING


async def main():
    """
    主函数：初始化服务并启动做市策略
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    strategy = SampleMM()
    await strategy.run()
    # 异步启动各服务并等待完成
    # is_paper_trading = True
    # mds = WssMarketDataService(
    #         url="wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999" if is_paper_trading
    #         else "wss://wspap.okx.com:8443/ws/v5/public",
    #         inst_id="BTC-USDT-SWAP",
    #         channel="books"
    #     )
    # await mds.start()
    # await mds.run_service()
    # while True:
    #     await asyncio.sleep(10)



if __name__ == "__main__":
    # strategy = SampleMM()
    # strategy.run()
    asyncio.run(main())


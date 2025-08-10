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
    做市流程：
    1. 初始化日志系统
    2. 创建市场数据、订单管理和头寸管理服务实例
    3. 初始化做市策略（SampleMM）
    4. 启动所有服务连接
    5. 运行策略主循环
    6. 捕获异常并优雅关闭服务
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # 初始化做市策略实例
    # 【做市核心】SampleMM继承自BaseStrategy，实现了具体的做市逻辑
    strategy = SampleMM(
        market_data_service=market_data_service,
        order_management_service=order_management_service,
        position_management_service=position_management_service,
        instrument_id=INSTRUMENT_ID,
        logger=logger
    )
    try:
        # 启动策略主循环
        # 【关键】该循环会持续生成做市订单并根据市场变化调整
        await strategy.run()
    except Exception as e:
        logger.error(f"策略运行异常: {e}")
    finally:
        # 关闭所有服务连接
        await market_data_service.close()
        await order_management_service.close()
        await position_management_service.close()


if __name__ == "__main__":
    strategy = SampleMM()
    strategy.run()


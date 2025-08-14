import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from okx_market_maker.strategy.BaseStrategy import BaseStrategy
from okx_market_maker.settings import *
from okx_market_maker.market_data_service.WssMarketDataService import WssMarketDataService

# 创建一个具体的策略类来测试
class TestStrategy(BaseStrategy):
    def order_operation_decision(self, order_data):
        """实现抽象方法"""
        pass
    
    def on_orderbook_data(self, orderbook_data):
        """处理订单簿数据"""
        print(f"收到订单簿数据: {orderbook_data}")

async def test_websocket_connection():
    """测试WebSocket连接功能，包括代理支持"""
    print("开始测试WebSocket连接...")
    
    # 创建测试策略实例
    try:
        strategy = TestStrategy(
            api_key=API_KEY,
            api_key_secret=API_KEY_SECRET,
            api_passphrase=API_PASSPHRASE,
            is_paper_trading=IS_PAPER_TRADING,
            proxy=PROXY
        )
        print("TestStrategy实例创建成功")
        
        # 启动市场数据服务
        print("启动市场数据服务...")
        await strategy.mds.start()
        await strategy.mds.run_service()
        print("市场数据服务启动成功")
        
        # 等待几秒钟查看连接状态
        await asyncio.sleep(5)
        
        # 停止服务
        print("停止服务...")
        strategy.mds.stop_service()
        
        print("WebSocket连接测试完成")
        return True
    except Exception as e:
        print(f"WebSocket连接测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_websocket_connection())
    if result:
        print("测试通过")
    else:
        print("测试失败")
        sys.exit(1)
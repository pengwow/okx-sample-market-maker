from dataclasses import dataclass, field
from typing import Dict

from okx_market_maker.utils.OkxEnum import InstType


@dataclass
class Ticker:
    """
    加密货币交易标的行情数据类，包含最新价格、买卖盘口和交易量等关键市场指标
    
    在做市策略中，行情数据是定价决策的基础，直接影响：
    - 订单定价（基于最新买卖价格）
    - 流动性评估（基于盘口深度和交易量）
    - 市场趋势判断（基于24小时价格变化）
    
    数据主要来源于交易所WebSocket实时推送和REST API查询
    """
    inst_type: InstType  # 交易标的类型（如现货、永续合约、期权等）
    inst_id: str         # 交易标的ID（如BTC-USDT、ETH-USDT-SWAP等）
    last: float = 0      # 最新成交价
    last_sz: float = 0   # 最新成交数量
    ask_px: float = 0    # 卖一价（当前市场最低卖价）
    ask_sz: float = 0    # 卖一量（卖一价对应的挂单数量）
    bid_px: float = 0    # 买一价（当前市场最高买价）
    bid_sz: float = 0    # 买一量（买一价对应的挂单数量）
    open24h: float = 0   # 24小时开盘价
    high24h: float = 0   # 24小时最高价
    low24h: float = 0    # 24小时最低价
    vol_ccy24h: float = 0  # 24小时交易量（按计价货币计算，如USDT）
    vol24h: float = 0    # 24小时交易量（按基础货币计算，如BTC）
    sod_utc0: float = 0  # UTC时间0点开盘价
    sod_utc8: float = 0  # UTC+8时间0点开盘价（北京时间）
    ts: int = 0          # 数据时间戳（毫秒级Unix时间）

    @classmethod
    def init_from_json(cls, json_response):
        """
        从OKX交易所API的JSON响应初始化Ticker对象
        
        交易所API返回的行情数据格式示例：
        {
            "instType":"SWAP",
            "instId":"LTC-USD-SWAP",
            "last":"9999.99",
            "lastSz":"0.1",
            "askPx":"9999.99",
            "askSz":"11",
            "bidPx":"8888.88",
            "bidSz":"5",
            "open24h":"9000",
            "high24h":"10000",
            "low24h":"8888.88",
            "volCcy24h":"2222",
            "vol24h":"2222",
            "sodUtc0":"0.1",
            "sodUtc8":"0.1",
            "ts":"1597026383085"
        }
        
        :param json_response: 交易所返回的行情JSON数据
        :return: 初始化完成的Ticker对象
        :raises KeyError: 如果JSON中缺少必要字段
        """
        # 解析交易类型和标的ID（必须字段）
        inst_type = InstType(json_response["instType"])
        inst_id = json_response["instId"]
        ticker = Ticker(inst_type, inst_id)

        # 解析可选价格字段，处理可能的缺失值
        ticker.last = float(json_response["last"]) if json_response.get("last") else 0
        ticker.last_sz = float(json_response["lastSz"]) if json_response.get("lastSz") else 0
        ticker.ask_px = float(json_response["askPx"]) if json_response.get("askPx") else 0
        ticker.ask_sz = float(json_response["askSz"]) if json_response.get("askSz") else 0
        ticker.bid_px = float(json_response["bidPx"]) if json_response.get("bidPx") else 0
        ticker.bid_sz = float(json_response["bidSz"]) if json_response.get("bidSz") else 0
        ticker.open24h = float(json_response["open24h"]) if json_response.get("open24h") else 0
        ticker.high24h = float(json_response["high24h"]) if json_response.get("high24h") else 0
        ticker.low24h = float(json_response["low24h"]) if json_response.get("low24h") else 0

        # 解析交易量数据
        ticker.vol_ccy24h = float(json_response["volCcy24h"]) if json_response.get("volCcy24h") else 0
        ticker.vol24h = float(json_response["vol24h"]) if json_response.get("vol24h") else 0

        # 解析开盘价数据（不同时区）
        ticker.sod_utc0 = float(json_response["sodUtc0"]) if json_response.get("sodUtc0") else 0
        ticker.sod_utc8 = float(json_response["sodUtc8"]) if json_response.get("sodUtc8") else 0

        # 解析时间戳
        ticker.ts = int(json_response["ts"]) if json_response.get("ts") else 0

        return ticker

    def update_from_json(self, json_response):
        """
        从JSON响应更新现有Ticker对象的数据
        
        与init_from_json的区别：
        - init_from_json：创建新Ticker对象
        - update_from_json：更新已有Ticker对象的字段值
        
        用于WebSocket推送的增量更新，避免频繁创建新对象
        
        :param json_response: 交易所返回的行情JSON数据
        """
        self.last = float(json_response["last"]) if json_response.get("last") else 0
        self.last_sz = float(json_response["lastSz"]) if json_response.get("lastSz") else 0
        self.ask_px = float(json_response["askPx"]) if json_response.get("askPx") else 0
        self.ask_sz = float(json_response["askSz"]) if json_response.get("askSz") else 0
        self.bid_px = float(json_response["bidPx"]) if json_response.get("bidPx") else 0
        self.bid_sz = float(json_response["bidSz"]) if json_response.get("bidSz") else 0
        self.open24h = float(json_response["open24h"]) if json_response.get("open24h") else 0
        self.high24h = float(json_response["high24h"]) if json_response.get("high24h") else 0
        self.low24h = float(json_response["low24h"]) if json_response.get("low24h") else 0
        self.vol_ccy24h = float(json_response["volCcy24h"]) if json_response.get("volCcy24h") else 0
        self.vol24h = float(json_response["vol24h"]) if json_response.get("vol24h") else 0
        self.sod_utc0 = float(json_response["sodUtc0"]) if json_response.get("sodUtc0") else 0
        self.sod_utc8 = float(json_response["sodUtc8"]) if json_response.get("sodUtc8") else 0
        self.ts = int(json_response["ts"]) if json_response.get("ts") else 0


@dataclass
class Tickers:
    """
    管理多个交易标的行情数据的容器类
    
    内部使用字典存储不同交易标的（inst_id）对应的Ticker对象，
    提供从API响应更新数据和查询特定标的行情的功能
    
    在做市系统中，通常会同时订阅多个交易对的行情数据，
    此类用于集中管理这些数据，支持快速查询和更新
    """
    # 存储inst_id到Ticker对象的映射
    _ticker_map: Dict[str, Ticker] = field(default_factory=lambda: dict())

    def update_from_json(self, json_response):
        """
        从OKX API的JSON响应批量更新多个交易标的的行情数据
        
        API响应格式示例：
        {
            "code": "0",  # 0表示成功
            "data": [
                {"instId": "BTC-USDT", ...},  # 第一个交易对数据
                {"instId": "ETH-USDT", ...}   # 第二个交易对数据
            ]
        }
        
        :param json_response: 包含多个交易对行情的JSON响应
        :raises ValueError: 如果API响应返回错误状态码
        """
        # 检查API响应状态
        if json_response.get("code") != '0':
            raise ValueError(f"行情数据获取失败: {json_response}")

        # 处理每个交易标的的数据
        data = json_response["data"]
        for info in data:
            inst_id = info["instId"]
            
            # 如果是新标的，创建Ticker对象；否则更新现有对象
            if inst_id not in self._ticker_map:
                self._ticker_map[inst_id] = Ticker.init_from_json(info)
            else:
                self._ticker_map[inst_id].update_from_json(info)

    def get_ticker_by_inst_id(self, inst_id: str) -> Ticker:
        """
        根据交易标的ID获取对应的Ticker对象
        
        在做市策略中的应用场景：
        1. 获取特定交易对的最新价格用于订单定价
        2. 查询盘口深度评估市场流动性
        3. 分析交易量判断市场活跃度
        
        :param inst_id: 交易标的ID（如BTC-USDT）
        :return: 对应的Ticker对象，若不存在则返回None
        """
        return self._ticker_map.get(inst_id)

    def get_usdt_price_by_ccy(self, ccy: str, use_mid: bool = True) -> float:
        """
        获取指定币种的USDT价格，支持直接和间接定价
        
        在加密货币市场中，并非所有币种都有直接的USDT交易对，
        因此需要通过中间币种进行换算（如通过BTC或ETH）
        
        定价优先级：
        1. 直接USDT交易对（如BTC-USDT）
        2. 间接交易对（如XRP-BTC + BTC-USDT）
        
        :param ccy: 要查询的币种（如BTC、ETH、XRP等）
        :param use_mid: 是否使用中间价（(买一价+卖一价)/2）
                        False则使用最新成交价
        :return: 该币种的USDT价格，若无法获取则返回0
        """
        # USDT本身价格为1
        if ccy == "USDT":
            return 1

        # 1. 尝试直接USDT交易对（如BTC-USDT）
        if f"{ccy}-USDT" in self._ticker_map:
            ticker = self.get_ticker_by_inst_id(f"{ccy}-USDT")
            # 使用中间价或最新成交价
            return ((ticker.ask_px + ticker.bid_px) / 2) if use_mid else ticker.last

        # 2. 尝试通过中间币种间接定价
        # 常用中间币种列表（按流动性排序）
        for quote in ["USDC", "BTC", "ETH", "DAI", "OKB", "DOT", "EURT"]:
            # 检查是否存在ccy-quote和quote-USDT交易对
            if f"{ccy}-{quote}" in self._ticker_map and f"{quote}-USDT" in self._ticker_map:
                # 获取ccy对quote的价格
                ticker = self.get_ticker_by_inst_id(f"{ccy}-{quote}")
                # 获取quote对USDT的价格
                quote_ticker = self.get_ticker_by_inst_id(f"{quote}-USDT")
                
                # 计算中间价或使用最新成交价
				#return (((ticker.ask_px + ticker.bid_px) / 2) * ((quote_ticker.ask_px + quote_ticker.bid_px) / 2)) \
                #    if use_mid else (ticker.last * quote_ticker.last)
                if use_mid:
                    ccy_quote_mid = (ticker.ask_px + ticker.bid_px) / 2
                    quote_usdt_mid = (quote_ticker.ask_px + quote_ticker.bid_px) / 2
                    return ccy_quote_mid * quote_usdt_mid
                else:
                    return ticker.last * quote_ticker.last

        # 3. 无法获取价格时返回0
        return 0

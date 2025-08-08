import math
import time
from decimal import Decimal
from typing import Tuple, List

from okx_market_maker.market_data_service.model.Instrument import Instrument
from okx_market_maker.market_data_service.model.OrderBook import OrderBook
from okx_market_maker.order_management_service.model.OrderRequest import PlaceOrderRequest, AmendOrderRequest, \
    CancelOrderRequest
from okx_market_maker.strategy.BaseStrategy import BaseStrategy, StrategyOrder, TRADING_INSTRUMENT_ID
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.utils.OkxEnum import TdMode, OrderSide, OrderType, PosSide, InstType
from okx_market_maker.utils.WsOrderUtil import get_request_uuid


class SampleMM(BaseStrategy):
    """
    示例网格做市策略实现，继承自BaseStrategy抽象基类
    
    这是一个完整的加密货币做市策略实现，采用经典的网格做市算法：
    1. 在当前买卖一档价格基础上，按固定百分比间隔（step_pct）生成多个价格层级
    2. 在每个价格层级挂单，形成买卖报价网格
    3. 根据净持仓情况动态调整买卖订单数量，控制风险敞口
    4. 定期更新订单，保持网格结构与市场同步
    
    适合初学者理解做市策略的核心组件：
    - 订单定价机制
    - 风险敞口控制
    - 订单生命周期管理
    - 市场适应性调整
    """
    def __init__(self):
        super().__init__()

    def order_operation_decision(self) -> \
            Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]:
        """
        实现网格做市核心决策逻辑，生成做市订单方案
        
        这是做市策略的核心方法，负责：
        1. 从订单簿获取最新市场价格
        2. 计算网格价格层级和订单数量
        3. 根据当前净持仓动态调整买卖订单密度
        4. 生成最终的订单操作方案（下单、改单、撤单）
        
        网格做市原理图解：
        [卖单] <-- 价格升高 -- 最佳卖价 -- 价格升高 --> [卖单]
                          |
                          | (当前市场价格)
                          |
        [买单] <-- 价格降低 -- 最佳买价 -- 价格降低 --> [买单]
        
        :return: 包含三类订单请求的元组：
                 - 新下单请求列表
                 - 修改订单请求列表
                 - 取消订单请求列表
        :raises ValueError: 如果订单簿为空或无法获取有效价格
        """
        # 获取当前订单簿数据，这是做市定价的基础
        order_book: OrderBook = self.get_order_book()
        # 获取最佳买卖价格（第一档）
        bid_level = order_book.bid_by_level(1)
        ask_level = order_book.ask_by_level(1)

        # 订单簿数据验证
        if not bid_level and not ask_level:
            raise ValueError("订单簿为空，无法获取市场价格！")
        # 处理单边市场情况（极端行情下可能出现）
        if bid_level and not ask_level:
            ask_level = order_book.bid_by_level(1)  # 用买一价作为卖价参考
        if ask_level and not bid_level:
            bid_level = order_book.ask_by_level(1)  # 用卖一价作为买价参考

        # 获取交易标的信息（包含最小下单量、合约乘数等关键参数）
        instrument = InstrumentUtil.get_instrument(TRADING_INSTRUMENT_ID, self.trading_instrument_type)

        # 从配置加载核心做市参数
        step_pct = self.params_loader.get_strategy_params("step_pct")  # 网格步长百分比（如0.001表示0.1%）
        num_of_order_each_side = self.params_loader.get_strategy_params("num_of_order_each_side")  # 每边初始订单数量

        # 计算单笔订单大小（确保不小于最小下单量，且为合约乘数的整数倍）
        single_order_size = max(
            self.params_loader.get_strategy_params("single_size_as_multiple_of_lot_size") * instrument.lot_sz,
            instrument.min_sz)

        # 获取策略绩效数据，用于风险控制
        strategy_measurement = self.get_strategy_measurement()

        # 初始化每边订单数量
        buy_num_of_order_each_side = num_of_order_each_side
        sell_num_of_order_each_side = num_of_order_each_side

        # 获取风险控制参数（最大净持仓限制）
        max_net_buy = self.params_loader.get_strategy_params("maximum_net_buy")  # 最大净买入量
        max_net_sell = self.params_loader.get_strategy_params("maximum_net_sell")  # 最大净卖出量

        # 根据当前净持仓动态调整订单数量，实现风险敞口控制
        if strategy_measurement.net_filled_qty > 0:
            # 净买入过多时，减少买单数量（避免进一步增加多头敞口）
            buy_num_of_order_each_side *= max(1 - strategy_measurement.net_filled_qty / max_net_buy, 0)
            buy_num_of_order_each_side = math.ceil(buy_num_of_order_each_side)  # 向上取整确保至少有1个订单
        if strategy_measurement.net_filled_qty < 0:
            # 净卖出过多时，减少卖单数量（避免进一步增加空头敞口）
            sell_num_of_order_each_side *= max(1 + strategy_measurement.net_filled_qty / max_net_sell, 0)
            sell_num_of_order_each_side = math.ceil(sell_num_of_order_each_side)

        # 生成买单价格层级（从最佳买价向下按步长百分比递减）
        proposed_buy_orders = [(bid_level.price * (1 - step_pct * (i + 1)), single_order_size)
                               for i in range(buy_num_of_order_each_side)]
        # 生成卖单价格层级（从最佳卖价向上按步长百分比递增）
        proposed_sell_orders = [(ask_level.price * (1 + step_pct * (i + 1)), single_order_size)
                                for i in range(sell_num_of_order_each_side)]

        # 价格和数量格式化（确保符合交易所精度要求）
        proposed_buy_orders = [(InstrumentUtil.price_trim_by_tick_sz(price_qty[0], OrderSide.BUY, instrument),
                                InstrumentUtil.quantity_trim_by_lot_sz(price_qty[1], instrument))
                               for price_qty in proposed_buy_orders]
        proposed_sell_orders = [(InstrumentUtil.price_trim_by_tick_sz(price_qty[0], OrderSide.SELL, instrument),
                                 InstrumentUtil.quantity_trim_by_lot_sz(price_qty[1], instrument))
                                for price_qty in proposed_sell_orders]

        # 获取当前策略订单（用于与新订单方案比较）
        current_buy_orders = self.get_bid_strategy_orders()
        current_sell_orders = self.get_ask_strategy_orders()

        # 分别计算买单和卖单的操作方案
        buy_to_place, buy_to_amend, buy_to_cancel = self.get_req(
            proposed_buy_orders, current_buy_orders, OrderSide.BUY, instrument)
        sell_to_place, sell_to_amend, sell_to_cancel = self.get_req(
            proposed_sell_orders, current_sell_orders, OrderSide.SELL, instrument)

        # 合并并返回所有订单操作请求
        return buy_to_place + sell_to_place, buy_to_amend + sell_to_amend, buy_to_cancel + sell_to_cancel

    def get_req(self, propose_orders: List[Tuple[str, str]],
                current_orders: List[StrategyOrder], side: OrderSide, instrument: Instrument) -> \
            Tuple[List[PlaceOrderRequest], List[AmendOrderRequest], List[CancelOrderRequest]]:
        """
        比较建议订单与当前订单，生成订单操作决策（下单/改单/撤单）
        
        这是订单管理的核心逻辑，实现了做市策略的"状态同步"功能：
        1. 保留价格和数量匹配的现有订单
        2. 新增建议订单中存在但当前订单中没有的订单
        3. 修改价格或数量不匹配的现有订单
        4. 取消建议订单中不存在的多余订单
        
        订单匹配算法流程：
        - 第一阶段：匹配并保留完全一致的订单
        - 第二阶段：处理新增、修改和取消操作
          * 若建议订单数量 > 当前订单数量：新增多余的建议订单
          * 若当前订单数量 > 建议订单数量：取消多余的当前订单
          * 若数量相等：修改不匹配的订单（价格或数量）
        
        :param propose_orders: 建议订单列表，每个元素为(价格, 数量)元组
        :param current_orders: 当前订单列表，包含策略现有订单
        :param side: 订单方向（买/卖）
        :param instrument: 交易标的信息
        :return: 包含三类订单请求的元组：
                 - 新下单请求列表
                 - 修改订单请求列表
                 - 取消订单请求列表
        """
        to_place: List[PlaceOrderRequest] = []  # 待新增订单
        to_amend: List[AmendOrderRequest] = []  # 待修改订单
        to_cancel: List[CancelOrderRequest] = []  # 待取消订单

        # 第一阶段：匹配并保留完全一致的订单
        for strategy_order in current_orders.copy():
            # 计算当前订单的剩余数量（原始数量 - 已成交数量）
            remaining_size = float(strategy_order.size) - float(strategy_order.filled_size)
            remaining_size = InstrumentUtil.quantity_trim_by_lot_sz(remaining_size, instrument)

            # 检查是否与建议订单中的某个(价格, 数量)对完全匹配
            if (strategy_order.price, remaining_size) in propose_orders:
                # 保留匹配的订单，从待处理列表中移除
                current_orders.remove(strategy_order)
                propose_orders.remove((strategy_order.price, remaining_size))

        # 第二阶段：处理新增、修改和取消操作
        for i in range(max(len(propose_orders), len(current_orders))):
            # 情况1：建议订单数量 > 当前订单数量 → 需要新增订单
            if i + 1 > len(current_orders):
                price, size = propose_orders[i]
                # 创建新订单请求
                order_req = PlaceOrderRequest(
                    inst_id=instrument.inst_id,  # 交易标的ID
                    td_mode=self.decide_td_mode(instrument),  # 交易模式（由父类方法决定）
                    side=side,  # 订单方向
                    ord_type=OrderType.LIMIT,  # 订单类型（限价单）
                    size=size,  # 订单数量
                    price=price,  # 订单价格
                    client_order_id=get_request_uuid("order"),  # 客户端订单ID（用于追踪）
                    pos_side=PosSide.net,  # 持仓方向（净额模式）
                    # 保证金币种（仅适用于保证金交易）
                    ccy=(instrument.base_ccy if side == OrderSide.BUY else instrument.quote_ccy)
                    if instrument.inst_type == InstType.MARGIN else ""
                )
                to_place.append(order_req)
                continue

            # 情况2：当前订单数量 > 建议订单数量 → 需要取消多余订单
            if i + 1 > len(propose_orders):
                strategy_order = current_orders[i]
                # 创建取消订单请求
                cancel_req = CancelOrderRequest(
                    inst_id=strategy_order.inst_id,
                    client_order_id=strategy_order.client_order_id
                )
                to_cancel.append(cancel_req)
                continue

            # 情况3：数量相等但价格或数量不匹配 → 需要修改订单
            strategy_order = current_orders[i]
            new_price, new_size = propose_orders[i]
            # 计算当前订单的剩余数量
            remaining_size = (Decimal(strategy_order.size) - Decimal(strategy_order.filled_size)).to_eng_string()
            cid = strategy_order.client_order_id

            # 创建修改订单请求
            amend_req = AmendOrderRequest(
                strategy_order.inst_id, 
                client_order_id=cid,
                req_id=get_request_uuid("amend")  # 修改请求ID
            )

            # 仅在价格变化时更新价格
            if new_price != strategy_order.price:
                amend_req.new_price = new_price
            # 仅在数量变化时更新数量（注意：新数量是剩余未成交部分的目标数量）
            if new_size != remaining_size:
                amend_req.new_size = (Decimal(strategy_order.filled_size) + Decimal(new_size)).to_eng_string()

            to_amend.append(amend_req)

        # 返回订单操作决策结果
        return to_place, to_amend, to_cancel

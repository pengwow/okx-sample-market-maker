import datetime
from dataclasses import dataclass
from decimal import Decimal

from okx_market_maker.market_data_service.model.Tickers import Tickers
from okx_market_maker.strategy.risk.RiskSnapshot import RiskSnapShot, AssetValueInst
from okx_market_maker.utils.InstrumentUtil import InstrumentUtil
from okx_market_maker.utils.OkxEnum import InstType, CtType
from okx_market_maker import tickers_container, mark_px_container, order_books


@dataclass
class StrategyMeasurement:
    trading_instrument: str = ""
    trading_instrument_type: InstType = None
    net_filled_qty: Decimal = 0
    buy_filled_qty: Decimal = 0
    sell_filled_qty: Decimal = 0
    trading_volume: Decimal = 0

    asset_value_change_in_usd_since_running: float = 0
    pnl_in_usd_since_running: float = 0
    trading_instrument_exposure_in_base: float = 0
    trading_instrument_exposure_in_quote: float = 0
    trading_inst_exposure_ccy: str = ""
    trading_inst_quote_ccy: str = ""
    _current_risk_snapshot: RiskSnapShot = None
    _inception_risk_snapshot: RiskSnapShot = None

    def calc_pnl(self):
        """
        此盈亏计算基于当前和初始时刻的风险快照，比较现金和工具头寸。例如：

        示例1：
        初始：现金中有{'BTC': 1, 'USDT': 30000}，无衍生品头寸。
        当前：现金中有{'BTC': 1.5, 'USDT': 15000}，无衍生品头寸。这可以看作是以30000价格额外买入0.5 BTC现货。当前BTC-USDT价格为36000。
        由于以30000价格额外买入0.5 BTC，这笔交易将产生0.5 * (36000 - 30000) = 3000 USDT，因此当前盈亏为3000 USDT。

        示例2：
        初始：现金中有{'BTC': 1, 'USDT': 30000}，同时持有1 BTC的BTC-USDT-SWAP多单，平均价格30000，标记价格31000，未实现盈亏1000 USDT。
        当前：现金中有{'BTC': 1, 'USDT': 30000}，同时持有2 BTC的BTC-USDT-SWAP多单，平均价格28000，标记价格29000，未实现盈亏2000 USDT。这可以看作是以26000价格额外买入1 BTC合约。
        假设初始头寸持有至当前，其未实现盈亏将变为1 * (29000 - 30000) = -1000，因此自初始以来的盈亏为(2000 - (-1000)) = 3000。这也来自于以26000买入的1 BTC产生的收益(1 * (29000 - 26000))。

        本计算不考虑合约到期的情况。
        :return: 以USDT计价的盈亏
        """
        pnl = 0
        delta_map = {}
        mark_px_cache = mark_px_container[0]
        usdt_to_usd_rate = mark_px_cache.get_usdt_to_usd_rate()
        for ccy in self._current_risk_snapshot.asset_cash_snapshot:
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] += self._current_risk_snapshot.asset_cash_snapshot[ccy]
        for key in self._current_risk_snapshot.asset_instrument_value_snapshot:
            ccy = key.split(":")[-1]
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] += self._current_risk_snapshot.asset_instrument_value_snapshot[key].asset_value
            # print(f"{key} asset value {self._current_risk_snapshot.asset_instrument_value_snapshot[key].asset_value}")
        for ccy in self._inception_risk_snapshot.asset_cash_snapshot:
            if ccy not in delta_map:
                delta_map[ccy] = 0
            delta_map[ccy] -= self._inception_risk_snapshot.asset_cash_snapshot[ccy]
        for key in self._inception_risk_snapshot.asset_instrument_value_snapshot:
            ccy = key.split(":")[-1]
            if ccy not in delta_map:
                delta_map[ccy] = 0
            asset_value_inst = self._inception_risk_snapshot.asset_instrument_value_snapshot[key]
            inst_id = asset_value_inst.instrument.inst_id
            # delta_map[ccy] -= self._inception_risk_snapshot.asset_instrument_value_snapshot[key]
            current_mark_px = self._current_risk_snapshot.mark_px_instrument_snapshot[inst_id] \
                if self._current_risk_snapshot.mark_px_instrument_snapshot.get(inst_id) \
                else InstrumentUtil.get_instrument_mark_px(inst_id)
            if not current_mark_px:
                raise ValueError(f"No current mark px is available for {inst_id}, consider the instrument is retired. "
                                 f"Pls restart the program.")
            assumed_asset_value = self.calc_assumed_asset_value(asset_value_inst, current_mark_px)
            if not assumed_asset_value:
                assumed_asset_value = asset_value_inst.asset_value
            # print(f"{key} assumed asset value {assumed_asset_value}")
            delta_map[ccy] -= assumed_asset_value
        for ccy in delta_map:
            price = self._current_risk_snapshot.price_to_usd_snapshot.get(ccy)
            if not price:
                tickers: Tickers = tickers_container[0]
                price = tickers.get_usdt_price_by_ccy(ccy) * usdt_to_usd_rate
            pnl += price * delta_map[ccy]
        return pnl

    @staticmethod
    def calc_assumed_asset_value(asset_value_inst: AssetValueInst, current_mark_px: float) -> float:
        instrument = asset_value_inst.instrument
        if instrument.inst_type in [InstType.MARGIN]:
            """
            For Margin P&L calculation, please refer to this page:
            https://www.okx.com/help-center/6997022292493 
            """
            if asset_value_inst.pos_ccy == instrument.base_ccy and asset_value_inst.pos_ccy == asset_value_inst.ccy:
                return asset_value_inst.pos + asset_value_inst.liability / current_mark_px
            if asset_value_inst.pos_ccy == instrument.quote_ccy and asset_value_inst.pos_ccy == asset_value_inst.ccy:
                return asset_value_inst.pos + asset_value_inst.liability * current_mark_px
            if asset_value_inst.pos_ccy == instrument.base_ccy and asset_value_inst.pos_ccy != asset_value_inst.ccy:
                return asset_value_inst.pos * current_mark_px + asset_value_inst.liability
            if asset_value_inst.pos_ccy == instrument.quote_ccy and asset_value_inst.pos_ccy != asset_value_inst.ccy:
                return asset_value_inst.pos / current_mark_px + asset_value_inst.liability
        if instrument.inst_type in [InstType.SWAP, InstType.FUTURES]:
            if instrument.ct_type == CtType.LINEAR:
                return asset_value_inst.pos * instrument.ct_mul * instrument.ct_val \
                       * (current_mark_px - asset_value_inst.avg_px) + asset_value_inst.margin
            if instrument.ct_type == CtType.INVERSE:
                return asset_value_inst.pos * instrument.ct_mul * instrument.ct_val \
                       * (1 / asset_value_inst.avg_px - 1 / current_mark_px) + asset_value_inst.margin
        if instrument.inst_type in [InstType.OPTION]:
            return asset_value_inst.pos * instrument.ct_mul * instrument.ct_val \
                   * current_mark_px + asset_value_inst.margin
        return 0.0

    def consume_risk_snapshot(self, risk_snapshot: RiskSnapShot):
        if self._inception_risk_snapshot is None:
            self._inception_risk_snapshot = risk_snapshot
            return
        self._current_risk_snapshot = risk_snapshot
        self.asset_value_change_in_usd_since_running = \
            self._current_risk_snapshot.asset_usd_value - self._inception_risk_snapshot.asset_usd_value
        self.pnl_in_usd_since_running = self.calc_pnl()
        instrument = InstrumentUtil.get_instrument(self.trading_instrument, self.trading_instrument_type)
        exposure_ccy = InstrumentUtil.get_asset_exposure_ccy(instrument)
        quote_ccy = InstrumentUtil.get_asset_quote_ccy(instrument)
        self.trading_inst_exposure_ccy = exposure_ccy
        self.trading_inst_quote_ccy = quote_ccy
        price = self._current_risk_snapshot.price_to_usd_snapshot.get(exposure_ccy)
        quote_price = self._current_risk_snapshot.price_to_usd_snapshot.get(quote_ccy)
        if instrument.inst_type == InstType.SPOT:
            current_cash = self._current_risk_snapshot.asset_cash_snapshot.get(exposure_ccy)
            init_cash = self._inception_risk_snapshot.asset_cash_snapshot.get(exposure_ccy)
            self.trading_instrument_exposure_in_base = current_cash - init_cash
            self.trading_instrument_exposure_in_quote = (current_cash - init_cash) * price / quote_price
        if instrument.inst_type in [InstType.SWAP, InstType.FUTURES, InstType.OPTION, InstType.MARGIN]:
            delta = 0
            for key, value in self._current_risk_snapshot.delta_instrument_snapshot.items():
                if self.trading_instrument in key:
                    delta += value
            init_delta = 0
            for key, value in self._inception_risk_snapshot.delta_instrument_snapshot.items():
                if self.trading_instrument in key:
                    init_delta += value
            self.trading_instrument_exposure_in_base = delta - init_delta
            self.trading_instrument_exposure_in_quote = (delta - init_delta) * price / quote_price
        self.print_risk_summary()

    def print_risk_summary(self):
        curr_time_string = datetime.datetime.fromtimestamp(
            self._current_risk_snapshot.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        init_time_string = datetime.datetime.fromtimestamp(
            self._inception_risk_snapshot.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        print(f"==== Risk Summary ====\n"
              f"Time: {curr_time_string}\n"
              f"Inception: {init_time_string}\n"
              f"P&L since inception (USD): {self.pnl_in_usd_since_running:.2f}\n"
              f"Asset Value Change since inception (USD): {self.asset_value_change_in_usd_since_running:.2f}\n"
              f"Trading Instrument: {self.trading_instrument} ({self.trading_instrument_type.value})\n"
              f"Trading Instrument Exposure ({self.trading_inst_exposure_ccy}): "
              f"{self.trading_instrument_exposure_in_base:.4f}\n"
              f"Trading Instrument Exposure ({self.trading_inst_quote_ccy}): "
              f"{self.trading_instrument_exposure_in_quote:.2f}\nNet Traded Position: {self.net_filled_qty}\n"
              f"Net Trading Volume: {self.trading_volume}\n==== End of Summary ====")

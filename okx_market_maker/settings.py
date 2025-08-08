import os

# API密钥凭证
API_KEY = ""
API_KEY_SECRET = ""
API_PASSPHRASE = ""
IS_PAPER_TRADING = True

# 做市交易标的
TRADING_INSTRUMENT_ID = "BTC-USDT-SWAP"
TRADING_MODE = "cross"  # "cash" / "isolated" / "cross"

# 默认延迟容忍时间
ORDER_BOOK_DELAYED_SEC = 60  # 如果订单簿超过此秒数未更新则警告，可能是WSS连接问题
ACCOUNT_DELAYED_SEC = 60  # 如果账户信息超过此秒数未更新则警告，可能是WSS连接问题

# 无风险货币
RISK_FREE_CCY_LIST = ["USDT", "USDC", "DAI"]

# 参数配置文件路径
PARAMS_PATH = os.path.abspath(os.path.dirname(__file__) + "/params.yaml")

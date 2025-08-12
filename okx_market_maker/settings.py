import os

# API密钥凭证
API_KEY = "7361a754-6fcf-4d8c-a81e-82abe6419911"
API_KEY_SECRET = "D44AF42935AF27262DDFE4DDE3B63103"
API_PASSPHRASE = "lwobqobj6L.."
IS_PAPER_TRADING = True
PROXY = "http://127.0.0.1:7890"

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

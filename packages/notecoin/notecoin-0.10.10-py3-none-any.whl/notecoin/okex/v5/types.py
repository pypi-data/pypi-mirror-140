
from enum import Enum


class BillType(Enum):
    # 划转
    TRANSFER = 1
    # 交易
    TRADE = 2
    # 交割
    DELIVERY = 3
    # 强制换币
    FORCE_SWAP = 4
    # 强平
    FORCED_LIQUIDATION = 5
    # ...


class BillSubType(Enum):
    LINEAR = "linear"
    INVERSE = "inverse"
    # ...


class CcyType(Enum):
    BTC = "BTC"
    ETH = "ETH"
    LTC = "LTC"
    ADA = "ADA"
    TRX = "TRX"
    OKB = "OKB"
    UNI = "UNI"
    # ...


class CtType(Enum):
    LINEAR = "linear"
    INVERSE = "inverse"


class InstType(Enum):
    MARGIN = "MARGIN"
    SPOT = "SPOT"
    SWAP = "SWAP"
    FUTURES = "FUTURES"
    OPTION = "OPTION"


# 仓位类型
class MgnMode(Enum):
    # 保证金模式
    ISOLATED = "isolated"
    CROSS = "cross"
    # 非保证金模式
    CASH = "cash"


class TdMode(Enum):
    # 保证金模式
    ISOLATED = "isolated"
    CROSS = "cross"
    # 非保证金模式
    CASH = "cash"


class PosSide(Enum):
    LONG = "long"
    SHORT = "short"


class OrderType(Enum):
    # 市价单
    MARKET = "market"
    # 限价单
    LIMIT = "limit"
    # 只做maker单
    POST_ONLY = "post_only"
    # 全部成交或立即取消
    FOK = "fok"
    # 立即成交并取消剩余
    IOC = "ioc"


class TrgCCY(Enum):
    # 交易货币
    BASE_CCY = "base_ccy"
    # 计价货币
    QUOTE_CCY = "quote_ccy"

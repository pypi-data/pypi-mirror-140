
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

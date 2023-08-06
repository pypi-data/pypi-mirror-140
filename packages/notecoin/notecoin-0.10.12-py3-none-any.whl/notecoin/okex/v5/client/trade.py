from typing import Dict, Iterable, Optional, Union

from notecoin.okex.v5.client.base import BaseClient
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.types import *
from notecoin.okex.v5.utils import enum_to_str


class Order(object):
    def __init__(self, inst_id: str, td_mode: Union[TdMode, str], ord_type: Union[OrderType, str],
                 sz: Union[float, int, str], ccy: Optional[Union[CcyType, str]] = None,
                 cl_ord_id: Optional[str] = None, tag: Optional[str] = None,
                 pos_side: Optional[Union[PosSide, str]] = None,
                 reduce_only: Optional[Union[str, bool]] = None,
                 tgt_ccy: Optional[Union[TrgCCY, str]] = None) -> None:
        super(Order, self).__init__()
        self.instId = inst_id
        self.tdMode = td_mode
        self.ordType = ord_type
        self.sz = sz
        self.ccy = ccy
        self.clOrdId = cl_ord_id
        self.tag = tag
        self.posSide = pos_side
        self.reduceOnly = reduce_only
        self.tgtCcy = tgt_ccy


class CancelOrder(object):
    def __init__(self, inst_id: str, ord_id: Optional[str] = None, cl_ord_id: Optional[str] = None) -> None:
        super(CancelOrder, self).__init__()
        self.instId = inst_id
        self.ordId = ord_id
        self.clOrdId = cl_ord_id


class TradeAPI(BaseClient):

    def __init__(self, *args, **kwargs):
        super(TradeAPI, self).__init__(*args, **kwargs)

    def order(self, inst_id: str,
              td_mode: Union[TdMode, str],
              ord_type: Union[OrderType, str],
              sz: Union[float, int, str],
              ccy: Optional[Union[CcyType, str]] = None,
              cl_ord_id: Optional[str] = None,
              tag: Optional[str] = None,
              pos_side: Optional[Union[PosSide, str]] = None,
              px: Optional[Union[float, int, str]] = None,
              reduce_only: Optional[Union[str, bool]] = None
              ) -> Dict:
        params = {}
        if inst_id is not None:
            params['instId'] = str(inst_id)
        if td_mode is not None:
            params['tdMode'] = enum_to_str(td_mode)
        if ord_type is not None:
            params['ordType'] = enum_to_str(ord_type)
        if sz is not None:
            params['sz'] = str(abs(sz))
            if sz >= 0:
                params['side'] = 'buy'
            else:
                params['side'] = 'sell'
        if ccy is not None:
            params['ccy'] = enum_to_str(ccy)
        if cl_ord_id is not None:
            params['clOrdId'] = str(cl_ord_id)
        if tag is not None:
            params['tag'] = str(tag)
        if pos_side is not None:
            params['posSide'] = enum_to_str(pos_side)
        if px is not None:
            params['px'] = str(px)
        if reduce_only is not None:
            if isinstance(reduce_only, bool):
                if reduce_only:
                    params['reduceOnly'] = 'true'
                else:
                    params['reduceOnly'] = 'false'
            else:
                params['reduceOnly'] = str(reduce_only)
        data = self._request_with_params(POST, ORDER, params)["data"]

        return data

    def batch_orders(self, orders: Union[Order, Iterable[Order]]) -> Dict:
        orders_list = []
        if isinstance(orders, Order):
            orders_list.append(orders)
        else:
            orders_list = orders
        params = []

        for order in orders_list:
            param = {}
            if order.instId is not None:
                param['instId'] = str(order.instId)
            if order.tdMode is not None:
                param['tdMode'] = enum_to_str(order.tdMode)
            if order.ordType is not None:
                param['ordType'] = enum_to_str(order.ordType)
            if order.sz is not None:
                param['sz'] = str(abs(order.sz))
                if order.sz >= 0:
                    param['side'] = 'buy'
                else:
                    param['side'] = 'sell'
            if order.ccy is not None:
                param['ccy'] = enum_to_str(order.ccy)
            if order.clOrdId is not None:
                param['clOrdId'] = str(order.clOrdId)
            if order.tag is not None:
                param['tag'] = str(order.tag)
            if order.posSide is not None:
                param['posSide'] = enum_to_str(order.posSide)

            if order.reduceOnly is not None:
                if isinstance(order.reduceOnly, bool):
                    if order.reduceOnly:
                        param['reduceOnly'] = 'true'
                    else:
                        param['reduceOnly'] = 'false'
                else:
                    param['reduceOnly'] = str(order.reduceOnly)
            if order.tgtCcy is not None:
                param['tgtCcy'] = enum_to_str(order.tgtCcy)
            params.append(param)

        data = self._request_with_params(POST, BATCH_ORDERS, params)["data"]

        return data

    def cancel_order(self, inst_id: str, ord_id: Optional[str] = None, cl_ord_id: Optional[str] = None):
        params = dict()

        if inst_id is not None:
            params['instId'] = str(inst_id)
        if ord_id is not None:
            params['ordId'] = str(ord_id)
        if cl_ord_id is not None:
            params['clOrdId'] = str(cl_ord_id)

        data = self._request_with_params(POST, CANCEL_ORDER, params)["data"]
        return data

    def cancel_batch_orders(self, orders: Union[CancelOrder, Iterable[CancelOrder]]):
        orders_list = []
        if isinstance(orders, Order):
            orders_list.append(orders)
        else:
            orders_list = orders
        params = []

        for order in orders_list:
            param = dict()
            if order.instId is not None:
                param["instId"] = str(order.instId)
            if order.ordId is not None:
                param["ordId"] = str(order.ordId)
            if order.clOrdId is not None:
                param["clOrdId"] = str(order.clOrdId)
            params.append(param)

        data = self._request_with_params(POST, CANCEL_BATCH_ORDERS, params)["data"]
        return data

    def get_order(self, inst_id: str, ord_id: Optional[str] = None, cl_ord_id: Optional[str] = None) -> Dict:
        params = {}
        if inst_id is not None:
            params['instId'] = str(inst_id)
        if ord_id is not None:
            params['ordId'] = str(ord_id)
        if cl_ord_id is not None:
            params['clOrdId'] = str(cl_ord_id)

        data = self._request_with_params(GET, ORDER, params)["data"]

        return data

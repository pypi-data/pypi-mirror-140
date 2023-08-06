from typing import Iterable, Optional, Union

import pandas as pd
from notecoin.okex.common.exceptions import OkexParamsException
from notecoin.okex.v5.client.base import BaseClient
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.types import (BillSubType, BillType, CcyType, CtType,
                                    InstType, MgnMode)
from notecoin.okex.v5.utils import enum_to_str, iterable_to_str


class AccountAPI(BaseClient):
    def __init__(self, *args, **kwargs):
        super(AccountAPI, self).__init__(*args, **kwargs)

    # get account position risk
    def position_risk(self, inst_type: Optional[Union[InstType, str]] = None):
        params = {}
        if inst_type is not None:
            params['instType'] = enum_to_str(inst_type)
        data = self._request_with_params(GET, POSITION_RISK, params)["data"]

        # df = pd.DataFrame(data)
        return data

    # get balance
    def balance(self, ccy_type: Optional[Union[CcyType, str]] = None):
        params = {}
        if ccy_type is not None:
            params['ccyType'] = enum_to_str(ccy_type)
        return self._request_with_params(GET, BALANCE, params)['data']

    # get specific currency info
    def positions(
            self, inst_type: Optional[Union[InstType, str]] = None, inst_id: Optional[str] = None,
            pos_id: Optional[Union[str, Iterable]] = None):
        params = {}
        if inst_type is not None:
            params['instType'] = enum_to_str(inst_type)
        if inst_id is not None:
            params['instId'] = inst_id
        if pos_id is not None:
            posIdList = list(pos_id)
            if len(posIdList) > 20:
                raise OkexParamsException("支持多个posId查询（不超过20个）")
            else:
                params['instId'] = iterable_to_str(posIdList)

        data = self._request_with_params(GET, POSITIONS, params)['data']
        return data

    def bills(self, inst_type: Optional[Union[InstType, str]] = None,
              ccy_type: Optional[Union[InstType, str]] = None,
              mgn_mode: Optional[Union[MgnMode, str]] = None,
              ct_type: Optional[Union[CtType, str]] = None,
              bill_type: Optional[Union[BillType, str]] = None,
              bill_subtype: Optional[Union[BillSubType, str]] = None,
              after: Optional[int] = None,
              before: Optional[int] = None,
              limit: Optional[int] = None
              ):
        params = {}
        if inst_type is not None:
            params['instType'] = enum_to_str(inst_type)
        if ccy_type is not None:
            params['ccyType'] = enum_to_str(ccy_type)
        if mgn_mode is not None:
            params['mgnMode'] = enum_to_str(mgn_mode)
        if ct_type is not None:
            params['ctType'] = enum_to_str(ct_type)
        if bill_type is not None:
            params['type'] = enum_to_str(bill_type)
        if bill_subtype is not None:
            params['subType'] = enum_to_str(bill_subtype)
        if after is not None:
            params['after'] = str(after)
        if before is not None:
            params['before'] = str(before)
        if limit is not None:
            params['befolimitre'] = str(limit)

        data = self._request_with_params(GET, BILLS, params)['data']

        df = pd.DataFrame(data, columns=["instType", "billId", "type", "subType", "ts", "balChg", "posBalChg",
                                         "bal", "posBal", "sz", "ccy", "pnl", "fee", "mgnMode",
                                         "instId", "ordId", "from", "to", "notes"])

        return df

    def bills_archive(self, inst_type: Optional[Union[InstType, str]] = None,
                      ccy_type: Optional[Union[InstType, str]] = None,
                      mgn_mode: Optional[Union[MgnMode, str]] = None,
                      ct_type: Optional[Union[CtType, str]] = None,
                      bill_type: Optional[Union[BillType, str]] = None,
                      bill_subtype: Optional[Union[BillSubType, str]] = None,
                      after: Optional[int] = None,
                      before: Optional[int] = None,
                      limit: Optional[int] = None
                      ):
        params = {}
        if inst_type is not None:
            params['instType'] = enum_to_str(inst_type)
        if ccy_type is not None:
            params['ccyType'] = enum_to_str(ccy_type)
        if mgn_mode is not None:
            params['mgnMode'] = enum_to_str(mgn_mode)
        if ct_type is not None:
            params['ctType'] = enum_to_str(ct_type)
        if bill_type is not None:
            params['type'] = enum_to_str(bill_type)
        if bill_subtype is not None:
            params['subType'] = enum_to_str(bill_subtype)
        if after is not None:
            params['after'] = str(after)
        if before is not None:
            params['before'] = str(before)
        if limit is not None:
            params['befolimitre'] = str(limit)

        data = self._request_with_params(GET, BILLS_ARCHIVE, params)['data']

        df = pd.DataFrame(data, columns=["instType", "billId", "type", "subType", "ts", "balChg", "posBalChg",
                                         "bal", "posBal", "sz", "ccy", "pnl", "fee", "mgnMode",
                                         "instId", "ordId", "from", "to", "notes"])

        return df

    def config(self):
        data = self._request_without_params(GET, CONFIG)['data']
        return data

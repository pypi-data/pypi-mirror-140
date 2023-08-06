import datetime
from typing import Iterable, Optional, Union

import pandas as pd
from notecoin.okex.common.exceptions import OkexParamsException
from notecoin.okex.v5.ccytype import CcyType
from notecoin.okex.v5.client import Client
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.insttype import InstType
from notecoin.okex.v5.utils import enum_to_str, iterable_to_str


class AssetAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, test=False, first=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, test, first)

    def deposit_address(self, ccy: Union[CcyType, str]):
        params = {}
        if ccy is not None:
            params['ccy'] = enum_to_str(ccy)

        data = self._request_with_params(GET, DEPOSIT_ADDRESS, params)["data"]

        return data

    def balances(self, ccy: Optional[Union[CcyType, str, Iterable[Union[CcyType, str]]]] = None):
        params = {}
        if ccy is not None:
            if isinstance(ccy, Iterable):
                ccyList = list(ccy)
                if len(ccyList) > 20:
                    raise OkexParamsException("支持多个ccy查询（不超过20个）")
                else:
                    params['ccy'] = iterable_to_str(ccyList)
            else:
                params['ccy'] = enum_to_str(ccy)

        data = self._request_with_params(GET, BALANCES, params)["data"]

        return data

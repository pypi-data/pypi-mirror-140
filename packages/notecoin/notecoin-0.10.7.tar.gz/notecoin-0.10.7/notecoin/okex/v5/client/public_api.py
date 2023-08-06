import datetime
from typing import Iterable, Optional, Union

import pandas as pd
from notecoin.okex.common.exceptions import OkexParamsException
from notecoin.okex.v5.client.client import Client
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.types import CcyType, InstType
from notecoin.okex.v5.utils import enum_to_str, iterable_to_str


class PublicAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, test=False, first=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, test, first)

    def instruments(self, instType: Union[InstType, str], uly: Optional[str] = None, instId: Optional[str] = None):
        params = {}
        if instType is not None:
            params['instType'] = enum_to_str(instType)
        if uly is not None:
            params['uly'] = uly
        if instId is not None:
            params['instId'] = instId
        data = self._request_with_params(GET, INSTRUMENTS, params)["data"]

        df = pd.DataFrame(data)
        df = df.apply(pd.to_numeric, errors='ignore')
        return df

    def delivery_exercise_history(self, instType: Union[InstType, str],
                                  uly: str,
                                  after: Optional[Union[int, str]] = None,
                                  before: Optional[Union[int, str]] = None,
                                  limit: Optional[Union[int, str]] = None):
        pass

    def open_interest(self,
                      instType: Union[InstType, str],
                      uly: Optional[str],
                      instId: Optional[str]):
        pass

    def funding_rate(self, instId: str):
        pass

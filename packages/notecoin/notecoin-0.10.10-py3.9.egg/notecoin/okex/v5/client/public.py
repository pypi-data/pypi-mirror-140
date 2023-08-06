from typing import Optional, Union

import pandas as pd
from notecoin.okex.v5.client.base import BaseClient
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.types import InstType
from notecoin.okex.v5.utils import enum_to_str


class PublicAPI(BaseClient):

    def __init__(self, *args, **kwargs):
        super(PublicAPI, self).__init__(*args, **kwargs)

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

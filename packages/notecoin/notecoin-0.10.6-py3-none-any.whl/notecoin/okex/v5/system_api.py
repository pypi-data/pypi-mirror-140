import datetime
from typing import Iterable, Optional, Union

import pandas as pd
from notecoin.okex.common.exceptions import OkexParamsException
from notecoin.okex.v5.client import Client
from notecoin.okex.v5.consts import *
from notecoin.okex.v5.types import CcyType, InstType
from notecoin.okex.v5.utils import enum_to_str, iterable_to_str


class SystemAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, test=False, first=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, test, first)

    def status(self, state: Optional[str] = None):
        params = {}
        if state is not None:
            params['state'] = state

        data = self._request_with_params(GET, INSTRUMENTS, params)["data"]

        return data

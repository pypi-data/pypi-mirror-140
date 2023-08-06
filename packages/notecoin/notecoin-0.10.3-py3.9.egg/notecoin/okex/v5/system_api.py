import datetime
from typing import Iterable, Optional, Union

import pandas as pd

from ..exceptions import OkexParamsException
from .ccytype import CcyType
from .client import Client
from .consts import *
from .insttype import InstType
from .utils import enum_to_str, iterable_to_str


class SystemAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, test=False, first=False):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, test, first)

    def status(self, state: Optional[str] = None):
        params = {}
        if state is not None:
            params['state'] = state

        data = self._request_with_params(GET, INSTRUMENTS, params)["data"]

        return data

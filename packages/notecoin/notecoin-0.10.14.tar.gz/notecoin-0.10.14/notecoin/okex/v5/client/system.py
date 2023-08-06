from typing import Optional

from notecoin.okex.v5.client.base import BaseClient
from notecoin.okex.v5.consts import *


class SystemClient(BaseClient):

    def __init__(self, *args, **kwargs):
        super(SystemClient, self).__init__(*args, **kwargs)

    def status(self, state: Optional[str] = None):
        params = {}
        if state is not None:
            params['state'] = state

        data = self._request_with_params(GET, INSTRUMENTS, params)["data"]

        return data

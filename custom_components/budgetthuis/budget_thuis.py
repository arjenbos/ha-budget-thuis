import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

_LOGGER = logging.getLogger(__name__)


class BudgetThuis:
    baseUrlAccounts: str = "https://accounts.budgetthuis.nl"

    def __init__(self, access_token: str):
        self.client = requests.Session()
        self.client.mount(
            prefix='https://',
            adapter=HTTPAdapter(
                max_retries=Retry(
                    total=5,
                    backoff_factor=3
                ),
                pool_maxsize=25,
                pool_block=True
            )
        )
        self.client.headers = {
            "Authorization": "Bearer " + access_token
        }

    def get_user_info(self):
        response = self.client.get(self.baseUrlAccounts + "/connect/userinfo")
        response.raise_for_status()
        return response.json()

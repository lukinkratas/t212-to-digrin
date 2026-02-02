import datetime
from typing import Any

import requests

from .utils import log_func

import logging

logger = logging.getLogger(__name__)

class Client(object):
    def __init__(self, key: str):
        self.key = key

    @log_func(logger.debug)
    def create_report(
        self,
        from_dt: str,
        to_dt: str,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions: bool = True,
    ) -> int | None:
        """Spawns T212 csv export process."""
        url = 'https://live.trading212.com/api/v0/history/exports'
        payload = {
            'dataIncluded': {
                'includeDividends': include_dividends,
                'includeInterest': include_interest,
                'includeOrders': include_orders,
                'includeTransactions': include_transactions,
            },
            'timeFrom': from_dt,
            'timeTo': to_dt,
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.key,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('reportId')

    @log_func(logger.debug)
    def list_reports(self) -> list[dict[str, Any]] | None:
        """Fetches list of reports."""
        url = 'https://live.trading212.com/api/v0/history/exports'
        headers = {'Authorization': self.key}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

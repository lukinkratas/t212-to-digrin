import logging
from typing import Any

import requests
from requests.exceptions import HTTPError

from .utils import log_func

logger = logging.getLogger(__name__)


class Client(object):
    """Client for Trading 212 API."""

    BASE_URL = "https://live.trading212.com/api/v0"

    def __init__(self, api_key_id: str, secret_key: str):
        self.api_key_id = api_key_id
        self.secret_key = secret_key

    @log_func(logger.debug)
    def export_report(
        self,
        from_dt: str,
        to_dt: str,
        include_dividends: bool = True,
        include_interest: bool = True,
        include_orders: bool = True,
        include_transactions: bool = True,
    ) -> int | None:
        """Spawn T212 csv export process."""
        url = f"{self.BASE_URL}/history/exports"
        payload = {
            "dataIncluded": {
                "includeDividends": include_dividends,
                "includeInterest": include_interest,
                "includeOrders": include_orders,
                "includeTransactions": include_transactions,
            },
            "timeFrom": from_dt,
            "timeTo": to_dt,
        }
        headers = {"Content-Type": "application/json"}
        auth = (self.api_key_id, self.secret_key)

        try:
            response = requests.post(url, json=payload, headers=headers, auth=auth)
            response.raise_for_status()

        except HTTPError as e:
            logger.warning(e)
            return None

        return response.json()["reportId"]

    @log_func(logger.debug)
    def list_exports(self) -> list[dict[str, Any]] | None:
        """Fetch list of reports."""
        url = f"{self.BASE_URL}/history/exports"
        auth = (self.api_key_id, self.secret_key)

        try:
            response = requests.get(url, auth=auth)
            response.raise_for_status()

        except HTTPError as e:
            logger.warning(e)
            return None

        return response.json()

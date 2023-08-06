import logging
from typing import Any, Dict, List, Optional

import requests

from .utils import clean_params

logger = logging.getLogger(__name__)


class CryptowatchAPIError(Exception):
    def __init__(self, response, message=""):
        super().__init__(message)
        self.response = response
        self.message = message

    def __str__(self):
        return f"{self.response.status_code} {self.response.content.decode()}"


class Cryptowatch:
    """Cryptowatch API wrapper.

    Web: https://cryptowat.ch/
    Doc: https://docs.cryptowat.ch/rest-api/
    """

    BASE_URL = "https://api.cryptowat.ch/"

    def __init__(
        self, key: Optional[str] = None, fail_silently: bool = False
    ) -> None:
        self.key = key
        self.fail_silently = fail_silently

    def _get_headers(self):
        headers = {}
        if self.key:
            headers["X-CW-API-Key"] = self.key
        return headers

    def _get(self, path, params: Optional[Dict[str, Any]] = None):
        """Get requests to the specified path on Cryptowatch API."""
        r = requests.get(
            url=self.BASE_URL + path,
            headers=self._get_headers(),
            params=clean_params(params),
        )

        if r.status_code == 200:
            return r.json()

        self._fail(r)

    def _fail(self, r):
        details = r.content.decode()
        try:
            details = r.json()
        except Exception:
            pass

        if not self.fail_silently:
            logger.warning(
                f"Cryptowatch API error {r.status_code} on {r.url}: {details}"
            )
            raise CryptowatchAPIError(response=r)

        logger.info(
            f"Cryptowatch API silent error {r.status_code} on {r.url}: "
            f"{details}"
        )

    def get_assets(self):
        """All Assets."""
        return self._get("assets")

    def get_asset(self, symbol: str):
        """Asset Details."""
        return self._get(f"assets/{symbol}")

    def get_pairs(self):
        """All Pairs."""
        return self._get("pairs")

    def get_pair(self, pair: str):
        """Get Pair Details."""
        return self._get(f"pairs/{pair}")

    def get_markets(self):
        """All Markets."""
        return self._get("markets")

    def get_market(self, exchange: str, pair: str):
        """Market Details."""
        return self._get(f"markets/{exchange}/{pair}")

    def get_market_price(self, exchange: str, pair: str):
        """Market Price."""
        return self._get(f"markets/{exchange}/{pair}/price")

    def get_market_prices(self):
        """All Market Prices."""
        return self._get("markets/prices")

    def get_market_trades(
        self,
        exchange: str,
        pair: str,
        since: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """Market Trades."""
        return self._get(
            f"markets/{exchange}/{pair}/trades",
            params={"since": since, "limit": limit},
        )

    def get_market_summary(self, exchange: str, pair: str):
        """Market Summary."""
        return self._get(f"markets/{exchange}/{pair}/summary")

    def get_market_summaries(self, key_by: Optional[str] = None):
        """All Market Summaries."""
        return self._get(
            "markets/summaries",
            params={"keyBy": key_by},
        )

    def get_order_book(
        self,
        exchange: str,
        pair: str,
        depth: Optional[int] = None,
        span: Optional[float] = None,
        limit: Optional[int] = None,
    ):
        """Order Book."""
        return self._get(
            f"markets/{exchange}/{pair}/orderbook",
            params={
                "depth": depth,
                "span": span,
                "limit": limit,
            },
        )

    def get_order_book_liquidity(self, exchange: str, pair: str):
        """Order Book Liquidity."""
        return self._get(f"markets/{exchange}/{pair}/orderbook/liquidity")

    def get_order_book_calculator(
        self,
        exchange: str,
        pair: str,
        amount: Optional[int] = None,
    ):
        """Order Book Calculator."""
        return self._get(
            f"markets/{exchange}/{pair}/orderbook/calculator",
            params={"amount": amount},
        )

    def get_ohlc(
        self,
        exchange: str,
        pair: str,
        before: Optional[int] = None,
        after: Optional[int] = None,
        periods: Optional[List[int]] = None,
    ):
        """Market OHLC."""
        return self._get(
            f"markets/{exchange}/{pair}/ohlc",
            params={
                "before": before,
                "after": after,
                "periods": periods,
            },
        )

    def get_exchanges(self):
        """All Exchanges."""
        return self._get("exchanges")

    def get_exchange(self, exchange: str):
        """Exchange Details."""
        return self._get(f"exchanges/{exchange}")

    def get_exchange_markets(self, exchange: str):
        """Exchange Markets."""
        return self._get(f"markets/{exchange}")

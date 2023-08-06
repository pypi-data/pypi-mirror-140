import logging
from typing import Any, Dict, List, Optional

import requests

from .utils import clean_params

logger = logging.getLogger(__name__)


class KeyTypeError(Exception):
    def __init__(self, function, message=""):
        super().__init__(message)
        self.func_name = function.__name__
        self.message = message
        logger.error(self.__str__())

    def __str__(self):
        return f"'{self.func_name}' is unavailable without a paid plans."


def requires_paid_plans(func):
    def wrapper_func(self, *args, **kwargs):
        if not self.paid_plans:
            raise KeyTypeError(func)
        func(self, *args, **kwargs)

    return wrapper_func


class NomicsAPIError(Exception):
    def __init__(self, response, message=""):
        super().__init__(message)
        self.response = response
        self.message = message

    def __str__(self):
        return f"{self.response.status_code} {self.response.content.decode()}"


class Nomics:
    """Nomics API wrapper.

    Web: https://nomics.com/
    Doc: https://nomics.com/docs/
    """

    BASE_URL = "https://api.nomics.com/"

    def __init__(
        self, key: str, paid_plans: bool = False, fail_silently: bool = False
    ) -> None:
        self.key = key
        self.paid_plans = paid_plans
        self.fail_silently = fail_silently

    def _get(
        self,
        path: str,
        params: Dict[str, Any] = dict(),
    ) -> Any:
        params.update({"key": self.key})

        r = requests.get(
            url=self.BASE_URL + path,
            params=clean_params(params),
        )

        if r.status_code == 200:
            return r.json()

        self._fail(r)

        return None

    def _fail(self, r):
        details = r.content.decode()
        try:
            details = r.json()
        except Exception:
            pass

        if not self.fail_silently:
            logger.warning(
                f"Nomics API error {r.status_code} on {r.url}: {details}"
            )
            raise NomicsAPIError(response=r)

        logger.info(
            f"Nomics API silent error {r.status_code} on {r.url}: " f"{details}"
        )

    def get_currencies_ticker(
        self,
        ids: List[str],
        interval: List[str],
        convert: str = "USD",
        status: Optional[str] = None,
        filter_param: Optional[str] = None,
        sort: Optional[str] = None,
        include_transparency: Optional[str] = None,
        per_page: int = 100,
        page: int = 1,
    ):
        return self._get(
            "v1/currencies/ticker",
            params={
                "ids": ids,
                "interval": interval,
                "convert": convert,
                "status": status,
                "filter": filter_param,
                "sort": sort,
                "include-transparency": include_transparency,
                "per-page": per_page,
                "page": page,
            },
        )

    def get_currencies_sparkline(
        self,
        ids: str,
        start: str,
        end: Optional[str] = None,
        convert: Optional[str] = None,
    ):
        return self._get(
            "v1/currencies/sparkline",
            params={
                "ids": ids,
                "start": start,
                "end": end,
                "convert": convert,
            },
        )

    def get_market(
        self,
        exchange: Optional[str] = None,
        base: Optional[str] = None,
        quote: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/markets",
            params={
                "exchange": exchange,
                "base": base,
                "quote": quote,
                "format": format,
            },
        )

    def get_marketcap_history(
        self,
        start: str,
        end: Optional[str] = None,
        convert: Optional[str] = None,
        format: Optional[str] = None,
        include_transparency: Optional[bool] = None,
    ):
        return self._get(
            "v1/market-cap/history",
            params={
                "start": start,
                "end": end,
                "convert": convert,
                "format": format,
                "include_transparency": include_transparency,
            },
        )

    def get_global_volume_history(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        convert: Optional[str] = None,
        format: Optional[str] = None,
        include_transparency: Optional[bool] = None,
    ):
        return self._get(
            "v1/volume/history",
            params={
                "start": start,
                "end": end,
                "convert": convert,
                "format": format,
                "include_transparency": include_transparency,
            },
        )

    def get_exchange_rates(self):
        return self._get("v1/exchange-rates")

    def get_exchange_rates_history(self):
        return self._get("v1/exchange-rates/history")

    def get_global_ticker(self, convert):
        return self._get("v1/global-ticker", params={"convert": convert})

    def get_currency_highlights(
        self,
        currency: str,
        convert: Optional[str] = None,
        interval: Optional[str] = None,
    ):
        return self._get(
            "v1/currencies/highlights",
            params={
                "currency": currency,
                "convert": convert,
                "interval": interval,
            },
        )

    def get_supply_history(
        self,
        currency: str,
        start: str,
        end: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "/v1/supplies/history",
            params={
                "currency": currency,
                "start": start,
                "end": end,
                "format": format,
            },
        )

    def get_exchange_highlights(
        self,
        exchange: str,
        convert: Optional[str] = None,
        interval: Optional[str] = None,
    ):
        return self._get(
            "/v1/exchanges/highlights",
            params={
                "exchange": exchange,
                "convert": convert,
                "interval": interval,
            },
        )

    def get_exchanges_ticker(
        self,
        ids: Optional[str] = None,
        interval: Optional[str] = None,
        convert: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        centralized: Optional[str] = None,
        decentralized: Optional[str] = None,
        per_page: Optional[int] = None,
        page: Optional[int] = None,
        sort: Optional[str] = None,
    ):
        return self._get(
            "v1/exchanges/ticker",
            params={
                "ids": ids,
                "interval": interval,
                "convert": convert,
                "status": status,
                "type": type,
                "centralized": centralized,
                "decentralized": decentralized,
                "per-page": per_page,
                "page": page,
                "sort": sort,
            },
        )

    def get_exchanges_volume_history(
        self,
        exchange: str,
        start: str,
        end: Optional[str] = None,
        convert: Optional[str] = None,
        format: Optional[str] = None,
        include_transparency: Optional[bool] = None,
    ):
        return self._get(
            "v1/exchanges/volume/history",
            params={
                "exchange": exchange,
                "start": start,
                "end": end,
                "convert": convert,
                "format": format,
                "include_transparency": include_transparency,
            },
        )

    def get_exchange_metadata(
        self,
        ids: Optional[str] = None,
        attribute: Optional[str] = None,
        centralized: Optional[str] = None,
        decentralized: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/exchanges",
            params={
                "ids": ids,
                "attribute": attribute,
                "centralized": centralized,
                "decentralized": decentralized,
                "format": format,
            },
        )

    def get_market_highlights(
        self,
        base: str,
        quote: str,
        convert: Optional[str] = None,
        interval: Optional[str] = None,
    ):
        return self._get(
            "v1/exchange-markets/highlights",
            params={
                "base": base,
                "quote": quote,
                "convert": convert,
                "interval": interval,
            },
        )

    @requires_paid_plans
    def get_exchange_markets_ticker(
        self,
        interval: Optional[str] = None,
        currency: Optional[str] = None,
        base: Optional[str] = None,
        quote: Optional[str] = None,
        exchange: Optional[str] = None,
        market: Optional[str] = None,
        convert: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        per_page: Optional[str] = None,
        page: Optional[int] = None,
        sort: Optional[str] = None,
    ):
        return self._get(
            "v1/exchange-markets/ticker",
            params={
                "interval": interval,
                "currency": currency,
                "base": base,
                "quote": quote,
                "exchange": exchange,
                "market": market,
                "convert": convert,
                "status": status,
                "search": search,
                "per_page": per_page,
                "page": page,
                "sort": sort,
            },
        )

    @requires_paid_plans
    def get_aggregated_ohlcv_candles(
        self,
        interval: str,
        currency: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/candles",
            params={
                "interval": interval,
                "currency": currency,
                "start": start,
                "end": end,
                "format": format,
            },
        )

    @requires_paid_plans
    def get_exchange_ohlcv_candles(
        self,
        interval: str,
        exchange: str,
        market: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/exchange_candles",
            params={
                "interval": interval,
                "exchange": exchange,
                "market": market,
                "start": start,
                "end": end,
                "format": format,
            },
        )

    @requires_paid_plans
    def get_aggregated_pair_ohlcv_candles(
        self,
        interval: str,
        base: str,
        quote: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/exchange_candles",
            params={
                "interval": interval,
                "base": base,
                "quote": quote,
                "start": start,
                "end": end,
                "format": format,
            },
        )

    @requires_paid_plans
    def get_trades(
        self,
        exchange: str,
        market: str,
        limit: Optional[int] = None,
        order: Optional[str] = None,
        from_timestamp: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/trades",
            params={
                "exchange": exchange,
                "market": market,
                "limit": limit,
                "order": order,
                "from": from_timestamp,
                "format": format,
            },
        )

    @requires_paid_plans
    def get_order_book_snapshot(
        self,
        exchange: str,
        market: str,
        at: Optional[str] = None,
        format: Optional[str] = None,
    ):
        return self._get(
            "v1/orders/snapshot",
            params={
                "exchange": exchange,
                "market": market,
                "at": at,
                "format": format,
            },
        )

    @requires_paid_plans
    def get_order_book_batches(
        self, exchange: str, market: str, date: Optional[str] = None
    ):
        return self._get(
            "v1/orders/batches",
            params={"exchange": exchange, "market": market, "date": date},
        )

    @requires_paid_plans
    def get_currency_predictions_ticker(self, ids: Optional[str] = None):
        return self._get(
            "v1/currencies/predictions/ticker", params={"ids": ids}
        )

    @requires_paid_plans
    def get_currency_predictions_history(
        self,
        id: Optional[str] = None,
        interval: Optional[str] = None,
    ):
        return self._get(
            "v1/currencies/predictions/history",
            params={"id": id, "interval": interval},
        )

    def get_currencies(
        self,
        ids: List[str],
        attributes: List[str],
        format_param: Optional[str] = None,
    ):
        return self._get(
            "v1/currencies",
            params={
                "ids": ids,
                "attributes": attributes,
                "format": format_param,
            },
        )

    @requires_paid_plans
    def get_currencies_predictions_ticket(self, ids: List[str]):
        return self._get(
            "/v1/currencies/predictions/ticker",
            params={"ids": ids},
        )

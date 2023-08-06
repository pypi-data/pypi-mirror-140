"""CoinMarketCap API wrapper.

Web: https://coinmarketcap.com/
Doc: https://coinmarketcap.com/api/documentation/v1/
"""
import logging
from typing import Any, Callable, Dict, List, Optional

import requests

from .utils import clean_params

logger = logging.getLogger(__name__)


class KeyTypeError(Exception):
    """Wrong key type exception.

    Raised in case of wrong key type.
    """

    def __init__(
        self, function, required_key_type, current_key_type, message=""
    ):
        super().__init__(message)
        self.function_name = function.__name__
        self.required_key_type = required_key_type
        self.current_key_type = current_key_type
        self.message = message
        logger.error(self.__str__())

    def __str__(self):
        return (
            f"{self.required_key_type} endpoint '{self.function_name}' is "
            f"unavailable with key type: {self.current_key_type}."
        )


def requires_startup(func: Callable):
    """Decorate function to impose startup key type requirement."""

    def wrapper_func(self, *args, **kwargs):
        if self.key_type not in [
            "startup",
            "standard",
            "professional",
            "enterprise",
        ]:
            raise KeyTypeError(func, "Startup", self.key_type)
        func(self, *args, **kwargs)

    return wrapper_func


def requires_standard(func: Callable):
    """Decorate function to impose standard key type requirement."""

    def wrapper_func(self, *args, **kwargs):
        if self.key_type not in ["standard", "professional", "enterprise"]:
            raise KeyTypeError(func, "Standard", self.key_type)
        func(self, *args, **kwargs)

    return wrapper_func


def requires_enterprise(func: Callable):
    """Decorate function to impose enterprise key type requirement."""

    def wrapper_func(self, *args, **kwargs):
        if self.key_type not in ["enterprise"]:
            raise KeyTypeError(func, "Enterprise", self.key_type)
        func(self, *args, **kwargs)

    return wrapper_func


class CoinMarketCapAPIError(Exception):
    def __init__(self, response, message=""):
        super().__init__(message)
        self.response = response
        self.message = message

    def __str__(self):
        return f"{self.response.status_code} {self.response.content.decode()}"


class CoinMarketCap:
    """CoinMarketCap API wrapper.

    Web: https://coinmarketcap.com/
    Doc: https://coinmarketcap.com/api/documentation/v1/
    """

    BASE_URL = "https://pro-api.coinmarketcap.com/"

    def __init__(
        self,
        key: str,
        key_type: str = "Basic",
        fail_silently: bool = False,
    ) -> None:
        """Init the CoinMarketCap API.

        Args:
            key (str): CoinMarketCap API key.
            key_type (:obj:`str`, optional): CoinMarketCap API Key type can be
                one of: Basic, Hobbyist, Startup, Standard, Professional,
                Enterprise. Defaults to Basic.
            fail_silently (:obj:`bool`, optional): If true an exception should
                be raise in case of wrong status code. Defaults to False.
        """
        self.key = key
        self.key_type = key_type.lower()
        self.fail_silently = fail_silently

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-CMC_PRO_API_KEY": self.key,
            "Accept": "application/json",
        }

    def _get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Get requests to the specified path on CoinMarketCap API."""
        r = requests.get(
            url=self.BASE_URL + path,
            params=clean_params(params),
            headers=self._get_headers(),
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
                f"CoinMarketCap API error {r.status_code} on {r.url}: {details}"
            )
            raise CoinMarketCapAPIError(response=r)

        logger.info(
            f"CoinMarketCap API silent error {r.status_code} on {r.url}: "
            f"{details}"
        )

    def get_airdrop(self, id: str):
        """Airdrop."""
        return self._get(
            "v1/cryptocurrency/airdrop",
            params={"id": id},
        )

    def get_airdrops(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        status: Optional[str] = None,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        symbol: Optional[str] = None,
    ):
        """Airdrops."""
        return self._get(
            "v1/cryptocurrency/airdrops",
            params={
                "start": start,
                "limit": limit,
                "status": status,
                "id": id,
                "slug": slug,
                "symbol": symbol,
            },
        )

    def get_categories(
        self,
        start: int = 1,
        limit: int = 5000,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
    ):
        """Categories."""
        return self._get(
            "v1/cryptocurrency/categories",
            params={
                "start": start,
                "limit": limit,
                "id": id,
                "slug": slug,
                "symbol": symbol,
            },
        )

    def get_category(
        self,
        id: str,
        start: int = 1,
        limit: int = 200,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Category.

        Returns information about a single coin category available on
        CoinMarketCap. Includes a paginated list of the cryptocurrency quotes
        and metadata for the category.
        """
        return self._get(
            "v1/cryptocurrency/category",
            params={
                "id": id,
                "start": start,
                "limit": limit,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    def get_info(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        address: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """Metadata.

        Returns all static metadata available for one or more cryptocurrencies.
        This information includes details like logo, description, official
        website URL, social links, and links to a cryptocurrency's technical
        documentation.
        """
        return self._get(
            "v1/cryptocurrency/info",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "address": address,
                "aux": aux,
            },
        )

    def get_map(
        self,
        listing_status: Optional[List[str]] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort: str = "cmc_rank",
        symbols: Optional[List[str]] = None,
        aux: Optional[List[str]] = None,
    ):
        """Cryptocurrency ID Map.

        Returns a mapping of all cryptocurrencies to unique CoinMarketCap ids.
        Per our Best Practices we recommend utilizing CMC ID instead of
        cryptocurrency symbols to securely identify cryptocurrencies with our
        other endpoints and in your own application logic. Each cryptocurrency
        returned includes typical identifiers such as name, symbol, and
        token_address for flexible mapping to id.

        By default this endpoint returns cryptocurrencies that have actively
        tracked markets on supported exchanges. You may receive a map of all
        inactive cryptocurrencies by passing listing_status=inactive. You may
        also receive a map of registered cryptocurrency projects that are
        listed but do not yet meet methodology requirements to have tracked
        markets via listing_status=untracked. Please review our methodology
        documentation for additional details on listing states.

        Cryptocurrencies returned include first_historical_data and
        last_historical_data timestamps to conveniently reference historical
        date ranges available to query with historical time-series data
        endpoints. You may also use the aux parameter to only include
        properties you require to slim down the payload if calling this
        endpoint frequently.

        listing_status = "active" (default), "inactive", or "untracked"
        sort = "id" (cmc default), or "cmc_rank" (our default)
        """
        return self._get(
            "v1/cryptocurrency/map",
            params={
                "listing_status": listing_status,
                "start": start,
                "limit": limit,
                "sort": sort,
                "symbol": symbols,
                "aux": aux,
            },
        )

    @requires_standard
    def get_listings_historical(
        self,
        date: str,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        sort: Optional[str] = None,
        sort_dir: Optional[str] = None,
        cryptocurrency_type: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """Get Listings Historical."""
        return self._get(
            "v1/cryptocurrency/listings/historical",
            params={
                "date": date,
                "start": start,
                "limit": limit,
                "convert": convert,
                "convert_id": convert_id,
                "sort": sort,
                "sort_dir": sort_dir,
                "cryptocurrency_type": sort_dir,
                "aux": aux,
            },
        )

    def get_listings_latest(
        self,
        start: Optional[int] = None,
        limit: int = 200,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
        market_cap_min: Optional[int] = None,
        market_cap_max: Optional[int] = None,
        volume_24h_min: Optional[int] = None,
        volume_24h_max: Optional[int] = None,
        circulating_supply_min: Optional[int] = None,
        circulating_supply_max: Optional[int] = None,
        percent_change_24h_min: Optional[int] = None,
        percent_change_24h_max: Optional[int] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        sort: Optional[str] = None,
        sort_dir: Optional[str] = None,
        cryptocurrency_type: Optional[str] = None,
        tag: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """Get Listings Latest."""
        return self._get(
            "v1/cryptocurrency/listings/latest",
            params={
                "start": start,
                "limit": limit,
                "price_min": price_min,
                "price_max": price_max,
                "volume_24h_min": volume_24h_min,
                "volume_24h_max": volume_24h_max,
                "circulating_supply_min": circulating_supply_min,
                "circulating_supply_max": circulating_supply_max,
                "percent_change_24h_min": percent_change_24h_min,
                "percent_change_24h_max": percent_change_24h_max,
                "convert": convert,
                "convert_id": convert_id,
                "sort": sort,
                "sort_dir": sort_dir,
                "cryptocurrency_type": cryptocurrency_type,
                "tag": tag,
                "aux": aux,
            },
        )

    @requires_standard
    def get_market_pairs_latest(
        self,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        symbol: Optional[str] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort_dir: Optional[str] = None,
        sort: Optional[str] = None,
        aux: Optional[List[str]] = None,
        matched_id: Optional[str] = None,
        matched_symbol: Optional[str] = None,
        category: Optional[str] = None,
        fee_type: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Market Pairs Latest."""
        return self._get(
            "v1/cryptocurrency/market-pairs/latest",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "start": start,
                "limit": limit,
                "sort_dir": sort_dir,
                "sort": sort,
                "aux": aux,
                "matched_id": matched_id,
                "matched_symbol": matched_symbol,
                "category": category,
                "fee_type": fee_type,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_startup
    def get_ohlcv_historical(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        time_period: Optional[str] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: Optional[int] = None,
        interval: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        skip_invalid: Optional[bool] = None,
    ):
        """OHLCV Historical."""
        return self._get(
            "v1/cryptocurrency/ohlcv/historical",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "time_period": time_period,
                "time_start": time_start,
                "time_end": time_end,
                "count": count,
                "interval": interval,
                "convert": convert,
                "convert_id": convert_id,
                "skip_invalid": skip_invalid,
            },
        )

    @requires_startup
    def get_ohlcv_latest(
        self,
        id: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        skip_invalid: Optional[bool] = None,
    ):
        """OHLCV Latest."""
        return self._get(
            "v1/cryptocurrency/ohlcv/latest",
            params={
                "id": id,
                "symbol": symbol,
                "convert": convert,
                "convert_id": convert_id,
                "skip_invalid": skip_invalid,
            },
        )

    @requires_startup
    def get_price_performance_stats_latest(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        time_period: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        skip_invalid: Optional[bool] = None,
    ):
        """Price Performance Stats."""
        return self._get(
            "v1/cryptocurrency/price-performance-stats/latest",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "time_period": time_period,
                "convert": convert,
                "convert_id": convert_id,
                "skip_invalid": skip_invalid,
            },
        )

    @requires_standard
    def get_quotes_historical(
        self,
        id: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: Optional[int] = None,
        interval: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        aux: Optional[List[str]] = None,
        skip_invalid: Optional[bool] = None,
    ):
        """Quotes Historical."""
        return self._get(
            "v1/cryptocurrency/quotes/historical",
            params={
                "id": id,
                "symbol": symbol,
                "time_start": time_start,
                "time_end": time_end,
                "count": count,
                "interval": interval,
                "convert": convert,
                "convert_id": convert_id,
                "aux": aux,
                "skip_invalid": skip_invalid,
            },
        )

    def get_quotes_latest(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        aux: Optional[List[str]] = None,
        skip_invalid: Optional[bool] = None,
    ):
        """Quotes Latest."""
        return self._get(
            "v1/cryptocurrency/quotes/latest",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "convert": convert,
                "convert_id": convert_id,
                "aux": aux,
                "skip_invalid": skip_invalid,
            },
        )

    @requires_startup
    def get_trending_gainers_losers(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        time_period: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Trending Gainers & Losers."""
        return self._get(
            "v1/cryptocurrency/trending/gainers-losers",
            params={
                "start": start,
                "limit": limit,
                "time_period": time_period,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_startup
    def get_trending_latest(
        self,
        limit: int = 200,
        start: Optional[int] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Trending Latest."""
        return self._get(
            "v1/cryptocurrency/trending/latest",
            params={
                "start": start,
                "limit": limit,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_startup
    def get_trending_most_visited(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        time_period: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Trending Most Visited."""
        return self._get(
            "v1/cryptocurrency/trending/most-visited",
            params={
                "start": start,
                "limit": limit,
                "time_period": time_period,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    def get_fiat_map(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        include_metals: Optional[bool] = None,
    ):
        """Fiat ID Map."""
        return self._get(
            "v1/fiat/map",
            params={
                "start": start,
                "limit": limit,
                "sort": sort,
                "include_metals": include_metals,
            },
        )

    def get_exchange_info(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        aux: Optional[List[str]] = None,
    ):
        """Metadata."""
        return self._get(
            "v1/exchange/info",
            params={
                "id": id,
                "slug": slug,
                "aux": aux,
            },
        )

    def get_exchange_map(
        self,
        listing_status: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        aux: Optional[List[str]] = None,
        crypto_id: Optional[str] = None,
    ):
        """Exchange ID Map."""
        return self._get(
            "v1/exchange/map",
            params={
                "listing_status": listing_status,
                "slug": slug,
                "start": start,
                "limit": limit,
                "sort": sort,
                "aux": aux,
                "crypto_id": crypto_id,
            },
        )

    @requires_standard
    def get_exchange_listings_latest(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        sort_dir: Optional[str] = None,
        market_type: Optional[str] = None,
        category: Optional[str] = None,
        aux: Optional[List[str]] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Get Listings Latest."""
        return self._get(
            "v1/exchange/listings/latest",
            params={
                "start": start,
                "limit": limit,
                "sort": sort,
                "sort_dir": sort_dir,
                "market_type": market_type,
                "category": category,
                "aux": aux,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_standard
    def get_exchange_market_pairs_latest(
        self,
        id: Optional[str] = None,
        slug: Optional[str] = None,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        aux: Optional[List[str]] = None,
        matched_id: Optional[str] = None,
        matched_symbol: Optional[str] = None,
        category: Optional[str] = None,
        fee_type: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Market Pairs Latest."""
        return self._get(
            "v1/exchange/market-pairs/latest",
            params={
                "id": id,
                "slug": slug,
                "start": start,
                "limit": limit,
                "aux": aux,
                "matched_id": matched_id,
                "matched_symbol": matched_symbol,
                "category": category,
                "fee_type": fee_type,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_standard
    def get_exchange_quotes_historical(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: Optional[int] = None,
        interval: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Quotes Historical."""
        return self._get(
            "v1/exchange/quotes/historical",
            params={
                "id": id,
                "slug": slug,
                "time_start": time_start,
                "time_end": time_end,
                "count": count,
                "interval": interval,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_standard
    def get_exchange_quotes_latest(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """Quotes Latest."""
        return self._get(
            "v1/exchange/quotes/latest",
            params={
                "id": id,
                "slug": slug,
                "convert": convert,
                "convert_id": convert_id,
                "aux": aux,
            },
        )

    @requires_standard
    def get_global_metrics_quotes_historical(
        self,
        time_start: Optional[str] = None,
        time_end: Optional[str] = None,
        count: Optional[int] = None,
        interval: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """Quotes Historical."""
        return self._get(
            "v1/global-metrics/quotes/historical",
            params={
                "time_start": time_start,
                "time_end": time_end,
                "count": count,
                "interval": interval,
                "convert": convert,
                "convert_id": convert_id,
                "aux": aux,
            },
        )

    def get_global_metrics_quotes_latest(
        self,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Quotes Latest."""
        return self._get(
            "v1/global-metrics/quotes/latest",
            params={"convert": convert, "convert_id": convert_id},
        )

    def get_tools_price_conversion(
        self,
        amount: float,
        id: Optional[str] = None,
        symbol: Optional[str] = None,
        time: Optional[str] = None,
        convert: Optional[List[str]] = None,
        convert_id: Optional[str] = None,
    ):
        """Price Conversion."""
        return self._get(
            "v1/tools/price-conversion",
            params={
                "amount": amount,
                "id": id,
                "symbol": symbol,
                "time": time,
                "convert": convert,
                "convert_id": convert_id,
            },
        )

    @requires_enterprise
    def get_blockchain_statistics_latest(
        self,
        id: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
    ):
        """Statistics Latest."""
        return self._get(
            "v1/blockchain/statistics/latest",
            params={"id": id, "symbol": symbol, "slug": slug},
        )

    def get_partners_flipside_crypto_fcas_listings_latest(
        self,
        start: Optional[int] = None,
        limit: Optional[str] = None,
        aux: Optional[List[str]] = None,
    ):
        """FCAS Listings Latest."""
        return self._get(
            "v1/partners/flipside-crypto/fcas/listings/latest",
            params={"start": start, "limit": limit, "aux": aux},
        )

    def get_partners_flipside_crypto_fcas_quotes_latest(
        self,
        id: Optional[List[str]] = None,
        slug: Optional[List[str]] = None,
        symbol: Optional[List[str]] = None,
        aux: Optional[List[str]] = None,
    ):
        """FCAS Quotes Latest."""
        return self._get(
            "v1/partners/flipside-crypto/fcas/quotes/latest",
            params={
                "id": id,
                "slug": slug,
                "symbol": symbol,
                "aux": aux,
            },
        )

    def get_key_info(self):
        """Key Info."""
        return self._get("v1/key/info")

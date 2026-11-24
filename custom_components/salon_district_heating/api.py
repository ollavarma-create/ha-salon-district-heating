"""Asynchronous LämpöVahti client."""
from urllib.parse import urljoin, urlsplit
import aiohttp
from .const import BASE_URL

class ApiError(Exception):
    """API request failed."""

class AuthenticationError(ApiError):
    """Invalid credentials."""

class RateLimitError(ApiError):
    """Request limit reached."""

class Client:
    def __init__(self, session, api_key):
        self.session = session
        self.api_key = api_key

    async def _pages(self, endpoint, params=None):
        url = urljoin(BASE_URL, endpoint)
        seen = set()
        rows = []
        while url:
            parts = urlsplit(url)
            base = urlsplit(BASE_URL)
            if (parts.scheme, parts.netloc) != (base.scheme, base.netloc) or not parts.path.startswith(base.path) or url in seen:
                raise ApiError("Invalid pagination URL")
            seen.add(url)
            try:
                async with self.session.get(url, params=params, headers={"X-API-Key": self.api_key}, timeout=aiohttp.ClientTimeout(total=30), allow_redirects=False) as response:
                    if response.status in (401, 403):
                        raise AuthenticationError("Authentication failed")
                    if response.status == 429:
                        raise RateLimitError("Rate limit reached")
                    if response.status != 200:
                        raise ApiError("Unexpected HTTP status")
                    data = await response.json()
                if not isinstance(data, dict) or not isinstance(data.get("results"), list) or any(not isinstance(row, dict) for row in data["results"]):
                    raise ApiError("Invalid response")
                rows.extend(data["results"])
                next_url = data.get("next")
                if next_url is not None and not isinstance(next_url, str):
                    raise ApiError("Invalid pagination")
                url = urljoin(url, next_url) if next_url else None
                params = None
            except (aiohttp.ClientError, TimeoutError, ValueError):
                raise ApiError("Connection or response error") from None
        return rows

    async def locations(self):
        rows = await self._pages("locations/")
        if any(type(row.get("id")) is not int or not isinstance(row.get("name"), str) for row in rows):
            raise ApiError("Invalid location")
        return rows

    async def consumptions(self, location_id, start, end):
        return await self._pages("consumptions/", {"location_id": location_id, "start": start, "end": end})


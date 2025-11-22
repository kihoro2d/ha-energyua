"""EnergyUA API Client."""

from __future__ import annotations

import socket
from datetime import datetime, time, timedelta
from typing import Any, TypedDict
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import aiohttp
from bs4 import BeautifulSoup

from .const import LOGGER

UKRAINE_TZ = ZoneInfo("Europe/Kiev")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class PeriodDict(TypedDict):
    """Represents a single period with start and end datetime."""

    start: datetime
    end: datetime


class EnergyUAApiClientError(Exception):
    """Exception to indicate a general API error."""


class EnergyUAApiClientCommunicationError(
    EnergyUAApiClientError,
):
    """Exception to indicate a communication error."""


class EnergyUAApiClient:
    """EnergyUA API Client."""

    def __init__(
        self,
        region: str | None = None,
        group: str | None = None,
    ) -> None:
        """Initialize the EnergyUA API Client."""
        self.region = region
        self.group = group

        self.regions: dict[str, str] = {}
        self.groups: dict[str, str] = {}
        self.periods: list[PeriodDict] = []

    async def fetch_regions(self) -> None:
        """Fetch regions data."""
        html = await self._fetch_html("https://energy-ua.info")
        soup = BeautifulSoup(html, "html.parser")

        self.regions = {"energy-ua.info": "Полтавська"}

        for link in soup.select("ul.footer_regions_list a"):
            href = link.get("href")
            name = link.text.strip()
            if isinstance(href, str) and "energy-ua.info" in href:
                host = urlparse(href).netloc
                if host and host not in self.regions:
                    self.regions[host] = name

        LOGGER.debug("Fetch regions data %s", self.regions)

    async def fetch_groups(self) -> None:
        """Fetch groups for the configured region."""
        if not self.region:
            LOGGER.warning(
                "Region must be set before fetching groups",
            )
            return

        html = await self._fetch_html(f"https://{self.region}")
        soup = BeautifulSoup(html, "html.parser")

        self.groups = {}

        for link in soup.select(".select_group_list a"):
            href = link.get("href")
            name = link.text.strip()
            if isinstance(href, str):
                group = href.split("/")[-1]
                if group and group not in self.groups:
                    self.groups[group] = name

        LOGGER.debug("Fetch groups data %s", self.groups)

    async def fetch_periods(self) -> None:
        """Fetch periods for the configured region and group."""
        if not self.region or not self.group:
            LOGGER.warning(
                "Region and Group must be set before fetching periods",
            )
            return

        html = await self._fetch_html(f"https://{self.region}/cherga/{self.group}")
        soup = BeautifulSoup(html, "html.parser")

        self.periods = []

        sections = soup.find_all("div", class_="scale_info")[:2]
        for i, section in enumerate(sections):
            day_date = datetime.now(UKRAINE_TZ).date() + timedelta(days=i)

            for span in section.select("div.periods_items span"):
                times = [b.get_text(strip=True) for b in span.find_all("b")[:2]]

                if len(times) == 2:  # noqa: PLR2004
                    start_str, end_str = times

                    start_time = time.fromisoformat(start_str)
                    end_time = time.fromisoformat(end_str)

                    start_dt = datetime.combine(day_date, start_time, tzinfo=UKRAINE_TZ)
                    end_dt = datetime.combine(day_date, end_time, tzinfo=UKRAINE_TZ)

                    if end_dt <= start_dt:
                        end_dt += timedelta(days=1)

                    self.periods.append({"start": start_dt, "end": end_dt})

        self.periods = self._merge_periods(self.periods)

        LOGGER.debug("Fetch periods data %s", self.periods)

    async def _fetch_html(self, url: str) -> str:
        """Fetch HTML content from the given URL."""
        try:
            async with (
                aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session,
                session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response,
            ):
                response.raise_for_status()
                return await response.text()
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching HTML - {exception}"
            raise EnergyUAApiClientCommunicationError(msg) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise EnergyUAApiClientError(msg) from exception

    def get_regions(self) -> list[dict]:
        """Get a list of regions."""
        regions_list = []

        for value, label in self.regions.items():
            region = {"value": value, "label": label}
            regions_list.append(region)

        return regions_list

    def get_region_by_value(
        self, value: str, *, only_label: bool = False
    ) -> dict[str, str] | str | None:
        """Get region data by value."""
        label = self.regions.get(value)

        if label is None or only_label:
            return label

        return {"value": value, "label": label}

    def get_region_by_label(self, label: str) -> dict | None:
        """Get region data by label."""
        for region in self.get_regions():
            if region["label"] == label:
                return region
        return None

    def get_groups(self) -> list[dict]:
        """Get a list of groups."""
        groups_list = []

        for value, label in self.groups.items():
            group = {"value": value, "label": label}
            groups_list.append(group)

        return groups_list

    def get_group_by_value(
        self, value: str, *, only_label: bool = False
    ) -> dict | str | None:
        """Get group data by value."""
        label = self.groups.get(value)

        if label is None or only_label:
            return label

        return {"value": value, "label": label}

    def get_group_by_label(self, label: str) -> dict | None:
        """Get group data by label."""
        for group in self.get_groups():
            if group["label"] == label:
                return group
        return None

    def get_period_at(self, at: datetime) -> PeriodDict | None:
        """Get period that includes the specified datetime."""
        for period in self.periods:
            if period["start"] <= at <= period["end"]:
                return period
        return None

    def get_periods_between(self, start: datetime, end: datetime) -> list[PeriodDict]:
        """Get all periods that overlap with the specified datetime range."""
        return [
            period
            for period in self.periods
            if period["start"] <= end and period["end"] >= start
        ]

    def get_region_label(self) -> str:
        """Get current region label."""
        label = self.get_region_by_value(self.region or "", only_label=True)
        return label if isinstance(label, str) else ""

    def get_group_label(self) -> str:
        """Get current group label."""
        label = self.get_group_by_value(self.group or "", only_label=True)
        return label if isinstance(label, str) else ""

    async def async_get_data(self) -> Any:
        """Get data from the API."""
        await self.fetch_periods()
        return {}

    @staticmethod
    def _merge_periods(periods: list[PeriodDict]) -> list[PeriodDict]:
        if not periods:
            return []

        periods.sort(key=lambda x: x["start"])
        merged = [periods[0]]

        for current in periods[1:]:
            last = merged[-1]

            if current["start"] <= last["end"]:
                last["end"] = max(last["end"], current["end"])
            else:
                merged.append(current)

        return merged

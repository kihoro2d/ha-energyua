"""DataUpdateCoordinator for EnergyUA."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.calendar import CalendarEvent
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import EnergyUAApiClientError, PeriodDict
from .const import (
    DOMAIN,
    LOGGER,
    STATE_NORMAL,
    STATE_OUTAGE,
    TIMEFRAME_TO_CHECK,
)

if TYPE_CHECKING:
    from datetime import datetime

    from .data import EnergyUAConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class EnergyUACoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: EnergyUAConfigEntry
    translations: dict[str, str]

    async def _async_setup(self) -> None:
        await self.async_fetch_translations()
        await self.config_entry.runtime_data.client.fetch_regions()
        await self.config_entry.runtime_data.client.fetch_groups()

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self.config_entry.runtime_data.client.async_get_data()
        except EnergyUAApiClientError as exception:
            raise UpdateFailed(exception) from exception

    async def async_fetch_translations(self) -> None:
        """Fetch translations."""
        self.translations = await async_get_translations(
            self.hass,
            self.hass.config.language,
            "common",
            [DOMAIN],
        )

    @property
    def region_label(self) -> str:
        """Get the configured region label."""
        return self.config_entry.runtime_data.client.get_region_label()

    @property
    def group_label(self) -> str:
        """Get the configured group label."""
        return self.config_entry.runtime_data.client.get_group_label()

    @property
    def current_state(self) -> str:
        """Get the current state."""
        period = self.config_entry.runtime_data.client.get_period_at(dt_util.now())
        LOGGER.debug("Current state: %s", period)
        return STATE_OUTAGE if period else STATE_NORMAL

    @property
    def next_outage(self) -> datetime | None:
        """Get the next outage time."""
        dt = self._get_next_power_change_dt(restore=False)
        LOGGER.debug("Next outage: %s", dt)
        return dt

    @property
    def next_restore(self) -> datetime | None:
        """Get the next restore time."""
        dt = self._get_next_power_change_dt(restore=True)
        LOGGER.debug("Next restore: %s", dt)
        return dt

    def get_current_event(self) -> CalendarEvent | None:
        """Get the event at the present time."""
        return self.get_event_at(dt_util.now())

    def get_event_at(self, at: datetime) -> CalendarEvent | None:
        """Get the event at a given time."""
        period = self.config_entry.runtime_data.client.get_period_at(at)
        return period and self._get_calendar_event(period)

    def get_events_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Get all events."""
        periods = self.config_entry.runtime_data.client.get_periods_between(
            start_date, end_date
        )
        return [self._get_calendar_event(period) for period in periods]

    def _get_calendar_event(self, period: PeriodDict) -> CalendarEvent:
        summary = self.translations.get(
            f"component.{DOMAIN}.common.electricity_outage", "Power outage"
        )
        description = f"{self.region_label} {self.group_label}"

        return CalendarEvent(
            start=period["start"],
            end=period["end"],
            summary=summary,
            description=description,
        )

    def _get_next_power_change_dt(self, *, restore: bool) -> datetime | None:
        now = dt_util.now()
        periods = self.config_entry.runtime_data.client.get_periods_between(
            now, now + TIMEFRAME_TO_CHECK
        )

        key = "end" if restore else "start"
        return min((p[key] for p in periods if p[key] > now), default=None)

"""Calendar platform for EnergyUA."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEntityDescription,
    CalendarEvent,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity import EnergyUAEntity

if TYPE_CHECKING:
    from datetime import datetime

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import EnergyUACoordinator
    from .data import EnergyUAConfigEntry

ENTITY_DESCRIPTIONS = (
    CalendarEntityDescription(
        key="outages", translation_key="outages", icon="mdi:calendar-alert"
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: EnergyUAConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    async_add_entities(
        EnergyUACalendar(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class EnergyUACalendar(EnergyUAEntity, CalendarEntity):
    """EnergyUA Calendar class."""

    entity_description: CalendarEntityDescription

    def __init__(
        self,
        coordinator: EnergyUACoordinator,
        entity_description: CalendarEntityDescription,
    ) -> None:
        """Initialize the calendar class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}-{self.entity_description.key}"
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the current or next upcoming event or None."""
        return self.coordinator.get_current_event()

    async def async_get_events(
        self,
        hass: HomeAssistant,  # noqa: ARG002
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        return self.coordinator.get_events_between(start_date, end_date)

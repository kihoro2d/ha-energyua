"""EnergyUAEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import EnergyUACoordinator


class EnergyUAEntity(CoordinatorEntity[EnergyUACoordinator]):
    """EnergyUAEntity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: EnergyUACoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            translation_key="energyua",
            translation_placeholders={
                "region": self.coordinator.region_label,
                "group": self.coordinator.group_label,
            },
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer="Energy-UA",
            model="Графіки відключень",
        )

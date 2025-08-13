"""
Defines orefree binary_sensor for Home Assistant.
"""

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


# For config flow support
async def async_setup_entry(hass, entry, async_add_entities):
    from .sensor import create_orefree_coordinator
    coordinator = await create_orefree_coordinator(hass)
    hass.data["orefree_coordinator"] = coordinator
    async_add_entities([
        OrefreeBinarySensor(coordinator)
    ])

class OrefreeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_name = "Orefree Active"
    _attr_unique_id = "orefree_active"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        return data.get("on", False)

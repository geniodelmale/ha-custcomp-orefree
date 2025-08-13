"""
Defines orefree binary_sensor for Home Assistant.
"""

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = hass.data.get("orefree_coordinator")
    if coordinator is None:
        from .sensor import create_orefree_coordinator
        coordinator = await create_orefree_coordinator(hass)
        hass.data["orefree_coordinator"] = coordinator
    async_add_entities([
        OrefreeBinarySensor(coordinator)
    ])

class OrefreeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_name = "Orefree"
    _attr_unique_id = "orefree"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def is_on(self):
        data = self.coordinator.data or {}
        return data.get("is_on", False)

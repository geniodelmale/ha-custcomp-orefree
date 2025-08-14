"""
Defines orefree sensors for Home Assistant.
"""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import create_orefree_coordinator

_LOGGER = logging.getLogger(__name__)


# For config flow support
async def async_setup_entry(hass, entry, async_add_entities):
    """Set up OreFree sensors."""
    coordinator = hass.data.get("orefree_coordinator")
    async_add_entities([
        OrefreeTextSensor(coordinator),
        OrefreeStartSensor(coordinator),
        OrefreeEndSensor(coordinator),
        OrefreeLastReadSensor(coordinator),
        OrefreeNextRefreshSensor(coordinator)
    ])


class OrefreeTextSensor(CoordinatorEntity, SensorEntity):
    """OreFree text sensor."""
    
    _attr_name = "Orefree Text"
    _attr_unique_id = "orefree_text"
    _attr_icon = "mdi:text"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self):
        """Return the state of the sensor without any space characters."""
        data = self.coordinator.data or {}
        text = data.get("text", "Unknown")
        # Remove all space characters
        return text.replace(" ", "") if text != "Unknown" else text


class OrefreeStartSensor(CoordinatorEntity, SensorEntity):
    """OreFree start time sensor."""
    
    _attr_name = "Orefree Start"
    _attr_unique_id = "orefree_start"
    _attr_icon = "mdi:clock-start"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data or {}
        return data.get("start", None)


class OrefreeEndSensor(CoordinatorEntity, SensorEntity):
    """OreFree end time sensor."""
    
    _attr_name = "Orefree End"
    _attr_unique_id = "orefree_end"
    _attr_icon = "mdi:clock-end"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data or {}
        return data.get("end", None)


class OrefreeLastReadSensor(CoordinatorEntity, SensorEntity):
    """OreFree last read sensor."""
    
    _attr_name = "Orefree Last Read"
    _attr_unique_id = "orefree_last_read"
    _attr_icon = "mdi:clock-check"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data or {}
        return data.get("last_read", None)


class OrefreeNextRefreshSensor(CoordinatorEntity, SensorEntity):
    """OreFree next refresh sensor."""
    
    _attr_name = "Orefree Next Refresh"
    _attr_unique_id = "orefree_next_refresh"
    _attr_icon = "mdi:timer"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data or {}
        return data.get("next_refresh", None)

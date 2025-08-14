"""
Defines orefree binary_sensor for Home Assistant.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)



# For config flow support
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data.get("orefree_coordinator")
    async_add_entities([
        OrefreeBinarySensor(coordinator)
    ])

class OrefreeBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """OreFree binary sensor that updates every minute to check active state."""
    
    _attr_name = "Orefree Active"
    _attr_unique_id = "orefree_active"
    _attr_icon = "mdi:clock-fast"

    def __init__(self, coordinator):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._timer_handle = None
        self._is_on = False

    async def async_added_to_hass(self):
        """Called when entity is added to hass."""
        await super().async_added_to_hass()
        # Start the minute timer
        await self._schedule_next_minute_update()

    async def async_will_remove_from_hass(self):
        """Called when entity will be removed from hass."""
        await super().async_will_remove_from_hass()
        # Cancel the timer
        if self._timer_handle:
            self._timer_handle.cancel()
            self._timer_handle = None

    def _calculate_active_state(self):
        """Calculate if OreFree is currently active based on time."""
        data = self.coordinator.data or {}
        start_str = data.get("start")
        end_str = data.get("end")
        
        if not start_str or not end_str:
            return False
        
        try:
            now = datetime.now().time()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()
            return start_time <= now <= end_time
        except (ValueError, TypeError) as e:
            _LOGGER.warning(f"Failed to parse orefree time range for active state: {e}")
            return False

    async def _schedule_next_minute_update(self):
        """Schedule the next minute update."""
        if self._timer_handle:
            self._timer_handle.cancel()
        
        # Calculate seconds until next minute
        now = datetime.now()
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        delay = (next_minute - now).total_seconds()
        
        # Schedule the update
        self._timer_handle = self.hass.loop.call_later(
            delay,
            lambda: asyncio.create_task(self._minute_update())
        )
        
        _LOGGER.debug(f"OreFree binary sensor: next minute update in {delay:.1f} seconds")

    async def _minute_update(self):
        """Update the binary sensor state and schedule next update."""
        old_state = self._is_on
        self._is_on = self._calculate_active_state()
        
        if old_state != self._is_on:
            _LOGGER.info(f"OreFree active state changed: {old_state} -> {self._is_on}")
            self.async_write_ha_state()
        
        # Schedule next minute update
        await self._schedule_next_minute_update()

    @property
    def is_on(self):
        """Return true if OreFree is currently active."""
        # Always recalculate to ensure accuracy
        self._is_on = self._calculate_active_state()
        return self._is_on

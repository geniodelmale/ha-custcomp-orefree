"""
Defines orefree sensors for Home Assistant.
"""

import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
import asyncio
import aiohttp

_LOGGER = logging.getLogger(__name__)
API_URL = "http://homeassistant.local:8000/fetchHours?username=%2B393316372674&password=Cat1a.enel&type=time"

async def fetch_orefree_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            text = await response.text()
            # Expecting format "9:00 - 12:00"
            try:
                start_str, end_str = [t.strip() for t in text.split('-')]
                now = datetime.now().time()
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()
                is_on = start_time <= now <= end_time
                return {
                    "text": text,
                    "start": start_str,
                    "end": end_str,
                    "on": is_on
                }
            except Exception as e:
                _LOGGER.error(f"Failed to parse orefree time range: {e}")
                return {
                    "text": text,
                    "start": None,
                    "end": None,
                    "on": False
                }

async def create_orefree_coordinator(hass):
    import datetime
    from datetime import datetime, time

async def async_update_data():
        try:
            return await fetch_orefree_data()
        except Exception as err:
            _LOGGER.error(f"Error fetching orefree data: {err}")
            return {}

class CustomCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        return await async_update_data()

    async def _schedule_refresh(self):
        now = datetime.datetime.now()
        next_hour = (now.replace(minute=0, second=30, microsecond=0) + datetime.timedelta(hours=1))
        if now.second < 30:
            next_refresh = now.replace(second=30, microsecond=0)
        else:
            next_refresh = next_hour
        delay = (next_refresh - now).total_seconds()
        self._unsub_refresh = self.hass.loop.call_later(delay, self._handle_refresh_interval)

        coordinator = CustomCoordinator(
            hass,
            _LOGGER,
            name="orefree_coordinator",
            update_method=async_update_data,
            update_interval=None
        )
        
        await coordinator.async_config_entry_first_refresh()
        coordinator._schedule_refresh()
        return coordinator

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    coordinator = hass.data.get("orefree_coordinator")
    if coordinator is None:
        coordinator = await create_orefree_coordinator(hass)
        hass.data["orefree_coordinator"] = coordinator
    async_add_entities([
        OrefreeTextSensor(coordinator),
        OrefreeStartSensor(coordinator),
        OrefreeEndSensor(coordinator)
    ])

class OrefreeTextSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Text"
    _attr_unique_id = "orefree_text"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("text", "Unknown")

class OrefreeStartSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Start"
    _attr_unique_id = "orefree_start"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("start", None)

class OrefreeEndSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree End"
    _attr_unique_id = "orefree_end"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("end", None)

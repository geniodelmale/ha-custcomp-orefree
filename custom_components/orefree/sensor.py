"""
Defines orefree sensors for Home Assistant.
"""


import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

def build_api_url(username, password):
    from urllib.parse import quote
    return f"http://homeassistant.local:8000/fetchHours?username={quote(username)}&password={quote(password)}&type=time"


async def fetch_orefree_data(hass):
    username = hass.data.get("orefree", {}).get("username")
    password = hass.data.get("orefree", {}).get("password")
    if not username or not password:
        _LOGGER.error("Orefree username or password not set in config entry.")
        return {}
    api_url = build_api_url(username, password)
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            text = await response.text()
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
    async def async_update_data():
        try:
            new_data = await fetch_orefree_data(hass)
            # If fetch failed or returned empty/invalid, keep previous data
            if not new_data or new_data.get("text") is None:
                _LOGGER.warning("Keeping previous orefree data due to fetch error or invalid response.")
                # self.data is only available in the coordinator context
                # We'll access it in CustomCoordinator below
                return None  # Signal to use previous data
            return new_data
        except Exception as err:
            _LOGGER.error(f"Error fetching orefree data: {err}")
            return None  # Signal to use previous data

    class CustomCoordinator(DataUpdateCoordinator):
        async def _async_update_data(self):
            result = await async_update_data()
            if result is None:
                # If None, keep previous data
                return self.data if hasattr(self, "data") else {}
            return result

        async def _schedule_refresh(self):
            now = datetime.now()
            next_hour = (now.replace(minute=0, second=30, microsecond=0) + timedelta(hours=1))
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
    await coordinator._schedule_refresh()
    return coordinator



# For config flow support
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data.get("orefree_coordinator")
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

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

def build_api_url(username, password, port):
    from urllib.parse import quote
    return f"http://homeassistant.local:{port}/fetchHours?username={quote(username)}&password={quote(password)}&type=time"


async def fetch_orefree_data(hass):
    domain_data = hass.data.get("orefree", {})
    username = domain_data.get("username")
    password = domain_data.get("password")
    port = domain_data.get("port", 8000)
    if not username or not password:
        _LOGGER.error("Orefree username or password not set in config entry.")
        return {}
    api_url = build_api_url(username, password, port)
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            text = await response.text()
            try:
                start_str, end_str = [t.strip() for t in text.split('-')]
                now = datetime.now().time()
                start_time = datetime.strptime(start_str, "%H:%M").time()
                end_time = datetime.strptime(end_str, "%H:%M").time()
                is_on = start_time <= now <= end_time
                last_read = datetime.now().isoformat()
                return {
                    "text": text,
                    "start": start_str,
                    "end": end_str,
                    "on": is_on,
                    "last_read": last_read
                }
            except Exception as e:
                _LOGGER.error(f"Failed to parse orefree time range: {e}")
                return {
                    "text": text,
                    "start": None,
                    "end": None,
                    "on": False,
                    "last_read": datetime.now().isoformat()
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
            # Store next refresh time in data for sensor
            if hasattr(self, "_next_refresh"):
                if result is None:
                    # If None, keep previous data but update next_refresh
                    prev = self.data if hasattr(self, "data") else {}
                    prev = dict(prev)
                    prev["next_refresh"] = self._next_refresh
                    return prev
                result = dict(result)
                result["next_refresh"] = self._next_refresh
            return result if result is not None else (self.data if hasattr(self, "data") else {})

        async def _schedule_refresh(self):
            now = datetime.now()
            # If before 00:00:30, schedule for 00:00:30 today
            if now.hour == 0 and (now.minute < 1 or (now.minute == 0 and now.second < 30)):
                next_refresh = now.replace(hour=0, minute=0, second=30, microsecond=0)
            else:
                # Find next :45:30 after current hour, or next 00:00:30 if after 20:45:30
                if now.hour < 20 or (now.hour == 20 and (now.minute < 45 or (now.minute == 45 and now.second < 30))):
                    # Next :45:30 in current or next hour
                    if now.minute < 45 or (now.minute == 45 and now.second < 30):
                        next_refresh = now.replace(minute=45, second=30, microsecond=0)
                    else:
                        next_refresh = (now + timedelta(hours=1)).replace(minute=45, second=30, microsecond=0)
                else:
                    # After 20:45:30, schedule for next day's 00:00:30
                    tomorrow = now + timedelta(days=1)
                    next_refresh = tomorrow.replace(hour=0, minute=0, second=30, microsecond=0)
            self._next_refresh = next_refresh.isoformat()
            delay = (next_refresh - now).total_seconds()
            self._unsub_refresh = self.hass.loop.call_later(delay, self._handle_refresh_interval)

    coordinator = CustomCoordinator(
        hass,
        _LOGGER,
        name="orefree_coordinator",
        update_method=async_update_data,
        update_interval=None
    )
    # Set _next_refresh before first refresh (same logic as above)
    now = datetime.now()
    if now.hour == 0 and (now.minute < 1 or (now.minute == 0 and now.second < 30)):
        next_refresh = now.replace(hour=0, minute=0, second=30, microsecond=0)
    else:
        if now.hour < 20 or (now.hour == 20 and (now.minute < 45 or (now.minute == 45 and now.second < 30))):
            if now.minute < 45 or (now.minute == 45 and now.second < 30):
                next_refresh = now.replace(minute=45, second=30, microsecond=0)
            else:
                next_refresh = (now + timedelta(hours=1)).replace(minute=45, second=30, microsecond=0)
        else:
            tomorrow = now + timedelta(days=1)
            next_refresh = tomorrow.replace(hour=0, minute=0, second=30, microsecond=0)
    coordinator._next_refresh = next_refresh.isoformat()
    await coordinator.async_config_entry_first_refresh()
    await coordinator._schedule_refresh()
    return coordinator



# For config flow support
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data.get("orefree_coordinator")
    async_add_entities([
        OrefreeTextSensor(coordinator),
        OrefreeStartSensor(coordinator),
        OrefreeEndSensor(coordinator),
        OrefreeLastReadSensor(coordinator),
        OrefreeNextRefreshSensor(coordinator)
    ])
class OrefreeNextRefreshSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Next Refresh"
    _attr_unique_id = "orefree_next_refresh"
    _attr_icon = "mdi:timer"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("next_refresh", None)
class OrefreeLastReadSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Last Read"
    _attr_unique_id = "orefree_last_read"
    _attr_icon = "mdi:clock-check"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("last_read", None)

class OrefreeTextSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Text"
    _attr_unique_id = "orefree_text"
    _attr_icon = "mdi:text"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("text", "Unknown")

class OrefreeStartSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree Start"
    _attr_unique_id = "orefree_start"
    _attr_icon = "mdi:clock-start"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("start", None)

class OrefreeEndSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Orefree End"
    _attr_unique_id = "orefree_end"
    _attr_icon = "mdi:clock-end"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        return data.get("end", None)

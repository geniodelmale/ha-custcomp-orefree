"""
OreFree coordinator for Home Assistant.
"""

import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def build_api_url(username, password, port):
    """Build the API URL for OreFree service."""
    from urllib.parse import quote
    return f"http://homeassistant.local:{port}/fetchHours?username={quote(username)}&password={quote(password)}&type=time"


async def fetch_orefree_data(hass):
    """Fetch data from OreFree API."""
    domain_data = hass.data.get("orefree", {})
    username = domain_data.get("username")
    password = domain_data.get("password")
    port = domain_data.get("port", 8000)
    
    if not username or not password:
        _LOGGER.error("Orefree username or password not set in config entry.")
        return {}
    
    api_url = build_api_url(username, password, port)
    
    try:
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
    except Exception as e:
        _LOGGER.error(f"Failed to fetch orefree data: {e}")
        return {}


class OrefreeCoordinator(DataUpdateCoordinator):
    """OreFree data update coordinator."""

    def __init__(self, hass):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="orefree_coordinator",
            update_interval=None,
        )
        self._next_refresh = None
        self._unsub_refresh = None

    async def _async_update_data(self):
        """Update data via API endpoint."""
        try:
            new_data = await fetch_orefree_data(self.hass)
            
            # If fetch failed or returned empty/invalid, keep previous data
            if not new_data or new_data.get("text") is None:
                _LOGGER.warning("Keeping previous orefree data due to fetch error or invalid response.")
                if hasattr(self, "data") and self.data:
                    prev_data = dict(self.data)
                    if self._next_refresh:
                        prev_data["next_refresh"] = self._next_refresh
                    return prev_data
                return {}
            
            # If orefree is active, schedule next refresh for tomorrow 00:00:30
            if new_data.get("on", False):
                tomorrow = datetime.now() + timedelta(days=1)
                next_refresh = tomorrow.replace(hour=0, minute=0, second=30, microsecond=0)
                self._next_refresh = next_refresh.isoformat()
                
                # Cancel any existing scheduled update and reschedule
                if self._unsub_refresh:
                    self._unsub_refresh.cancel()
                    
                delay = (next_refresh - datetime.now()).total_seconds()
                self._unsub_refresh = self.hass.loop.call_later(
                    delay, 
                    self._handle_refresh_interval
                )
                _LOGGER.info(f"OreFree is active, next refresh scheduled for {next_refresh}")
            
            # Add next_refresh to the data
            if self._next_refresh:
                new_data["next_refresh"] = self._next_refresh
                
            return new_data
            
        except Exception as err:
            _LOGGER.error(f"Error fetching orefree data: {err}")
            # Keep previous data on error
            if hasattr(self, "data") and self.data:
                prev_data = dict(self.data)
                if self._next_refresh:
                    prev_data["next_refresh"] = self._next_refresh
                return prev_data
            return {}

    def _calculate_next_refresh_time(self):
        """Calculate the next refresh time based on current time."""
        now = datetime.now()
        
        # If before 00:00:30, schedule for 00:00:30 today
        if now.hour == 0 and (now.minute < 1 or (now.minute == 0 and now.second < 30)):
            return now.replace(hour=0, minute=0, second=30, microsecond=0)
        
        # Find next :45:30 after current hour, or next 00:00:30 if after 20:45:30
        if now.hour < 20 or (now.hour == 20 and (now.minute < 45 or (now.minute == 45 and now.second < 30))):
            # Next :45:30 in current or next hour
            if now.minute < 45 or (now.minute == 45 and now.second < 30):
                return now.replace(minute=45, second=30, microsecond=0)
            else:
                return (now + timedelta(hours=1)).replace(minute=45, second=30, microsecond=0)
        else:
            # After 20:45:30, schedule for next day's 00:00:30
            tomorrow = now + timedelta(days=1)
            return tomorrow.replace(hour=0, minute=0, second=30, microsecond=0)

    async def schedule_refresh(self):
        """Schedule the next refresh based on the refresh logic."""
        next_refresh = self._calculate_next_refresh_time()
        self._next_refresh = next_refresh.isoformat()
        
        delay = (next_refresh - datetime.now()).total_seconds()
        if delay > 0:
            self._unsub_refresh = self.hass.loop.call_later(
                delay, 
                self._handle_refresh_interval
            )
            _LOGGER.info(f"Next refresh scheduled for {next_refresh}")
        else:
            # If the calculated time is in the past, schedule for immediate refresh
            self._unsub_refresh = self.hass.loop.call_soon(self._handle_refresh_interval)
            _LOGGER.info("Scheduling immediate refresh")

    def _handle_refresh_interval(self):
        """Handle refresh interval callback."""
        asyncio.create_task(self.async_request_refresh())

    async def async_setup(self):
        """Set up the coordinator."""
        # Perform initial refresh
        await self.async_config_entry_first_refresh()
        
        # Schedule the next refresh
        await self.schedule_refresh()

    async def async_shutdown(self):
        """Clean up coordinator resources."""
        if self._unsub_refresh:
            self._unsub_refresh.cancel()
            self._unsub_refresh = None


async def create_orefree_coordinator(hass):
    """Create and set up the OreFree coordinator."""
    coordinator = OrefreeCoordinator(hass)
    await coordinator.async_setup()
    return coordinator

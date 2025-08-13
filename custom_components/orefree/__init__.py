"""
Home Assistant custom component: orefree
"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .coordinator import create_orefree_coordinator

DOMAIN = "orefree"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OreFree from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_USERNAME] = entry.data.get(CONF_USERNAME)
    hass.data[DOMAIN][CONF_PASSWORD] = entry.data.get(CONF_PASSWORD)
    hass.data[DOMAIN]["port"] = entry.data.get("port", 8000)
    _LOGGER.debug(f"Orefree config entry setup: username={entry.data.get(CONF_USERNAME)}, port={entry.data.get('port', 8000)}")

    # Create and store the coordinator once
    coordinator = await create_orefree_coordinator(hass)
    hass.data["orefree_coordinator"] = coordinator

    # Forward entry setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Clean up coordinator
    coordinator = hass.data.get("orefree_coordinator")
    if coordinator:
        await coordinator.async_shutdown()
    
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])
    
    if unload_ok:
        # Remove data
        hass.data.pop("orefree_coordinator", None)
        if DOMAIN in hass.data:
            hass.data.pop(DOMAIN)
    
    return unload_ok

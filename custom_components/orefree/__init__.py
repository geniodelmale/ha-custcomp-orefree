"""
Home Assistant custom component: orefree
"""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

DOMAIN = "orefree"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
	hass.data.setdefault(DOMAIN, {})
	hass.data[DOMAIN][CONF_USERNAME] = entry.data.get(CONF_USERNAME)
	hass.data[DOMAIN][CONF_PASSWORD] = entry.data.get(CONF_PASSWORD)
	_LOGGER.debug(f"Orefree config entry setup: username={entry.data.get(CONF_USERNAME)}")
	return True

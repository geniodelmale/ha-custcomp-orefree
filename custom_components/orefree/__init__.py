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

	# Create and store the coordinator once
	from .sensor import create_orefree_coordinator
	coordinator = await create_orefree_coordinator(hass)
	hass.data["orefree_coordinator"] = coordinator

	# Forward entry setup to platforms
	await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])
	return True


# Orefree Home Assistant Custom Component

This custom component exposes:

- `binary_sensor.orefree`: Binary sensor
- `sensor.orefree_text`: String sensor
- `sensor.orefree_start`: Datetime sensor
- `sensor.orefree_end`: Datetime sensor
- 'sensor.orefree_last_read': Datetime sensor

All data is fetched from the [OreFree Scraper Addon](https://github.com/geniodelmale/ha-addon-orefree) that should be installed before running the component.

## Installation

1. Copy the `orefree` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant
3. Add the integration via UI, and provide username and password that you use on website.

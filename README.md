# OreFree Home Assistant Custom Component

This custom component exposes:

- `binary_sensor.orefree_active`: Binary sensor updated every minute that tells you if OreFree is active or not at the moment
- `sensor.orefree_text`: String sensor containing today's OreFree hours, e.g. '10:00-13:00'
- `sensor.orefree_start`: String sensor containing start hour, e.g. '10:00'
- `sensor.orefree_end`: String sensor containing end hour, e.g. '13:00'
- `sensor.orefree_last_read`: Datetime sensor with the date of last successful API read
- `sensor.orefree_next_refresh`: Datetime sensor with the date of next API read

> [!WARNING]
> This is still **under construction**. It might be unstable and use it on your
> own risk.

> [!WARNING]
> This is the first time I write Python code and extend Home Assistant. The code might
> not be ideal. I used GitHub Copilot for 95% of the code. And it works!


## Install Add-On BEFORE installing the custom component

All data is fetched from the OreFree website using [OreFree Scraper Addon](https://github.com/geniodelmale/ha-addon-orefree) that should be installed before running the component.

## Installation using HACS

1. Open HACS
2. Click on the 3 dots in the top right corner.
3. Select "Custom repositories"
4. Add the URL to this repository.
5. Click the "ADD" button.
6. Install "OreFree integration for Home Assistant" using HACS
7. Restart Home Assistant
8. Add the integration via UI, and provide username and password that you use on website, and eventually change the port used in the Add-On.

## Manual Installation

1. Copy the `orefree` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant
3. Add the integration via UI, and provide username and password that you use on website, and eventually change the port used in the Add-On.

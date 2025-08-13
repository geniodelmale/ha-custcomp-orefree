
# Orefree Home Assistant Custom Component

This custom component exposes:

- `binary_sensor.orefree`: Binary sensor
- `sensor.orefree_text`: String sensor
- `sensor.orefree_start`: Datetime sensor
- `sensor.orefree_end`: Datetime sensor

All data is fetched from a REST API.

## Installation

1. Copy the `orefree` folder to your Home Assistant `custom_components` directory.
2. Add the integration via configuration.yaml or UI.

## Configuration Example

```yaml
# configuration.yaml
sensor:
  - platform: orefree
binary_sensor:
  - platform: orefree
```

## API

Replace the API URL in `sensor.py` and `binary_sensor.py` with your actual endpoint.

"""
Support for Xiaomi Philips Lights (LED Ball & Ceil).
"""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (PLATFORM_SCHEMA, ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light)
from homeassistant.const import (DEVICE_DEFAULT_NAME, CONF_NAME, CONF_HOST, CONF_TOKEN)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_TOKEN): vol.All(str, vol.Length(min=32, max=32)),
    vol.Optional(CONF_NAME): cv.string,
})

#REQUIREMENTS = ['python-mirobo']
REQUIREMENTS = ['https://github.com/syssi/python-mirobo/archive/'
                'ac20c00acc535bab7e1d1b8db4a4a0c542bd8557.zip#'
                'python-mirobo']

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the plug from config."""
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)

    add_devices_callback([PhilipsLight(name, host, token)], True)


class PhilipsLight(Light):
    """Representation of a Philips Light."""

    def __init__(self, name, host, token):
        """Initialize the light device."""
        self._name = name or DEVICE_DEFAULT_NAME
        self.host = host
        self.token = token

        self._brightness = 180

        self._light = None
        self._state = None

    @property
    def should_poll(self):
        """Poll the light."""
        return True

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._state is not None

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def supported_features(self):
        """Return the supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def light(self):
        """Property accessor for plug object."""
        if not self._light:
            from mirobo import Ceil
            _LOGGER.info("Initializing light with host %s token %s",
                         self.host, self.token)
            self._light = Ceil(self.host, self.token)

        return self._light

    def turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            self._brightness = int(100 * kwargs[ATTR_BRIGHTNESS] / 255)

        # TODO: Set brightness

        if self.light.on():
            self._state = True

    def turn_off(self, **kwargs):
        """Turn the light off."""
        if self.light.off():
            self._state = False

    def update(self):
        """Fetch state from the device."""
        from mirobo import DeviceException
        try:
            state = self.plug.status()
            _LOGGER.debug("Got state from light (%s): %s", self.host, state)

            self._state = state.is_on
        except DeviceException as ex:
            _LOGGER.error("Got exception while fetching the state: %s", ex)

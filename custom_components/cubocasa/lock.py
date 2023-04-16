"""Lock platform for Cubo Casa."""
import logging
from datetime import timedelta
from typing import Any, Callable, Optional

import voluptuous as vol

from homeassistant.components.lock import LockEntity, LockEntityFeature
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_NAME,
    CONF_ACCESS_TOKEN,
    CONF_NAME,
    CONF_PATH,
    CONF_URL,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

from .api import CuboClient

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(seconds=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_TOKEN): cv.string,
        vol.Optional(CONF_URL): cv.url,
    }
)

DOMAIN = "cubocasa"

async def async_setup_entry(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable
) -> None:
    """Set up the sensor platform."""
    session = async_get_clientsession(hass)
    print(config)
    client = CuboClient(session, token=config.data[CONF_ACCESS_TOKEN], url=config.data[CONF_URL])
    status, data = await client.list_devices()        
    if status != 200 or "devices" not in data:
        _LOGGER.error("Error getting devices: %s", data)
        return        
    locks = [CubocasaLock(client, device["id"]) for device in data["devices"]]
    async_add_entities(locks, update_before_add=True)

class CubocasaLock(LockEntity):
    """Representation of a Cubo Casa lock."""
    
    def __init__(self, client, device_id):
        super().__init__()
        self._client = client
        self._id = device_id
        self._name = f"Cubo {device_id}"
        self._last_action = None
        self._attr_is_locked = None
        self._attr_is_unlocking = None
        self._attr_is_jammed = None
        self._attr_changed_by = None
        # no code required
        self._attr_code_format = None
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name="Cubo Casa",
            manufacturer="Cubo Casa",
            model="Cubo Casa",
            sw_version="1.0",
            suggested_area="External",
        )     
        self._attr_supported_features = LockEntityFeature.OPEN
        self._attr_should_poll = True
    
    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name    
    
    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""
        return (
            "mdi:lock" if self.is_locked else "mdi:lock-open-variant"
        )
            
    async def async_lock(self, **kwargs: Any) -> None:
        status, data = await self._client.set_device_status(self._id, "close")
        if status != 200 or data["status"] != True:
            _LOGGER.error("Error locking device: %s", data)
        self._last_action = "close"
        self._attr_is_locking = True
        
    async def async_unlock(self, **kwargs: Any) -> None:
        status, data = await self._client.set_device_status(self._id, "open")
        if status != 200 or data["status"] != True:
            _LOGGER.error("Error unlocking device: %s", data)
        self._last_action = "open"
        self._attr_is_unlocking = True

    async def async_update(self) -> None:
        status, data = await self._client.get_device_status(self._id)
        if status != 200 or data["status"] != True:
            _LOGGER.error("Error unlocking device: %s", data)
            return
        if "deviceStatus" not in data:
            _LOGGER.error("Error getting device status: %s", data)
            return        
        if "online" not in data:
            _LOGGER.error("Error getting device online status: %s", data)
            return 
        
        self._attr_is_locked = data["deviceStatus"] == "close"

        if self._last_action and self._last_action == data["deviceStatus"]:
            self._last_action = None
            self._attr_is_locking = False
            self._attr_is_unlocking = False 
            
        self._attr_available = (data["online"] == 1)        
        _LOGGER.debug(f"Cubo {self._id} status: %s", data)
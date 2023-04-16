"""Adds config flow for Cubo Casa."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import CuboClient
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_URL, CONF_SCAN_INTERVAL
from .const import DOMAIN
from .const import PLATFORMS

_LOGGER = logging.getLogger(__name__)

class CubocasaFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for cubocasa."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_credentials(
                user_input[CONF_ACCESS_TOKEN], user_input[CONF_URL]
            )
            if valid:
                return self.async_create_entry(
                    title="Logged in Cubo Casa", data=user_input
                )
            else:
                self._errors["base"] = "auth"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return CubocasaOptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCESS_TOKEN): str, 
                    vol.Required(CONF_URL, default="https://iot.cubo.casa"): str,
                    vol.Required(CONF_SCAN_INTERVAL, default=5): int
                }
            ),
            errors=self._errors,
        )
        
    async def _test_credentials(self, token, url):
        """Return true if credentials is valid."""
        try:
            session = async_create_clientsession(self.hass)
            client = CuboClient(session, token=token, url=url)
            status, data = await client.list_devices()
            if status == 403:
                return False
            if status == 200:
                return True            
            _LOGGER.error("Unknown case while checking credentials: %s", data)
        except Exception:  # pylint: disable=broad-except
            pass        
        return False


class CubocasaOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for cubocasa."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title="Cubo Casa Updated", data=self.options
        )

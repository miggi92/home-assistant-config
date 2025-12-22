from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN

class ElGordoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for El Gordo."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Initialer Setup-Dialog."""
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            return self.async_create_entry(title="El Gordo", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("tickets", default="27133"): str,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Verknüpft den Options-Dialog für nachträgliche Änderungen."""
        return ElGordoOptionsFlowHandler(config_entry)

class ElGordoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handler für das Menü unter 'Konfigurieren'."""
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Dialog zum Ändern der Ticket-Liste."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Aktuelle Liste aus den Optionen oder den Initial-Daten laden
        current_tickets = self.config_entry.options.get(
            "tickets", self.config_entry.data.get("tickets", "")
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("tickets", default=current_tickets): str,
            })
        )
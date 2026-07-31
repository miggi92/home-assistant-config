import re

from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import (
    DEFAULT_TICKET_TYPE,
    DOMAIN,
    TICKET_TYPE_BILLETE,
    TICKET_TYPE_DECIMO,
)


def validate_tickets(value):
    """Validate and normalize a comma-separated list of ticket numbers."""
    tickets = [ticket.strip() for ticket in value.split(",") if ticket.strip()]
    if not tickets or any(not re.fullmatch(r"\d{5}", ticket) for ticket in tickets):
        raise vol.Invalid("Ticket numbers must contain exactly five digits")
    return ",".join(dict.fromkeys(tickets))


def ticket_schema(tickets, ticket_type):
    """Build the shared config and options schema."""
    return vol.Schema(
        {
            vol.Required("tickets", default=tickets): vol.All(str, validate_tickets),
            vol.Required("ticket_type", default=ticket_type): vol.In(
                {
                    TICKET_TYPE_DECIMO: "Décimo",
                    TICKET_TYPE_BILLETE: "Billete",
                }
            ),
        }
    )

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
            data_schema=ticket_schema("27133", DEFAULT_TICKET_TYPE),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Verknüpft den Options-Dialog für nachträgliche Änderungen."""
        return ElGordoOptionsFlowHandler()

class ElGordoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handler für das Menü unter 'Konfigurieren'."""

    async def async_step_init(self, user_input=None):
        """Dialog zum Ändern der Ticket-Liste."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Aktuelle Liste aus den Optionen oder den Initial-Daten laden
        current_tickets = self.config_entry.options.get(
            "tickets", self.config_entry.data.get("tickets", "")
        )
        current_ticket_type = self.config_entry.options.get(
            "ticket_type",
            self.config_entry.data.get("ticket_type", DEFAULT_TICKET_TYPE),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=ticket_schema(current_tickets, current_ticket_type),
        )
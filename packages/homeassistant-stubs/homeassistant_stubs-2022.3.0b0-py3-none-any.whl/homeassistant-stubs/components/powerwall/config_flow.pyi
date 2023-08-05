from .const import DOMAIN as DOMAIN
from homeassistant import config_entries as config_entries, core as core, exceptions as exceptions
from homeassistant.components import dhcp as dhcp
from homeassistant.const import CONF_IP_ADDRESS as CONF_IP_ADDRESS, CONF_PASSWORD as CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult as FlowResult
from homeassistant.util.network import is_ip_address as is_ip_address
from tesla_powerwall import Powerwall, SiteInfo as SiteInfo
from typing import Any

_LOGGER: Any

def _login_and_fetch_site_info(power_wall: Powerwall, password: str) -> tuple[SiteInfo, str]: ...
async def validate_input(hass: core.HomeAssistant, data: dict[str, str]) -> dict[str, str]: ...

class ConfigFlow(config_entries.ConfigFlow):
    VERSION: int
    ip_address: Any
    title: Any
    reauth_entry: Any
    def __init__(self) -> None: ...
    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult: ...
    async def _async_try_connect(self, user_input: dict[str, Any]) -> tuple[Union[dict[str, Any], None], Union[dict[str, str], None]]: ...
    async def async_step_confirm_discovery(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_user(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_reauth_confirm(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_reauth(self, data: dict[str, str]) -> FlowResult: ...

class WrongVersion(exceptions.HomeAssistantError): ...

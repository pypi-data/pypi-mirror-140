from .typing import DiscoveryInfoType as DiscoveryInfoType, UNDEFINED as UNDEFINED, UndefinedType as UndefinedType
from collections.abc import Awaitable, Callable
from homeassistant import config_entries as config_entries
from homeassistant.components import dhcp as dhcp, mqtt as mqtt, ssdp as ssdp, zeroconf as zeroconf
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.data_entry_flow import FlowResult as FlowResult
from typing import Any, TypeVar

_R = TypeVar('_R', bound='Awaitable[bool] | bool')
DiscoveryFunctionType = Callable[[HomeAssistant], _R]
_LOGGER: Any

class DiscoveryFlowHandler(config_entries.ConfigFlow):
    VERSION: int
    _domain: Any
    _title: Any
    _discovery_function: Any
    def __init__(self, domain: str, title: str, discovery_function: DiscoveryFunctionType[_R]) -> None: ...
    async def async_step_user(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_confirm(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_discovery(self, discovery_info: DiscoveryInfoType) -> FlowResult: ...
    async def async_step_dhcp(self, discovery_info: dhcp.DhcpServiceInfo) -> FlowResult: ...
    async def async_step_homekit(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult: ...
    async def async_step_mqtt(self, discovery_info: mqtt.MqttServiceInfo) -> FlowResult: ...
    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult: ...
    async def async_step_ssdp(self, discovery_info: ssdp.SsdpServiceInfo) -> FlowResult: ...
    async def async_step_import(self, _: Union[dict[str, Any], None]) -> FlowResult: ...

def register_discovery_flow(domain: str, title: str, discovery_function: DiscoveryFunctionType[Union[Awaitable[bool], bool]], connection_class: Union[str, UndefinedType] = ...) -> None: ...

class WebhookFlowHandler(config_entries.ConfigFlow):
    VERSION: int
    _domain: Any
    _title: Any
    _description_placeholder: Any
    _allow_multiple: Any
    def __init__(self, domain: str, title: str, description_placeholder: dict, allow_multiple: bool) -> None: ...
    async def async_step_user(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...

def register_webhook_flow(domain: str, title: str, description_placeholder: dict, allow_multiple: bool = ...) -> None: ...
async def webhook_async_remove_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> None: ...

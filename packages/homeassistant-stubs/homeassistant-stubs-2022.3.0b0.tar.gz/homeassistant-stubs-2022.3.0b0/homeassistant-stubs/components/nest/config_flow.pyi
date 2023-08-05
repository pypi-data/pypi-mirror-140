import logging
from . import api as api, auth as auth
from .const import CONF_CLOUD_PROJECT_ID as CONF_CLOUD_PROJECT_ID, CONF_PROJECT_ID as CONF_PROJECT_ID, CONF_SUBSCRIBER_ID as CONF_SUBSCRIBER_ID, DATA_NEST_CONFIG as DATA_NEST_CONFIG, DATA_SDM as DATA_SDM, DOMAIN as DOMAIN, OOB_REDIRECT_URI as OOB_REDIRECT_URI, SDM_SCOPES as SDM_SCOPES
from collections.abc import Iterable
from enum import Enum
from google_nest_sdm.structure import Structure as Structure
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import CONF_CLIENT_ID as CONF_CLIENT_ID, CONF_CLIENT_SECRET as CONF_CLIENT_SECRET
from homeassistant.core import HomeAssistant as HomeAssistant, callback as callback
from homeassistant.data_entry_flow import FlowResult as FlowResult
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError
from homeassistant.helpers import config_entry_oauth2_flow as config_entry_oauth2_flow
from homeassistant.helpers.typing import ConfigType as ConfigType
from homeassistant.util import get_random_string as get_random_string
from homeassistant.util.json import load_json as load_json
from typing import Any

DATA_FLOW_IMPL: str
SUBSCRIPTION_FORMAT: str
SUBSCRIPTION_RAND_LENGTH: int
CLOUD_CONSOLE_URL: str
_LOGGER: Any

class ConfigMode(Enum):
    SDM: int
    LEGACY: int

def get_config_mode(hass: HomeAssistant) -> ConfigMode: ...
def _generate_subscription_id(cloud_project_id: str) -> str: ...
def register_flow_implementation(hass: HomeAssistant, domain: str, name: str, gen_authorize_url: str, convert_code: str) -> None: ...
def register_flow_implementation_from_config(hass: HomeAssistant, config: ConfigType) -> None: ...

class NestAuthError(HomeAssistantError): ...
class CodeInvalid(NestAuthError): ...
class UnexpectedStateError(HomeAssistantError): ...

def generate_config_title(structures: Iterable[Structure]) -> Union[str, None]: ...

class NestFlowHandler(config_entry_oauth2_flow.AbstractOAuth2FlowHandler):
    DOMAIN: Any
    VERSION: int
    _reauth: bool
    _data: Any
    _structure_config_title: Any
    def __init__(self) -> None: ...
    @property
    def config_mode(self) -> ConfigMode: ...
    @property
    def logger(self) -> logging.Logger: ...
    @property
    def extra_authorize_data(self) -> dict[str, str]: ...
    async def async_oauth_create_entry(self, data: dict[str, Any]) -> FlowResult: ...
    async def async_step_reauth(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_reauth_confirm(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_user(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    external_data: Any
    async def async_step_auth(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    def _configure_pubsub(self) -> bool: ...
    async def async_step_pubsub(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_finish(self, data: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    flow_impl: Any
    async def async_step_init(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_link(self, user_input: Union[dict[str, Any], None] = ...) -> FlowResult: ...
    async def async_step_import(self, info: dict[str, Any]) -> FlowResult: ...
    def _entry_from_tokens(self, title: str, flow: dict[str, Any], tokens: Union[list[Any], dict[Any, Any]]) -> FlowResult: ...

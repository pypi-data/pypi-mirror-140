from .const import CONTROLLER_MODES as CONTROLLER_MODES, CURRENT_HVAC_ACTIONS as CURRENT_HVAC_ACTIONS, DATA_KNX_CONFIG as DATA_KNX_CONFIG, DOMAIN as DOMAIN, PRESET_MODES as PRESET_MODES
from .knx_entity import KnxEntity as KnxEntity
from .schema import ClimateSchema as ClimateSchema
from homeassistant import config_entries as config_entries
from homeassistant.components.climate import ClimateEntity as ClimateEntity
from homeassistant.components.climate.const import CURRENT_HVAC_IDLE as CURRENT_HVAC_IDLE, CURRENT_HVAC_OFF as CURRENT_HVAC_OFF, HVAC_MODE_OFF as HVAC_MODE_OFF, PRESET_AWAY as PRESET_AWAY, SUPPORT_PRESET_MODE as SUPPORT_PRESET_MODE, SUPPORT_TARGET_TEMPERATURE as SUPPORT_TARGET_TEMPERATURE
from homeassistant.const import ATTR_TEMPERATURE as ATTR_TEMPERATURE, CONF_ENTITY_CATEGORY as CONF_ENTITY_CATEGORY, CONF_NAME as CONF_NAME, Platform as Platform, TEMP_CELSIUS as TEMP_CELSIUS
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType as ConfigType
from typing import Any
from xknx import XKNX as XKNX
from xknx.devices import Climate as XknxClimate

ATTR_COMMAND_VALUE: str
CONTROLLER_MODES_INV: Any
PRESET_MODES_INV: Any

async def async_setup_entry(hass: HomeAssistant, config_entry: config_entries.ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...
def _create_climate(xknx: XKNX, config: ConfigType) -> XknxClimate: ...

class KNXClimate(KnxEntity, ClimateEntity):
    _device: XknxClimate
    _attr_temperature_unit: Any
    _attr_entity_category: Any
    _attr_supported_features: Any
    _attr_target_temperature_step: Any
    _attr_unique_id: Any
    default_hvac_mode: Any
    def __init__(self, xknx: XKNX, config: ConfigType) -> None: ...
    async def async_update(self) -> None: ...
    @property
    def current_temperature(self) -> Union[float, None]: ...
    @property
    def target_temperature(self) -> Union[float, None]: ...
    @property
    def min_temp(self) -> float: ...
    @property
    def max_temp(self) -> float: ...
    async def async_set_temperature(self, **kwargs: Any) -> None: ...
    @property
    def hvac_mode(self) -> str: ...
    @property
    def hvac_modes(self) -> list[str]: ...
    @property
    def hvac_action(self) -> Union[str, None]: ...
    async def async_set_hvac_mode(self, hvac_mode: str) -> None: ...
    @property
    def preset_mode(self) -> Union[str, None]: ...
    @property
    def preset_modes(self) -> Union[list[str], None]: ...
    async def async_set_preset_mode(self, preset_mode: str) -> None: ...
    @property
    def extra_state_attributes(self) -> Union[dict[str, Any], None]: ...
    async def async_added_to_hass(self) -> None: ...
    async def async_will_remove_from_hass(self) -> None: ...

from . import EsphomeEntity as EsphomeEntity, esphome_state_property as esphome_state_property, platform_async_setup_entry as platform_async_setup_entry
from aioesphomeapi import LockEntityState, LockInfo
from homeassistant.components.lock import LockEntity as LockEntity, SUPPORT_OPEN as SUPPORT_OPEN
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import ATTR_CODE as ATTR_CODE
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from typing import Any

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...

class EsphomeLock(EsphomeEntity[LockInfo, LockEntityState], LockEntity):
    @property
    def assumed_state(self) -> bool: ...
    @property
    def supported_features(self) -> int: ...
    @property
    def code_format(self) -> Union[str, None]: ...
    def is_locked(self) -> Union[bool, None]: ...
    def is_locking(self) -> Union[bool, None]: ...
    def is_unlocking(self) -> Union[bool, None]: ...
    def is_jammed(self) -> Union[bool, None]: ...
    async def async_lock(self, **kwargs: Any) -> None: ...
    async def async_unlock(self, **kwargs: Any) -> None: ...
    async def async_open(self, **kwargs: Any) -> None: ...

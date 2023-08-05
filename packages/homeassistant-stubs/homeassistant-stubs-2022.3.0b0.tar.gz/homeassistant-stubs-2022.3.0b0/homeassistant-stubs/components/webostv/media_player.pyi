from . import WebOsClientWrapper as WebOsClientWrapper
from .const import ATTR_PAYLOAD as ATTR_PAYLOAD, ATTR_SOUND_OUTPUT as ATTR_SOUND_OUTPUT, CONF_SOURCES as CONF_SOURCES, DATA_CONFIG_ENTRY as DATA_CONFIG_ENTRY, DOMAIN as DOMAIN, LIVE_TV_APP_ID as LIVE_TV_APP_ID, WEBOSTV_EXCEPTIONS as WEBOSTV_EXCEPTIONS
from aiowebostv import WebOsClient as WebOsClient
from collections.abc import Awaitable as Awaitable, Callable as Callable, Coroutine
from homeassistant import util as util
from homeassistant.components.media_player import MediaPlayerDeviceClass as MediaPlayerDeviceClass, MediaPlayerEntity as MediaPlayerEntity
from homeassistant.components.media_player.const import MEDIA_TYPE_CHANNEL as MEDIA_TYPE_CHANNEL, SUPPORT_NEXT_TRACK as SUPPORT_NEXT_TRACK, SUPPORT_PAUSE as SUPPORT_PAUSE, SUPPORT_PLAY as SUPPORT_PLAY, SUPPORT_PLAY_MEDIA as SUPPORT_PLAY_MEDIA, SUPPORT_PREVIOUS_TRACK as SUPPORT_PREVIOUS_TRACK, SUPPORT_SELECT_SOURCE as SUPPORT_SELECT_SOURCE, SUPPORT_STOP as SUPPORT_STOP, SUPPORT_TURN_OFF as SUPPORT_TURN_OFF, SUPPORT_TURN_ON as SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE as SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET as SUPPORT_VOLUME_SET, SUPPORT_VOLUME_STEP as SUPPORT_VOLUME_STEP
from homeassistant.config_entries import ConfigEntry as ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID as ATTR_ENTITY_ID, ATTR_SUPPORTED_FEATURES as ATTR_SUPPORTED_FEATURES, ENTITY_MATCH_ALL as ENTITY_MATCH_ALL, ENTITY_MATCH_NONE as ENTITY_MATCH_NONE, STATE_OFF as STATE_OFF, STATE_ON as STATE_ON
from homeassistant.core import HomeAssistant as HomeAssistant
from homeassistant.exceptions import HomeAssistantError as HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect as async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo as DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback as AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity as RestoreEntity
from typing import Any, TypeVar
from typing_extensions import Concatenate as Concatenate

_LOGGER: Any
SUPPORT_WEBOSTV: Any
SUPPORT_WEBOSTV_VOLUME: Any
MIN_TIME_BETWEEN_SCANS: Any
MIN_TIME_BETWEEN_FORCED_SCANS: Any
SCAN_INTERVAL: Any

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None: ...
_T = TypeVar('_T', bound='LgWebOSMediaPlayerEntity')
_P: Any

def cmd(func: Callable[Concatenate[_T, _P], Awaitable[None]]) -> Callable[Concatenate[_T, _P], Coroutine[Any, Any, None]]: ...

class LgWebOSMediaPlayerEntity(RestoreEntity, MediaPlayerEntity):
    _attr_device_class: Any
    _wrapper: Any
    _client: Any
    _attr_assumed_state: bool
    _attr_name: Any
    _attr_unique_id: Any
    _sources: Any
    _paused: bool
    _current_source: Any
    _source_list: Any
    _supported_features: int
    def __init__(self, wrapper: WebOsClientWrapper, name: str, sources: Union[list[str], None], unique_id: str) -> None: ...
    async def async_added_to_hass(self) -> None: ...
    async def async_will_remove_from_hass(self) -> None: ...
    async def async_signal_handler(self, data: dict[str, Any]) -> None: ...
    async def async_handle_state_update(self, _client: WebOsClient) -> None: ...
    _attr_state: Any
    _attr_is_volume_muted: Any
    _attr_volume_level: Any
    _attr_source: Any
    _attr_source_list: Any
    _attr_media_content_type: Any
    _attr_media_title: Any
    _attr_media_image_url: Any
    _attr_device_info: Any
    _attr_extra_state_attributes: Any
    def _update_states(self) -> None: ...
    def _update_sources(self) -> None: ...
    async def async_update(self) -> None: ...
    @property
    def supported_features(self) -> int: ...
    async def async_turn_off(self) -> None: ...
    async def async_turn_on(self) -> None: ...
    async def async_volume_up(self) -> None: ...
    async def async_volume_down(self) -> None: ...
    async def async_set_volume_level(self, volume: int) -> None: ...
    async def async_mute_volume(self, mute: bool) -> None: ...
    async def async_select_sound_output(self, sound_output: str) -> None: ...
    async def async_media_play_pause(self) -> None: ...
    async def async_select_source(self, source: str) -> None: ...
    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any) -> None: ...
    async def async_media_play(self) -> None: ...
    async def async_media_pause(self) -> None: ...
    async def async_media_stop(self) -> None: ...
    async def async_media_next_track(self) -> None: ...
    async def async_media_previous_track(self) -> None: ...
    async def async_button(self, button: str) -> None: ...
    async def async_command(self, command: str, **kwargs: Any) -> None: ...

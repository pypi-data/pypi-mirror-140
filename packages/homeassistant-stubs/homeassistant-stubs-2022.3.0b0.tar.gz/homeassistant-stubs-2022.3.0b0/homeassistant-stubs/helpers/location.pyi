from collections.abc import Iterable
from homeassistant.const import ATTR_LATITUDE as ATTR_LATITUDE, ATTR_LONGITUDE as ATTR_LONGITUDE
from homeassistant.core import HomeAssistant as HomeAssistant, State as State
from typing import Any

_LOGGER: Any

def has_location(state: State) -> bool: ...
def closest(latitude: float, longitude: float, states: Iterable[State]) -> Union[State, None]: ...
def find_coordinates(hass: HomeAssistant, name: str, recursion_history: Union[list, None] = ...) -> Union[str, None]: ...
def resolve_zone(hass: HomeAssistant, zone_name: str) -> Union[str, None]: ...
def _get_location_from_attributes(entity_state: State) -> str: ...

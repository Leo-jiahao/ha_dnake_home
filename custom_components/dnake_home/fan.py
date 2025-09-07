import logging
from typing import Any, Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import ranged_value_to_percentage, percentage_to_ranged_value

from .core.assistant import assistant
from .core.constant import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

# Mapping for fan speeds (0: low, 1: medium, 2: high)
_air_fresh_fan_table = {
    0: "low",
    1: "medium",
    2: "high",
}

# Number of speed levels
SPEED_COUNT = len(_air_fresh_fan_table)  # 3 speeds: low, medium, high


def load_fans(device_list):
    """Load fresh air fan devices from the device list."""
    fans = [
        DnakeAirFreshFan(device) for device in device_list if device.get("ty") == 16926
    ]
    _LOGGER.info(f"Found fresh air fan devices: {len(fans)}")
    assistant.entries["fan"] = fans


def update_fans_state(states):
    """Update the state of all fan entities based on received state data."""
    fans = assistant.entries.get("fan", [])
    for fan in fans:
        state = next((state for state in states if fan.is_hint_state(state)), None)
        if state:
            fan.update_state(state)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up fan entities from a config entry."""
    fan_list = assistant.entries.get("fan", [])
    if fan_list:
        async_add_entities(fan_list)


class DnakeAirFreshFan(FanEntity):
    """Representation of a Dnake fresh air fan entity."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = SPEED_COUNT  # 3 speed levels (low, medium, high)
    _enable_turn_on_off_backwards_compatibility = False  # Disable deprecated turn on/off compatibility

    def __init__(self, device):
        """Initialize the fan entity."""
        self._name = device.get("na")
        self._dev_no = device.get("nm")
        self._dev_ch = device.get("ch")
        self._dev_type = device.get("ty")
        self._is_on = device.get("powerOn", 0) == 1
        self._attr_percentage = self._calculate_percentage(device.get("speed", 0))
        self._error_code = device.get("errorCode", 0)
        self._pm25 = device.get("pm25", 0)

    def is_hint_state(self, state):
        """Check if the state corresponds to this fan."""
        return (
            state.get("devType") == self._dev_type
            and state.get("devNo") == self._dev_no
            and state.get("devCh") == self._dev_ch
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the fan."""
        return f"dnake_air_fresh_fan_{self._dev_no}_{self._dev_ch}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the fan."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"air_fresh_fan_{self._dev_no}_{self._dev_ch}")},
            name=self._name,
            manufacturer=MANUFACTURER,
            model="Fresh Air Fan",
            via_device=(DOMAIN, "gateway"),
        )

    @property
    def name(self) -> str:
        """Return the name of the fan."""
        return self._name

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the fan is on."""
        return self._is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed as a percentage."""
        return self._attr_percentage

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "error_code": self._error_code,
            "pm25": self._pm25,
        }

    def _calculate_percentage(self, speed: int) -> Optional[int]:
        """Convert speed index to percentage."""
        if speed not in _air_fresh_fan_table:
            return None
        speed_range = (0, self._attr_speed_count - 1)  # e.g., (0, 2) for low, medium, high
        return round(ranged_value_to_percentage(speed_range, speed))

    def _percentage_to_speed(self, percentage: int) -> int:
        """Convert percentage to speed index."""
        speed_range = (0, self._attr_speed_count - 1)  # e.g., (0, 2) for low, medium, high
        speed_index = round(percentage_to_ranged_value(speed_range, percentage))
        return max(0, min(speed_index, self._attr_speed_count - 1))

    async def async_turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        if not self._is_on:
            is_success = await self.hass.async_add_executor_job(
                assistant.set_air_fresh_power, self._dev_no, self._dev_ch, True
            )
            if is_success:
                self._is_on = True
                # Default to lowest speed (0 = low) if no percentage is specified
                if percentage is None:
                    percentage = self._calculate_percentage(0)

        if percentage is not None:
            await self.async_set_percentage(percentage)

        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fan."""
        is_success = await self.hass.async_add_executor_job(
            assistant.set_air_fresh_power, self._dev_no, self._dev_ch, False
        )
        if is_success:
            self._is_on = False
            self._attr_percentage = None  # No speed when off
            self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan as a percentage."""
        speed_index = self._percentage_to_speed(percentage)
        is_success = await self.hass.async_add_executor_job(
            assistant.set_air_fresh_speed, self._dev_no, self._dev_ch, speed_index
        )
        if is_success:
            self._attr_percentage = self._calculate_percentage(speed_index)
            self._is_on = True  # Ensure fan is marked as on when setting speed
            self.async_write_ha_state()

    def update_state(self, state: dict) -> None:
        """Update the fan's state based on received data."""
        self._is_on = state.get("powerOn", 0) == 1
        speed = state.get("speed", 0)
        self._attr_percentage = self._calculate_percentage(speed) if self._is_on else None
        self._error_code = state.get("errorCode", 0)
        self._pm25 = state.get("pm25", 0)
        self.async_write_ha_state()
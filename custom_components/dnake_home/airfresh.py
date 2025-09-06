import asyncio
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    FAN_LOW,
    FAN_MIDDLE,
    FAN_HIGH,
    ClimateEntityFeature,
)
from homeassistant.const import UnitOfMass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .core.assistant import assistant
from .core.constant import DOMAIN, MANUFACTURER
from .core.utils import get_key_by_value

_LOGGER = logging.getLogger(__name__)

# 风速表
_air_fresh_fan_table = {1: FAN_LOW, 2: FAN_MIDDLE, 3: FAN_HIGH}

# 配置加载和实体更新
def load_air_freshs(device_list):
    air_fresh_devices = [
        DnakeAirFresh(device) for device in device_list if device.get("ty") == 16926
    ]
    _LOGGER.info(f"find air_fresh num: {len(air_fresh_devices)}")
    assistant.entries["air_fresh"] = air_fresh_devices

def update_air_fresh_state(states):
    air_fresh_devices = assistant.entries["air_fresh"]
    for device in air_fresh_devices:
        state = next((state for state in states if device.is_hint_state(state)), None)
        if state:
            device.update_state(state)

async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
):
    air_fresh_list = assistant.entries["air_fresh"]
    if air_fresh_list:
        async_add_entities(air_fresh_list)

# 新风设备类
class DnakeAirFresh(ClimateEntity):

    def __init__(self, device):
        self._name = device.get("na")
        self._dev_no = device.get("nm")
        self._dev_ch = device.get("ch")
        self._dev_type = device.get("ty")
        self._is_on = device.get("powerOn", 0) == 1
        self._current_pm25 = device.get("pm25", 0)
        self._fan_mode = _air_fresh_fan_table.get(device.get("speed"), FAN_LOW)

    def is_hint_state(self, state):
        return state.get('devType') == self._dev_type and state.get("devNo") == self._dev_no and state.get(
            "devCh") == self._dev_ch
    
    @property
    def unique_id(self):
        return f"dnake_air_fresh_{self._dev_no}_{self._dev_ch}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"air_fresh_{self._dev_no}_{self._dev_ch}")},
            name=self._name,
            manufacturer=MANUFACTURER,
            model="新风控制",
            via_device=(DOMAIN, "gateway"),
        )

    @property
    def supported_features(self):
        return (
            ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.FAN_MODE
        )
    
    @property
    def temperature_unit(self):
        return UnitOfMass.MICROGRAMS

    @property
    def current_temperature(self):
        return self._current_pm25
    
    @property
    def name(self):
        return self._name

    @property
    def fan_mode(self):
        return self._fan_mode

    @property
    def fan_modes(self):
        return list(_air_fresh_fan_table.values())

    @property
    def should_poll(self):
        return False

    async def async_turn_on(self, **kwargs):
        """开启新风设备"""
        await self._async_turn_to(True)

    async def async_turn_off(self, **kwargs):
        """关闭新风设备"""
        await self._async_turn_to(False)

    async def async_set_fan_mode(self, fan_mode):
        """设置新风的风速"""
        is_success = await self.hass.async_add_executor_job(
            assistant.set_air_fresh_speed,
            self._dev_no,
            self._dev_ch,
            get_key_by_value(_air_fresh_fan_table, fan_mode, 0),
        )
        if is_success:
            self._fan_mode = fan_mode
            self.async_write_ha_state()

    async def _async_turn_to(self, is_open: bool):
        """开关新风"""
        is_success = await self.hass.async_add_executor_job(
            assistant.set_air_fresh_power,
            self._dev_no,
            self._dev_ch,
            is_open,
        )
        if is_success:
            self._is_on = is_open
            self.async_write_ha_state()

    def update_state(self, state):
        """更新新风状态"""
        self._is_on = state.get("powerOn", 0) == 1
        self._current_pm25 = state.get("pm25", 0)
        self._fan_mode = _air_fresh_fan_table.get(state.get("speed"), FAN_LOW)
        self.async_write_ha_state()


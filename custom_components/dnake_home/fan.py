import logging
from homeassistant.components.fan import FanEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.assistant import assistant
from .core.constant import DOMAIN, MANUFACTURER
from .core.utils import get_key_by_value

_LOGGER = logging.getLogger(__name__)

# 自定义常量，替代 fan.const
FAN_LOW = "low"
FAN_MIDDLE = "medium"
FAN_HIGH = "high"
SUPPORT_SET_SPEED = 1  # 表示支持调速

# 映射表
_fan_speed_table = {0: FAN_LOW, 1: FAN_MIDDLE, 2: FAN_HIGH}
_fan_speed_reverse = {v: k for k, v in _fan_speed_table.items()}


def load_fans(device_list):
    """加载新风设备"""
    fans = [DnakeFreshAir(device) for device in device_list if device.get("ty") == 16926]
    _LOGGER.info(f"find fresh_air num: {len(fans)}")
    assistant.entries["fan"] = fans


def update_fans_state(states):
    """更新新风设备状态"""
    fans = assistant.entries["fan"]
    for fan in fans:
        state = next((s for s in states if fan.is_hint_state(s)), None)
        if state:
            fan.update_state(state)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    fan_list = assistant.entries.get("fan")
    if fan_list:
        async_add_entities(fan_list)


class DnakeFreshAir(FanEntity):
    """新风系统实体"""

    def __init__(self, device):
        self._name = device.get("na")
        self._dev_no = device.get("nm")
        self._dev_ch = device.get("ch")
        self._dev_type = device.get("ty")
        self._is_on = device.get("powerOn", 0) == 1
        self._fan_mode = _fan_speed_table.get(device.get("speed"), FAN_LOW)

    def is_hint_state(self, state):
        return (
            state.get("devType") == self._dev_type
            and state.get("devNo") == self._dev_no
            and state.get("devCh") == self._dev_ch
        )

    @property
    def unique_id(self):
        return f"dnake_fresh_air_{self._dev_no}_{self._dev_ch}"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, f"fresh_air_{self._dev_no}_{self._dev_ch}")},
            name=self._name,
            manufacturer=MANUFACTURER,
            model="新风控制",
            via_device=(DOMAIN, "gateway"),
        )

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    @property
    def speed(self):
        return self._fan_mode

    @property
    def speed_count(self):
        return 3

    @property
    def speed_list(self):
        return list(_fan_speed_table.values())

    @property
    def supported_features(self):
        return SUPPORT_SET_SPEED

    async def async_turn_on(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            assistant.set_fan_power, self._dev_no, self._dev_ch, True
        )
        if success:
            self._is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        success = await self.hass.async_add_executor_job(
            assistant.set_fan_power, self._dev_no, self._dev_ch, False
        )
        if success:
            self._is_on = False
            self.async_write_ha_state()

    async def async_set_speed(self, speed):
        speed_index = get_key_by_value(_fan_speed_table, speed, 0)
        success = await self.hass.async_add_executor_job(
            assistant.set_fan_speed, self._dev_no, self._dev_ch, speed_index
        )
        if success:
            self._fan_mode = speed
            self.async_write_ha_state()

    def update_state(self, state):
        self._is_on = state.get("powerOn", 0) == 1
        self._fan_mode = _fan_speed_table.get(state.get("speed"), FAN_LOW)
        self.async_write_ha_state()

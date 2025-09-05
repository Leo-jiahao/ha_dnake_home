from enum import Enum

TITLE = "Dnake Home"
DOMAIN = "dnake_home"
MANUFACTURER = "Dnake"


class Action(Enum):
    # 获取单设备状态
    ReadDev = "readDev"
    # 获取所有设备状态
    ReadAllDevState = "readAllDevState"
    # 控制设备
    CtrlDev = "ctrlDev"


class Cmd(Enum):
    # 灯.etc
    On = "on"
    Off = "off"
    # 窗帘.etc
    Stop = "stop"
    Level = "level"
    # 空调
    AirCondition = "airCondition"
    # 新风
    Fan = "fan"       # 新增，用于新风系统



class Power(Enum):
    On = "powerOn"
    Off = "powerOff"


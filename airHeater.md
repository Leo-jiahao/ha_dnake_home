
{
  "action": "readDev",
  "devNo": 21,
  "devCh": 3
}

{"powerOn":0,"tempIndoor":28,"tempDesire":20,"panelLocked":0,"errorCode":8,"valve":0,"highTempProtect":40,"lowTempProtectEnable":0,"uuid":"C93A4F99BC796610A50984E6B7CFEACF","result":"ok"}

<!-- 开 -->
{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "powerOn",
  "devNo": 21,
  "devCh": 3
}

{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "powerOff",
  "devNo": 21,
  "devCh": 3
}

<!-- 正确 -->
{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "setTemp",
  "param": 25,
  "devNo": 21,
  "devCh": 3
}

<!-- 正确 -->
{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "setHighTempProtect",
  "param": 40,
  "devNo": 21,
  "devCh": 3
}

{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "enableLowTempProtect",
  "param": 1,
  "devNo": 21,
  "devCh": 3
}

{
  "action": "ctrlDev",
  "cmd": "airHeater",
  "oper": "enableLowTempProtect",
  "param": 0,
  "devNo": 21,
  "devCh": 3
}


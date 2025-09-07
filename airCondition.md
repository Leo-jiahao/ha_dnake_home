//空调
{"devNo":16385,"devCh":0,"devType":16665,"powerOn":0,"mode":4,"speed":2,"tempDesire":21,"tempIndoor":30,"swing":0},
{"devNo":16386,"devCh":0,"devType":16665,"powerOn":0,"mode":2,"speed":1,"tempDesire":20,"tempIndoor":27,"swing":0},
{"devNo":16387,"devCh":0,"devType":16665,"powerOn":0,"mode":3,"speed":1,"tempDesire":24,"tempIndoor":28,"swing":0},
{"devNo":16388,"devCh":0,"devType":16665,"powerOn":0,"mode":1,"speed":2,"tempDesire":28,"tempIndoor":32,"swing":0},

{
  "action": "readDev",
  "devNo": 16388,
  "devCh": 0
}


<!-- 打开空调 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "powerOn",
  "devNo": 16388,
  "devCh": 0
}
<!-- 关闭 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "powerOff",
  "devNo": 16388,
  "devCh": 0
}
<!-- 切换模式 1-4 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "setMode",
  "param": 3,
  "devNo": 16388,
  "devCh": 0
}

<!-- 切风速 0-1-2高 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "setFlow",
  "param": 1,
  "devNo": 16388,
  "devCh": 0
}

<!-- 设置温度 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "setTemp",
  "param": 22,
  "devNo": 16388,
  "devCh": 0
}
<!-- 切换风摆1开 0关 -->
{
  "action": "ctrlDev",
  "cmd": "airCondition",
  "oper": "setSwing",
  "param": 1,
  "devNo": 16388,
  "devCh": 0
}


# OpenClaw Raspberry Pi LED Control via MQTT

## 功能描述

通过 MQTT 协议控制树莓派上的 LED 设备，支持开灯、关灯和切换开关状态。

## 工作原理

- MQTT 服务端 mosquitto 运行在树莓派上 (192.168.204.75)
- 此技能通过 mosquitto_pub 客户端发送控制消息
- 控制消息发布到主题 `rpi3b/control`
- 消息格式: `{"device":"led1","action":"<action>"}`

## 系统依赖

- mosquitto-clients 工具包

## 安装检查

```bash
#!/bin/bash
# 检查是否安装了 mosquitto_pub
if ! command -v mosquitto_pub &> /dev/null; then
    echo "mosquitto-clients 未安装，正在安装..."
    apt update && apt install -y mosquitto-clients
else
    echo "mosquitto-clients 已安装"
fi
```

## 可用命令

### 开灯 (turn on)
```bash
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"on"}'
```

### 关灯 (turn off)
```bash
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"off"}'
```

### 切换开关 (toggle)
```bash
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"toggle"}'
```

## 使用示例

```bash
# 检查依赖并开灯
if ! command -v mosquitto_pub &> /dev/null; then apt update && apt install -y mosquitto-clients; fi
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"on"}'

# 检查依赖并关灯
if ! command -v mosquitto_pub &> /dev/null; then apt update && apt install -y mosquitto-clients; fi
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"off"}'

# 检查依赖并切换
if ! command -v mosquitto_pub &> /dev/null; then apt update && apt install -y mosquitto-clients; fi
mosquitto_pub -h 192.168.204.75 -t "rpi3b/control" -m '{"device":"led1","action":"toggle"}'
```

## 配置参数

| 参数 | 值 | 说明 |
|------|-----|------|
| MQTT Broker | 192.168.204.75 | 树莓派 MQTT 服务器地址 |
| Topic | rpi3b/control | 控制消息主题 |
| Device ID | led1 | LED 设备标识 |
| Actions | on/off/toggle | 支持的操作 |

## 注意事项

1. 确保宿主机网络可以连接到 MQTT Broker (192.168.204.75)
2. 如果 mosquitto_pub 命令不存在，会自动安装 mosquitto-clients
3. 安装需要管理员权限 (sudo)
4. 消息格式为 JSON，需要使用单引号包裹以避免 shell 转义问题

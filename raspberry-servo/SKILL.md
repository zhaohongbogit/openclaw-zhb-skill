# 树莓派舵机控制技能

## 技能概述

这个技能允许你使用树莓派控制舵机，从基础的单舵机控制到复杂的多舵机协同工作。无论是制作机械臂、云台还是其他需要精确角度控制的项目，这个技能都能帮到你。

## 技能组件

1. **基础舵机控制** - 控制单个舵机的角度位置
2. **平滑运动控制** - 使舵机平滑地从一个位置移动到另一个位置
3. **多舵机同步** - 同时协调控制多个舵机
4. **舵机扫动** - 使舵机在指定范围内来回移动
5. **交互式控制界面** - 通过命令行实时控制舵机

## 所需硬件

- 树莓派 (任何型号)
- 舵机 (如SG90、MG996R等标准PWM舵机)
- 面包板和跳线
- 外部5V电源（推荐，特别是控制多个舵机时）
- 舵机连接器或杜邦线

## 接线图

```
树莓派接线：
          +-----+
          | RPi |
          +-----+
    5V -----> 舵机红线 (电源)
    GND ----> 舵机黑/棕线 (接地)
    GPIO18 --> 舵机黄/橙线 (信号)

使用外部电源时：
    外部5V ---> 舵机红线
    外部GND --> 舵机黑/棕线 + 树莓派GND (共地)
    GPIO18 ----> 舵机黄/橙线 (信号)
```

## 安装步骤

1. **安装必要的软件包**:
   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip
   sudo pip3 install RPi.GPIO
   ```

2. **下载控制脚本**:
   ```bash
   wget -O servo_control.py https://raw.githubusercontent.com/yourusername/raspberry-servo/main/servo_control.py
   wget -O multi_servo_demo.py https://raw.githubusercontent.com/yourusername/raspberry-servo/main/multi_servo_demo.py
   ```

3. **设置权限**:
   ```bash
   chmod +x servo_control.py
   chmod +x multi_servo_demo.py
   ```

## 使用方法

### 基础舵机控制

运行基础演示程序：
```bash
python3 servo_control.py
```

### 多舵机控制

运行多舵机演示程序：
```bash
python3 multi_servo_demo.py --demo
```

### 交互式控制

启动交互式控制：
```bash
python3 multi_servo_demo.py --interactive
```

交互式命令：
- `1 90` - 将舵机1移动到90度
- `2 45 10` - 将舵机2平滑移动到45度，使用10步
- `all 90` - 将所有舵机移动到90度
- `sweep 1 0 180` - 舵机1在0-180度范围内扫动
- `exit` - 退出程序

## 代码片段

### 1. 基础舵机控制

```python
from servo_control import ServoController

# 创建舵机控制器，GPIO针脚18
servo = ServoController(18)

# 设置角度
servo.set_angle(90)  # 设置到90度

# 平滑移动
servo.move_smooth(180, steps=20)  # 平滑移动到180度

# 完成后清理
servo.cleanup()
```

### 2. 多舵机控制

```python
from multi_servo_demo import MultiServoController

# 创建多舵机控制器
controller = MultiServoController()

# 添加舵机
pan_servo = controller.add_servo("pan", 18)  # GPIO 18
tilt_servo = controller.add_servo("tilt", 19)  # GPIO 19

# 设置角度
controller.set_angle("pan", 90)
controller.set_angle("tilt", 45)

# 同步移动
controller.synchronize({
    "pan": 120,
    "tilt": 60
}, steps=15)

# 扫动
controller.sweep("pan", 30, 150, speed=60, cycles=2)

# 完成后清理
controller.cleanup()
```

## 核心代码

### servo_control.py
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
树莓派舵机控制程序
"""

import RPi.GPIO as GPIO
import time

class ServoController:
    def __init__(self, pin, min_pulse_width=0.5, max_pulse_width=2.5, frequency=50):
        """
        初始化舵机控制器

        参数:
            pin (int): 控制舵机的GPIO针脚号 (BCM模式)
            min_pulse_width (float): 最小脉冲宽度，单位为毫秒，通常为0.5-1.0
            max_pulse_width (float): 最大脉冲宽度，单位为毫秒，通常为2.0-2.5
            frequency (int): PWM频率，通常为50Hz
        """
        self.pin = pin
        self.min_pulse_width = min_pulse_width
        self.max_pulse_width = max_pulse_width
        self.frequency = frequency
        self.current_angle = 90  # 默认位置为90度

        # 初始化GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)

        # 创建PWM控制器
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(self._angle_to_duty_cycle(self.current_angle))

    def _angle_to_duty_cycle(self, angle):
        """
        将角度转换为占空比

        参数:
            angle (float): 舵机角度 (0-180)

        返回:
            float: 对应的PWM占空比
        """
        # 确保角度在有效范围内
        angle = max(0, min(180, angle))

        # 将角度转换为脉冲宽度 (ms)
        pulse_width = self.min_pulse_width + (angle / 180.0) * (self.max_pulse_width - self.min_pulse_width)

        # 将脉冲宽度转换为占空比
        duty_cycle = pulse_width * self.frequency / 10.0

        return duty_cycle

    def set_angle(self, angle):
        """
        立即设置舵机角度

        参数:
            angle (float): 舵机角度 (0-180)
        """
        duty_cycle = self._angle_to_duty_cycle(angle)
        self.pwm.ChangeDutyCycle(duty_cycle)
        self.current_angle = angle
        time.sleep(0.1)  # 稍微等待舵机移动

    def move_smooth(self, target_angle, steps=10, delay=0.03):
        """
        平滑地移动舵机到指定角度

        参数:
            target_angle (float): 目标角度 (0-180)
            steps (int): 中间步骤数
            delay (float): 每步之间的延迟，单位为秒
        """
        # 确保目标角度在有效范围内
        target_angle = max(0, min(180, target_angle))

        # 计算每一步的增量
        start_angle = self.current_angle
        angle_increment = (target_angle - start_angle) / steps

        # 逐步移动舵机
        for i in range(steps + 1):
            angle = start_angle + angle_increment * i
            self.set_angle(angle)
            time.sleep(delay)

    def cleanup(self):
        """
        清理GPIO资源
        """
        self.pwm.stop()
```

### multi_servo_demo.py (部分代码)
```python
class MultiServoController:
    def __init__(self):
        """初始化多舵机控制器"""
        # 初始化GPIO
        GPIO.setmode(GPIO.BCM)
        # 存储所有舵机的PWM对象
        self.servos = {}
        # 默认配置参数
        self.default_config = {
            "min_pulse_width": 0.5,  # ms
            "max_pulse_width": 2.5,  # ms
            "frequency": 50,  # Hz
        }

    def add_servo(self, servo_id, pin, min_angle=0, max_angle=180, **kwargs):
        """
        添加一个舵机

        参数:
            servo_id (str): 舵机的标识符
            pin (int): GPIO针脚号(BCM模式)
            min_angle (float): 最小角度限制
            max_angle (float): 最大角度限制
            **kwargs: 其他参数(min_pulse_width, max_pulse_width, frequency)
        """
        config = self.default_config.copy()
        config.update(kwargs)

        # 设置GPIO针脚为输出
        GPIO.setup(pin, GPIO.OUT)

        # 创建PWM对象
        pwm = GPIO.PWM(pin, config["frequency"])

        # 默认角度(居中)
        default_angle = (min_angle + max_angle) / 2

        # 计算默认占空比
        duty_cycle = self._angle_to_duty_cycle(
            default_angle, min_angle, max_angle,
            config["min_pulse_width"], config["max_pulse_width"],
            config["frequency"]
        )

        # 启动PWM
        pwm.start(duty_cycle)

        # 保存舵机信息
        self.servos[servo_id] = {
            "pwm": pwm,
            "pin": pin,
            "min_angle": min_angle,
            "max_angle": max_angle,
            "current_angle": default_angle,
            "config": config
        }

        # 稍微等待舵机初始化
        time.sleep(0.1)
        return servo_id
```

## 参数调整

根据舵机型号可能需要调整以下参数：

| 舵机型号 | min_pulse_width | max_pulse_width | frequency |
|---------|----------------|----------------|-----------|
| SG90    | 0.5            | 2.5            | 50        |
| MG996R  | 0.5            | 2.5            | 50        |
| DS3218  | 0.6            | 2.4            | 50        |

示例：
```python
# 为特定舵机调整参数
servo = ServoController(18, min_pulse_width=0.6, max_pulse_width=2.4)
```

## 常见问题

### 舵机不动或抖动
- 检查接线是否正确
- 确保信号线连接到正确的GPIO针脚
- 检查电源是否足够
- 尝试调整min_pulse_width和max_pulse_width参数

### 舵机角度不准确
- 调整min_pulse_width和max_pulse_width参数
- 检查舵机是否机械受限

### 多个舵机同时使用时不稳定
- 使用外部电源
- 确保树莓派GND和电源GND连接在一起（共地）

### GPIO警告
- 使用`GPIO.setwarnings(False)`消除警告
- 确保程序正常终止并调用cleanup()

## 项目示例

### 1. 简单的云台项目

```python
from multi_servo_demo import MultiServoController
import time

# 创建控制器
controller = MultiServoController()

# 添加水平和垂直舵机
pan = controller.add_servo("pan", 18)   # 水平舵机
tilt = controller.add_servo("tilt", 19) # 垂直舵机

try:
    # 跟踪运动模式
    positions = [
        {"pan": 45, "tilt": 45},
        {"pan": 135, "tilt": 45},
        {"pan": 135, "tilt": 135},
        {"pan": 45, "tilt": 135},
        {"pan": 45, "tilt": 45},
    ]

    for pos in positions:
        controller.synchronize(pos, steps=20)
        time.sleep(1)

    # 回到中心位置
    controller.synchronize({"pan": 90, "tilt": 90})

finally:
    controller.cleanup()
```

### 2. 舵机波浪效果

```python
from multi_servo_demo import MultiServoController
import time

# 创建控制器
controller = MultiServoController()

# 添加5个舵机
servos = ["servo1", "servo2", "servo3", "servo4", "servo5"]
for i, servo_id in enumerate(servos):
    controller.add_servo(servo_id, 18 + i)  # GPIO 18, 19, 20, 21, 22

try:
    # 波浪效果
    for _ in range(3):  # 重复3次
        # 正向波
        for i, servo_id in enumerate(servos):
            controller.set_angle(servo_id, 135)
            time.sleep(0.15)
            if i > 0:
                controller.set_angle(servos[i-1], 45)

        time.sleep(0.15)
        controller.set_angle(servos[-1], 45)
        time.sleep(0.5)

    # 回到中心位置
    for servo_id in servos:
        controller.set_angle(servo_id, 90)

finally:
    controller.cleanup()
```

## 安全注意事项

- 不要超出舵机的额定电压范围（通常为4.8V-6V）
- 避免舵机堵转，可能导致舵机损坏或电源问题
- 先进行编程，再连接舵机，防止舵机在程序启动时突然移动
- 确保机械结构没有限制舵机的移动范围
- 控制多个舵机时使用外部电源，避免树莓派供电不足

## 资源

- [RPi.GPIO库文档](https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/)
- [SG90舵机数据表](http://www.micropik.com/PDF/SG90Servo.pdf)
- [树莓派GPIO针脚图](https://www.raspberrypi.org/documentation/usage/gpio/)

## 作者

作者：Claude

## 许可证

MIT许可证
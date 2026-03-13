# 树莓派舵机控制程序

这个项目包含用于树莓派控制舵机的Python程序，提供了从基础到高级的多种控制功能。

## 文件说明

- `servo_control.py`: 基础舵机控制程序，包含单舵机控制功能
- `multi_servo_demo.py`: 多舵机控制程序，包含更多高级功能和演示序列

## 硬件要求

- 树莓派 (任何型号都可以)
- 一个或多个舵机 (SG90、MG996R等标准舵机)
- 外部电源 (如果控制多个舵机，建议使用外部5V电源)
- 面包板和连接线

## 接线说明

基本接线方式：

1. 舵机红线 → 5V电源
2. 舵机棕/黑线 → GND (地)
3. 舵机黄/橙/信号线 → 树莓派GPIO针脚 (默认是GPIO18)

**注意**：如果连接多个舵机，建议使用外部电源，并将电源的GND连接到树莓派的GND。

## 软件依赖

```
sudo apt-get update
sudo apt-get install python3-pip
sudo pip3 install RPi.GPIO
```

## 使用方法

### 基础舵机控制

运行基础舵机控制程序：

```
python3 servo_control.py
```

这将运行一个演示序列，展示舵机控制的基本功能。

### 多舵机控制

运行多舵机控制程序有两种模式：

1. 演示模式：
```
python3 multi_servo_demo.py --demo
```

2. 交互式控制模式：
```
python3 multi_servo_demo.py --interactive
```
或者直接运行：
```
python3 multi_servo_demo.py
```

在交互式模式下，您可以输入命令来控制各个舵机：

- `1 90` - 将舵机1移动到90度
- `2 45 10` - 将舵机2平滑移动到45度，使用10步
- `all 90` - 将所有舵机移动到90度
- `sweep 1 0 180` - 舵机1在0-180度范围内扫动
- `exit` - 退出程序

## 自定义使用

您可以将`ServoController`或`MultiServoController`类导入到自己的Python程序中：

```python
from servo_control import ServoController

# 创建舵机控制器，GPIO针脚18
servo = ServoController(18)

# 控制舵机
servo.set_angle(90)  # 设置到90度
servo.move_smooth(180, steps=20)  # 平滑移动到180度

# 清理
servo.cleanup()
```

## 调整舵机参数

不同型号的舵机可能需要调整脉冲宽度参数。在创建控制器时可以指定：

```python
# 对于常见的SG90舵机
servo = ServoController(18, min_pulse_width=0.5, max_pulse_width=2.5)

# 对于一些需要调整的舵机
servo = ServoController(18, min_pulse_width=0.6, max_pulse_width=2.4)
```

## 故障排除

1. **舵机不动或抖动**：
   - 检查接线是否正确
   - 确认电源是否足够
   - 尝试调整min_pulse_width和max_pulse_width参数

2. **舵机动作范围不足或过大**：
   - 调整min_pulse_width和max_pulse_width参数

3. **多个舵机同时使用时不稳定**：
   - 使用外部电源
   - 确保树莓派GND和电源GND连接在一起

## 安全注意事项

- 不要超出舵机的额定电压范围
- 注意防止舵机堵转，这可能导致舵机损坏
- 确保舵机的角度限制不会导致机械结构卡住

## 许可

此项目采用MIT许可证。
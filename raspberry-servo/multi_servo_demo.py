#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
树莓派多舵机控制演示程序
"""

import RPi.GPIO as GPIO
import time
import sys
import argparse

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

    def _angle_to_duty_cycle(self, angle, min_angle, max_angle,
                             min_pulse_width, max_pulse_width, frequency):
        """
        将角度转换为占空比
        """
        # 限制角度范围
        angle = max(min_angle, min(max_angle, angle))

        # 将角度映射到脉冲宽度范围
        angle_range = max_angle - min_angle
        angle_percentage = (angle - min_angle) / angle_range if angle_range > 0 else 0

        pulse_width = min_pulse_width + angle_percentage * (max_pulse_width - min_pulse_width)

        # 将脉冲宽度转换为占空比
        duty_cycle = pulse_width * frequency / 10.0

        return duty_cycle

    def set_angle(self, servo_id, angle):
        """
        设置特定舵机的角度

        参数:
            servo_id (str): 舵机标识符
            angle (float): 目标角度
        """
        if servo_id not in self.servos:
            raise ValueError(f"舵机 '{servo_id}' 未找到")

        servo = self.servos[servo_id]

        # 计算占空比
        duty_cycle = self._angle_to_duty_cycle(
            angle,
            servo["min_angle"],
            servo["max_angle"],
            servo["config"]["min_pulse_width"],
            servo["config"]["max_pulse_width"],
            servo["config"]["frequency"]
        )

        # 更新占空比
        servo["pwm"].ChangeDutyCycle(duty_cycle)
        servo["current_angle"] = angle
        time.sleep(0.05)  # 稍微等待舵机移动

    def move_smooth(self, servo_id, target_angle, steps=10, delay=0.03):
        """
        平滑移动舵机到目标角度

        参数:
            servo_id (str): 舵机标识符
            target_angle (float): 目标角度
            steps (int): 移动步数
            delay (float): 每步之间的延迟(秒)
        """
        if servo_id not in self.servos:
            raise ValueError(f"舵机 '{servo_id}' 未找到")

        servo = self.servos[servo_id]
        start_angle = servo["current_angle"]

        # 限制目标角度
        target_angle = max(servo["min_angle"], min(servo["max_angle"], target_angle))

        # 计算增量
        angle_increment = (target_angle - start_angle) / steps

        # 分步移动
        for i in range(steps + 1):
            angle = start_angle + angle_increment * i
            self.set_angle(servo_id, angle)
            time.sleep(delay)

    def sweep(self, servo_id, start_angle=None, end_angle=None,
              speed=30, cycles=1, pause_time=0.5):
        """
        使舵机在指定角度范围内来回扫动

        参数:
            servo_id (str): 舵机标识符
            start_angle (float): 起始角度(默认为舵机最小角度)
            end_angle (float): 结束角度(默认为舵机最大角度)
            speed (float): 移动速度(度/秒)
            cycles (int): 来回扫动的次数
            pause_time (float): 在端点处的暂停时间(秒)
        """
        if servo_id not in self.servos:
            raise ValueError(f"舵机 '{servo_id}' 未找到")

        servo = self.servos[servo_id]

        # 如果没有指定角度，使用舵机的角度范围
        if start_angle is None:
            start_angle = servo["min_angle"]
        if end_angle is None:
            end_angle = servo["max_angle"]

        # 限制角度范围
        start_angle = max(servo["min_angle"], min(servo["max_angle"], start_angle))
        end_angle = max(servo["min_angle"], min(servo["max_angle"], end_angle))

        # 确保起始角度小于结束角度
        if start_angle > end_angle:
            start_angle, end_angle = end_angle, start_angle

        # 计算扫动步骤
        angle_range = end_angle - start_angle
        travel_time = angle_range / speed if speed > 0 else 0
        steps = int(max(5, travel_time / 0.02))  # 至少5步，步进时间约为20ms

        # 执行扫动
        try:
            for _ in range(cycles):
                # 从起点到终点
                self.move_smooth(servo_id, end_angle, steps=steps)
                time.sleep(pause_time)

                # 从终点到起点
                self.move_smooth(servo_id, start_angle, steps=steps)
                time.sleep(pause_time)
        except KeyboardInterrupt:
            print("\n扫动被用户中断")

    def synchronize(self, positions, steps=10, delay=0.03):
        """
        同步移动多个舵机到指定位置

        参数:
            positions (dict): {servo_id: target_angle}的字典
            steps (int): 移动步数
            delay (float): 每步之间的延迟(秒)
        """
        # 收集所有舵机的起始角度和目标角度
        servo_data = {}
        for servo_id, target_angle in positions.items():
            if servo_id in self.servos:
                servo = self.servos[servo_id]
                start_angle = servo["current_angle"]

                # 限制目标角度
                target_angle = max(servo["min_angle"], min(servo["max_angle"], target_angle))

                # 计算增量
                angle_increment = (target_angle - start_angle) / steps

                servo_data[servo_id] = {
                    "start": start_angle,
                    "target": target_angle,
                    "increment": angle_increment
                }
            else:
                print(f"警告: 舵机 '{servo_id}' 未找到，已忽略")

        # 同步移动所有舵机
        for i in range(steps + 1):
            for servo_id, data in servo_data.items():
                angle = data["start"] + data["increment"] * i
                self.set_angle(servo_id, angle)
            time.sleep(delay)

    def cleanup(self):
        """清理所有舵机资源"""
        for servo_id, servo in self.servos.items():
            servo["pwm"].stop()
        GPIO.cleanup()
        self.servos = {}

def demo_sequence():
    """多舵机控制演示序列"""
    controller = MultiServoController()

    try:
        # 添加三个舵机 (假设连接到GPIO针脚18, 19, 20)
        pan_servo = controller.add_servo("pan", 18)
        tilt_servo = controller.add_servo("tilt", 19)
        grip_servo = controller.add_servo("grip", 20, min_angle=30, max_angle=150)

        print("初始化完成，开始演示...")

        # 基础移动演示
        print("1. 基础移动演示")
        controller.set_angle("pan", 0)
        time.sleep(1)
        controller.set_angle("pan", 180)
        time.sleep(1)
        controller.set_angle("pan", 90)
        time.sleep(1)

        # 平滑移动演示
        print("2. 平滑移动演示")
        controller.move_smooth("tilt", 0)
        time.sleep(1)
        controller.move_smooth("tilt", 180, steps=20)
        time.sleep(1)
        controller.move_smooth("tilt", 90, steps=15)
        time.sleep(1)

        # 扫动演示
        print("3. 扫动演示")
        controller.sweep("pan", 30, 150, speed=60, cycles=2)

        # 同步移动演示
        print("4. 同步移动演示")
        controller.synchronize({
            "pan": 30,
            "tilt": 30,
            "grip": 30
        })
        time.sleep(1)

        controller.synchronize({
            "pan": 150,
            "tilt": 150,
            "grip": 150
        })
        time.sleep(1)

        # 复位到中间位置
        print("5. 复位到中间位置")
        controller.synchronize({
            "pan": 90,
            "tilt": 90,
            "grip": 90
        })

        print("演示结束")

    except Exception as e:
        print(f"演示过程中发生错误: {e}")

    finally:
        controller.cleanup()

def interactive_control():
    """交互式控制模式"""
    controller = MultiServoController()

    try:
        # 添加舵机
        servos = {
            "1": controller.add_servo("servo1", 18),
            "2": controller.add_servo("servo2", 19),
            "3": controller.add_servo("servo3", 20)
        }

        print("交互式舵机控制")
        print("-------------------")
        print("命令格式:")
        print("  舵机号码 角度 [speed]")
        print("例如:")
        print("  1 90     - 将舵机1移动到90度")
        print("  2 45 10  - 将舵机2平滑移动到45度，使用10步")
        print("  all 90   - 将所有舵机移动到90度")
        print("  sweep 1 0 180 - 舵机1在0-180度范围内扫动")
        print("  exit     - 退出程序")
        print("-------------------")

        while True:
            cmd = input("\n输入命令 > ").strip().split()

            if not cmd:
                continue

            if cmd[0].lower() == "exit":
                break

            elif cmd[0].lower() == "all" and len(cmd) >= 2:
                try:
                    angle = float(cmd[1])
                    positions = {f"servo{i}": angle for i in range(1, 4)}

                    steps = 10
                    if len(cmd) >= 3:
                        steps = int(cmd[2])

                    controller.synchronize(positions, steps=steps)
                    print(f"所有舵机已移动到 {angle}度")
                except ValueError:
                    print("错误的角度值")

            elif cmd[0].lower() == "sweep" and len(cmd) >= 2:
                try:
                    servo_num = cmd[1]
                    servo_id = f"servo{servo_num}"

                    start = 0
                    end = 180
                    speed = 30
                    cycles = 1

                    if len(cmd) >= 4:
                        start = float(cmd[2])
                        end = float(cmd[3])

                    if len(cmd) >= 5:
                        speed = float(cmd[4])

                    if len(cmd) >= 6:
                        cycles = int(cmd[5])

                    if servo_id in servos.values():
                        controller.sweep(servo_id, start, end, speed, cycles)
                        print(f"舵机{servo_num}完成扫动")
                    else:
                        print(f"找不到舵机{servo_num}")

                except (ValueError, IndexError):
                    print("命令格式错误")

            elif cmd[0] in servos and len(cmd) >= 2:
                try:
                    servo_id = servos[cmd[0]]
                    angle = float(cmd[1])

                    if len(cmd) >= 3:
                        steps = int(cmd[2])
                        controller.move_smooth(servo_id, angle, steps=steps)
                        print(f"舵机{cmd[0]}平滑移动到{angle}度")
                    else:
                        controller.set_angle(servo_id, angle)
                        print(f"舵机{cmd[0]}移动到{angle}度")

                except ValueError:
                    print("错误的角度值或步数")
            else:
                print("无效的命令")

    except KeyboardInterrupt:
        print("\n程序被用户中断")

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        controller.cleanup()

if __name__ == "__main__":
    # 设置命令行参数
    parser = argparse.ArgumentParser(description="树莓派多舵机控制程序")
    parser.add_argument("--demo", action="store_true", help="运行演示序列")
    parser.add_argument("--interactive", action="store_true", help="启动交互式控制模式")

    args = parser.parse_args()

    if args.demo:
        demo_sequence()
    elif args.interactive:
        interactive_control()
    else:
        # 默认运行交互式模式
        interactive_control()
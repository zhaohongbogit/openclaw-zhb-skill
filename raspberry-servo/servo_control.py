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

        # 将脉冲宽度转换为占空比 (%)
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

def main():
    """
    演示程序
    """
    try:
        # 创建舵机控制器，默认使用GPIO18（可更改）
        servo_pin = 18
        servo = ServoController(servo_pin)

        print("舵机控制演示开始")

        # 设置到0度
        print("移动到0度")
        servo.set_angle(0)
        time.sleep(1)

        # 设置到90度
        print("移动到90度")
        servo.set_angle(90)
        time.sleep(1)

        # 设置到180度
        print("移动到180度")
        servo.set_angle(180)
        time.sleep(1)

        # 平滑移动演示
        print("平滑移动到0度")
        servo.move_smooth(0)
        time.sleep(1)

        print("平滑移动到180度")
        servo.move_smooth(180)
        time.sleep(1)

        # 连续移动演示
        print("连续移动演示")
        for angle in range(0, 181, 30):
            print(f"移动到 {angle}度")
            servo.move_smooth(angle)
            time.sleep(0.5)

        for angle in range(180, -1, -30):
            print(f"移动到 {angle}度")
            servo.move_smooth(angle)
            time.sleep(0.5)

        print("舵机控制演示结束")

    except KeyboardInterrupt:
        print("\n程序被用户中断")

    finally:
        # 清理资源
        if 'servo' in locals():
            servo.cleanup()
        GPIO.cleanup()  # 清理所有GPIO资源

if __name__ == "__main__":
    main()
# src/particle.py
import numpy as np

class Particle:
    def __init__(self, position):
        """
        初始化一个粒子。
        Args:
            position: 一个包含[x, y, z]坐标的列表或np.array。
        """
        # 核心状态属性
        self.position = np.array(position, dtype=np.float32)  # 当前位置
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32) # 当前速度
        self.acceleration = np.array([0.0, 0.0, 0.0], dtype=np.float32) # 当前加速度（由力产生）

        # SPH计算所需的物理属性（先定义，下一阶段才计算）
        self.density = 0.0        # 密度
        self.pressure = 0.0       # 压力

        # 可视化属性（可选）
        self.color = [1.0, 0.5, 0.2, 1.0]  # RGBA颜色 (橙色)

    def update_position(self, dt):
        """根据速度和加速度，更新粒子的位置（最简单的欧拉积分）。"""
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        # 清空加速度，为下一帧计算做准备
        self.acceleration = np.array([0.0, 0.0, 0.0])
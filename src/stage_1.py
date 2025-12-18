# src/stage_1.py
import glfw
from particle import Particle
from OpenGL.GL import *

class SimulationWindow:
    def __init__(self):
        self.particle_count = 500  # 这是一个可以被滑块控制的变量
        if not glfw.init():
            return
        self.window = glfw.create_window(800, 600, "3D Fluid Sim - Stage 1", None, None)
        glfw.make_context_current(self.window)

        # **关键步骤：设置UI回调函数**
        glfw.set_window_size_callback(self.window, self.on_resize)
        # 这里我们暂时用键盘按键模拟滑块，下节课用更专业的UI库
        glfw.set_key_callback(self.window, self.on_key)
        
        self.particles = []
        self.init_particles()  # ✅ 现在可以正确调用了

    def init_particles(self):
        """初始化粒子，让它们随机分布在一个方块内。"""
        import random
        for _ in range(self.particle_count):
            x = random.uniform(-0.5, 0.5)
            y = random.uniform(-0.5, 0.5)
            z = random.uniform(-0.5, 0.5)
            self.particles.append(Particle([x, y, z]))

    def on_resize(self, window, width, height):
        """当窗口大小改变时，调整OpenGL的视口。"""
        glViewport(0, 0, width, height)

    def on_key(self, window, key, scancode, action, mods):
        """键盘回调：按上/下键增减粒子数量，模拟滑块效果。"""
        if action == glfw.PRESS or action == glfw.REPEAT:
            if key == glfw.KEY_UP:
                self.particle_count = min(6000, self.particle_count + 50)
                print(f"粒子数增加至: {self.particle_count}")
                # 重新初始化粒子
                self.particles = []
                self.init_particles()
            elif key == glfw.KEY_DOWN:
                self.particle_count = max(10, self.particle_count - 50)
                print(f"粒子数减少至: {self.particle_count}")
                # 重新初始化粒子
                self.particles = []
                self.init_particles()

    def run(self):
        """主渲染循环。"""
        while not glfw.window_should_close(self.window):
            # 1. 处理事件（如按键）
            glfw.poll_events()
            # 2. 清空屏幕
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            # 3. 在这里绘制粒子
            self.render_particles()
            # 4. 交换缓冲区，显示画面
            glfw.swap_buffers(self.window)
        glfw.terminate()

    def render_particles(self):
        """使用立即模式（简单但低效）绘制所有粒子。"""
        glPointSize(5.0)  # 设置点的大小
        glBegin(GL_POINTS)  # 开始绘制点
        for p in self.particles:
            glColor4f(*p.color)  # 设置颜色 (R,G,B,A)
            glVertex3f(*p.position)  # 设置顶点位置 (x,y,z)
        glEnd()  # 结束绘制

if __name__ == "__main__":
    app = SimulationWindow()
    app.run()
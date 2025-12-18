# src/main.py
import glfw
import math
from particle import Particle
from OpenGL.GL import *
from OpenGL.GLU import *

class SimulationWindow:
    def __init__(self):
        self.particle_count = 500  # 粒子数量
        if not glfw.init():
            return
        
        # 创建窗口
        self.window = glfw.create_window(800, 600, "3D Fluid Sim - Stage 1", None, None)
        if not self.window:
            glfw.terminate()
            return
            
        glfw.make_context_current(self.window)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # 设置回调函数
        glfw.set_window_size_callback(self.window, self.on_resize)
        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_scroll_callback(self.window, self.on_mouse_scroll)
        
        # 摄像机参数
        self.camera_distance = 5.0  # 摄像机距离原点的距离
        self.camera_yaw = 45.0      # 水平旋转角度（度）
        self.camera_pitch = 30.0    # 垂直旋转角度（度）
        self.last_mouse_x = 400     # 上次鼠标X位置
        self.last_mouse_y = 300     # 上次鼠标Y位置
        self.mouse_dragging = False # 鼠标是否正在拖动
        
        # 初始化粒子
        self.particles = []
        self.init_particles()
        
        # 初始化OpenGL设置
        glClearColor(0.1, 0.1, 0.1, 1.0)  # 背景颜色
        
    def init_particles(self):
        """初始化粒子，让它们随机分布在一个立方体内"""
        import random
        self.particles = []  # 清空粒子列表
        for _ in range(self.particle_count):
            x = random.uniform(-1.0, 1.0)
            y = random.uniform(-1.0, 1.0)
            z = random.uniform(-1.0, 1.0)
            self.particles.append(Particle([x, y, z]))

    def on_resize(self, window, width, height):
        """窗口大小改变时调整视口"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def on_key(self, window, key, scancode, action, mods):
        """键盘回调函数"""
        if action == glfw.PRESS or action == glfw.REPEAT:
            # 摄像机移动控制
            move_speed = 0.2
            if key == glfw.KEY_W:  # 向前移动
                self.camera_distance = max(1.0, self.camera_distance - move_speed)
            elif key == glfw.KEY_S:  # 向后移动
                self.camera_distance += move_speed
            elif key == glfw.KEY_A:  # 向左旋转
                self.camera_yaw -= 5.0
            elif key == glfw.KEY_D:  # 向右旋转
                self.camera_yaw += 5.0
            elif key == glfw.KEY_Q:  # 向上倾斜
                self.camera_pitch = min(89.0, self.camera_pitch + 5.0)
            elif key == glfw.KEY_E:  # 向下倾斜
                self.camera_pitch = max(-89.0, self.camera_pitch - 5.0)
            elif key == glfw.KEY_R:  # 重置摄像机
                self.camera_distance = 5.0
                self.camera_yaw = 45.0
                self.camera_pitch = 30.0
            
            # 粒子数量控制
            elif key == glfw.KEY_UP:
                self.particle_count = min(6000, self.particle_count + 50)
                print(f"粒子数增加至: {self.particle_count}")
                self.init_particles()
            elif key == glfw.KEY_DOWN:
                self.particle_count = max(10, self.particle_count - 50)
                print(f"粒子数减少至: {self.particle_count}")
                self.init_particles()
            
            # 退出程序
            elif key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            
            # 切换鼠标拖拽模式
            elif key == glfw.KEY_TAB:
                if glfw.get_input_mode(window, glfw.CURSOR) == glfw.CURSOR_NORMAL:
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
                else:
                    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def on_mouse_move(self, window, xpos, ypos):
        """鼠标移动回调函数"""
        if glfw.get_input_mode(window, glfw.CURSOR) == glfw.CURSOR_DISABLED:
            # 计算鼠标移动距离
            dx = xpos - self.last_mouse_x
            dy = ypos - self.last_mouse_y
            
            # 更新摄像机角度
            sensitivity = 0.1
            self.camera_yaw += dx * sensitivity
            self.camera_pitch -= dy * sensitivity
            
            # 限制俯仰角范围
            self.camera_pitch = max(-89.0, min(89.0, self.camera_pitch))
        
        # 更新鼠标位置
        self.last_mouse_x = xpos
        self.last_mouse_y = ypos

    def on_mouse_scroll(self, window, xoffset, yoffset):
        """鼠标滚轮回调函数"""
        zoom_speed = 0.5
        self.camera_distance = max(1.0, self.camera_distance - yoffset * zoom_speed)

    def update_camera(self):
        """更新摄像机位置和朝向"""
        # 计算摄像机位置（球坐标转直角坐标）
        yaw_rad = math.radians(self.camera_yaw)
        pitch_rad = math.radians(self.camera_pitch)
        
        # 计算摄像机位置
        cam_x = self.camera_distance * math.cos(pitch_rad) * math.cos(yaw_rad)
        cam_y = self.camera_distance * math.sin(pitch_rad)
        cam_z = self.camera_distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        
        # 设置模型视图矩阵
        glLoadIdentity()
        gluLookAt(
            cam_x, cam_y, cam_z,  # 摄像机位置
            0.0, 0.0, 0.0,       # 观察点位置（原点）
            0.0, 1.0, 0.0        # 上方向
        )

    def draw_coordinate_axes(self):
        """绘制坐标轴（用于3D空间参考）"""
        glLineWidth(2.0)
        glBegin(GL_LINES)
        
        # X轴（红色）
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(2.0, 0.0, 0.0)
        
        # Y轴（绿色）
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 2.0, 0.0)
        
        # Z轴（蓝色）
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 2.0)
        
        glEnd()
        
        # 绘制坐标轴标签
        glColor3f(1.0, 1.0, 1.0)
        self.draw_text_3d(2.1, 0.0, 0.0, "X")
        self.draw_text_3d(0.0, 2.1, 0.0, "Y")
        self.draw_text_3d(0.0, 0.0, 2.1, "Z")

    def draw_text_3d(self, x, y, z, text):
        """在3D空间中绘制文本（简单实现）"""
        # 这是一个简化的3D文本绘制函数
        # 在实际应用中，您可能需要使用纹理或更复杂的文本渲染
        glRasterPos3f(x, y, z)
        for char in text:
            # 这里使用GLUT的位图字体，需要安装PyOpenGL并导入GLUT
            # 为了简化，我们暂时省略具体实现
            pass

    def draw_bounding_box(self):
        """绘制包围盒，帮助理解3D空间"""
        glLineWidth(1.0)
        glColor3f(0.5, 0.5, 0.5)  # 灰色
        glBegin(GL_LINE_LOOP)
        # 底面
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glEnd()
        
        glBegin(GL_LINE_LOOP)
        # 顶面
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glEnd()
        
        # 连接底面和顶面的四条边
        glBegin(GL_LINES)
        glVertex3f(-1.0, -1.0, -1.0); glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0); glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, -1.0, 1.0); glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0); glVertex3f(-1.0, 1.0, 1.0)
        glEnd()

    def render_particles(self):
        """渲染所有粒子"""
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for p in self.particles:
            # 根据粒子位置设置颜色（简单的颜色渐变）
            r = (p.position[0] + 1.0) / 2.0  # X坐标映射到[0,1]
            g = (p.position[1] + 1.0) / 2.0  # Y坐标映射到[0,1]
            b = (p.position[2] + 1.0) / 2.0  # Z坐标映射到[0,1]
            glColor3f(r, g, b)
            glVertex3f(*p.position)
        glEnd()

    def display_instructions(self):
        """在控制台显示操作说明"""
        print("=== 3D粒子模拟器操作说明 ===")
        print("W/S: 前进/后退 (调整摄像机距离)")
        print("A/D: 左转/右转 (调整水平角度)")
        print("Q/E: 上仰/下俯 (调整垂直角度)")
        print("鼠标移动: 旋转视角 (当鼠标模式启用时)")
        print("鼠标滚轮: 缩放")
        print("上/下箭头: 增加/减少粒子数量")
        print("R: 重置摄像机位置")
        print("TAB: 切换鼠标控制模式")
        print("ESC: 退出程序")
        print("==========================")

    def run(self):
        """主渲染循环"""
        # 显示操作说明
        self.display_instructions()
        
        # 初始设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45.0, 800/600, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
        while not glfw.window_should_close(self.window):
            # 处理事件
            glfw.poll_events()
            
            # 清空屏幕和深度缓冲
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # 更新摄像机
            self.update_camera()
            
            # 绘制坐标轴
            self.draw_coordinate_axes()
            
            # 绘制包围盒
            self.draw_bounding_box()
            
            # 绘制粒子
            self.render_particles()
            
            # 交换缓冲区
            glfw.swap_buffers(self.window)
        
        glfw.terminate()

if __name__ == "__main__":
    app = SimulationWindow()
    app.run()

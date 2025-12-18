# **第二节课课件：手把手搭建基础框架 - 从零到一的粒子世界**

**课程口号：** “一行代码，一个粒子；一次提交，一步脚印。”

---

### **一、 课程目标与回顾（5分钟）**

**一句话目标：** 今天，我们要亲手搭建起项目的“地基”和“骨架”，让500个粒子在窗口中“活”起来，并为它们装上可调节的“控制器”。

**快速回顾：**
*   **总目标**：一个能模拟水滴碰撞的3D程序。
*   **四阶段**：**基础框架** → SPH算法 → 碰撞交互 → 优化控制。
*   **本节课**：我们专注攻克**第一阶段**，打好一切的基础。

---

### **二、 任务1.1：搭建项目基础框架（25分钟）**

**目标：** 创建一个规范、可维护的代码“家”，并打开一扇能与用户对话的“窗”。

#### **1. 创建你的代码基地：GitHub仓库**
*   **原理**：GitHub是我们的云端代码保险箱和进度记录本。
*   **实践步骤：**
    1.  登录GitHub，点击“New repository”。
    2.  仓库名：`3d-fluid-sim`。
    3.  勾选 `Add a README.md`，这是项目的“门面”。
    4.  点击创建，然后通过 `git clone <你的仓库链接>` 命令，将它“下载”到你的电脑。

#### **2. 规划你的项目结构（仓库里放什么？）**
一个清晰的结构让后期开发事半功倍。我们的仓库根目录初步规划如下：
```
3d-fluid-sim/
├── src/                    # 源代码目录
│   ├── main.py            # 程序主入口，启动窗口和主循环
│   ├── particle.py        # 粒子类（Particle）的定义
│   └── solver.py          # 流体求解器类（将来SPH算法的核心）
├── requirements.txt       # 项目依赖库清单（如PyOpenGL, glfw, numpy）
├── README.md              # 项目说明文档
└── .gitignore             # 告诉Git哪些文件不用上传（如临时文件、虚拟环境）
```

#### **3. 配置Python虚拟环境与安装依赖**
*   **原理**：虚拟环境像一个独立的“工具箱”，防止不同项目的库互相打架。
*   **实践步骤（在项目根目录执行）：**
    ```bash
    # 1. 创建虚拟环境
    python -m venv venv

    # 2. 激活虚拟环境 (Windows)
    .\venv\Scripts\activate
    # 激活虚拟环境 (Mac/Linux)
    source venv/bin/activate

    # 3. 安装核心依赖库
    pip install PyOpenGL glfw numpy
    # 将当前环境中的库列表导出到requirements.txt
    pip freeze > requirements.txt
    ```

#### **4. 打造动态可交互窗口（main.py核心架构）**
*   **原理**：`glfw`库负责创建和管理窗口，处理键盘鼠标事件；`OpenGL`负责在窗口内绘图。我们通过“回调函数”来响应滑块的变化。
*   **手把手代码实践：**
    ```python
    # src/main.py
    import glfw
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

        def on_resize(self, window, width, height):
            """当窗口大小改变时，调整OpenGL的视口。"""
            glViewport(0, 0, width, height)

        def on_key(self, window, key, scancode, action, mods):
            """键盘回调：按上/下键增减粒子数量，模拟滑块效果。"""
            if action == glfw.PRESS or action == glfw.REPEAT:
                if key == glfw.KEY_UP:
                    self.particle_count = min(1000, self.particle_count + 50)
                    print(f"粒子数增加至: {self.particle_count}")
                elif key == glfw.KEY_DOWN:
                    self.particle_count = max(10, self.particle_count - 50)
                    print(f"粒子数减少至: {self.particle_count}")

        def run(self):
            """主渲染循环。"""
            while not glfw.window_should_close(self.window):
                # 1. 处理事件（如按键）
                glfw.poll_events()
                # 2. 清空屏幕
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                # 3. 在这里绘制粒子（下一任务实现）
                self.render_particles()
                # 4. 交换缓冲区，显示画面
                glfw.swap_buffers(self.window)
            glfw.terminate()

        def render_particles(self):
            """绘制粒子（暂留空，任务1.3实现）。"""
            # TODO: 在这里绘制self.particle_count个粒子
            pass

    if __name__ == "__main__":
        app = SimulationWindow()
        app.run()
    ```
*   **立即测试**：运行 `python src/main.py`，你应该看到一个黑色的窗口，并且按上下键能在控制台看到输出变化。

---

### **三、 任务1.2：建立粒子数据结构（15分钟）**

**目标：** 定义“粒子”这个基本单元的属性和能力。

*   **原理**：在SPH中，流体由大量粒子表示。每个粒子都需要记录自己的状态（位置、速度）和计算出的临时属性（密度、压力）。
*   **手把手代码实践：**
    ```python
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
    ```
*   **理解重点**：`Particle` 类是一个“模板”或“蓝图”。`self.position` 等是它的“特征”，`update_position` 是它的“行为”。

---

### **四、 任务1.3：简单粒子渲染（20分钟）**

**目标：** 将内存中的粒子数据，变成屏幕上可见的点。

*   **原理**：OpenGL需要我们将粒子数据（位置、颜色）放入特定的缓冲区（VBO），然后通过一个简单的着色器程序来绘制。
*   **手把手代码实践（更新 main.py 和 particle.py）：**
    ```python
    # 首先，在 SimulationWindow.__init__ 中初始化粒子系统
    # src/main.py (SimulationWindow.__init__ 方法内添加)
    self.particles = []
    self.init_particles()

    def init_particles(self):
        """初始化粒子，让它们随机分布在一个方块内。"""
        import random
        for _ in range(self.particle_count):
            x = random.uniform(-0.5, 0.5)
            y = random.uniform(-0.5, 0.5)
            z = 0.0  # 我们先在2D平面观察
            self.particles.append(Particle([x, y, z]))

    # 然后，实现 render_particles 方法
    def render_particles(self):
        """使用立即模式（简单但低效）绘制所有粒子。"""
        glPointSize(5.0)  # 设置点的大小
        glBegin(GL_POINTS) # 开始绘制点
        for p in self.particles:
            glColor4f(*p.color)  # 设置颜色 (R,G,B,A)
            glVertex3f(*p.position) # 设置顶点位置 (x,y,z)
        glEnd() # 结束绘制
    ```
*   **技巧**：先只初始化10个粒子(`range(10)`)，确保能正确显示。再改成 `self.particle_count`，并用键盘上下键动态改变数量，验证交互。
*   **验收标准达成**：运行程序，你应该看到一个窗口，里面有指定数量的橙色小点，并且按上下键，点的数量会动态变化。

---

### **五、 任务1.4：Git提交与TDD测试初探（10分钟）**

**目标：** 规范地保存工作成果，并开始建立测试意识。

#### **1. 规范的Git提交**
现在我们已经完成了基础框架，是时候进行第一次正式提交了。
```bash
# 在项目根目录下执行
git add src/ requirements.txt .gitignore README.md
git commit -m "feat: 搭建基础框架与窗口系统\n- 创建GLFW窗口并实现键盘交互\n- 实现Particle基础类\n- 实现500个粒子的初始化和简单渲染"
```
*   **解释标记**：`feat` 表示这是一个新功能。提交信息的第一行是摘要，空行后是更详细的描述。

#### **2. 为验收标准设计简单测试（TDD思维）**
虽然我们还没写单元测试文件，但可以手动验证，并规划未来的测试：
*   **测试用例1（正测试）：窗口与粒子显示**
    *   **情景**：程序启动后。
    *   **操作**：运行 `python src/main.py`。
    *   **预期结果**：成功弹出标题为“3D Fluid Sim - Stage 1”的窗口，窗口内显示指定数量的橙色点。
    *   **解释**：验证图形窗口和基础渲染管线工作正常。

*   **测试用例2（交互测试）：滑块参数实时读取（模拟）**
    *   **情景**：程序运行中。
    *   **操作**：按下键盘`UP`键。
    *   **预期结果**：控制台打印出增加的粒子数量（如“粒子数增加至: 550”），并且窗口中粒子数量**立即**增加。
    *   **解释**：验证交互逻辑（`on_key`回调）与渲染逻辑（`render_particles`）是实时联动的，这是后续所有交互的基础。

*   **测试用例3（负测试）：异常输入处理（规划）**
    *   **情景**：未来，当通过UI文本框输入粒子数时。
    *   **操作**：输入一个非数字（如“abc”）。
    *   **预期结果**：程序应能优雅处理，例如弹出警告，并保持上一个有效值，而不是崩溃。
    *   **解释**：好的程序需要对非法输入有鲁棒性。这个测试用例我们可以在后续加入UI时再实现。

---

### **六、 总结与课后任务（5分钟）**

**我们完成了什么？**
1.  ✅ 一个规范的项目仓库和Python环境。
2.  ✅ 一个能响应用户输入（键盘）的OpenGL窗口。
3.  ✅ 一个定义了核心属性的`Particle`类。
4.  ✅ 将数百个粒子成功渲染到屏幕上。
5.  ✅ 一次规范的Git提交，和明确的验收测试点。

**课后任务：**
1.  **巩固**：确保你本地环境能成功运行今天编写的所有代码。
2.  **探索**：尝试修改 `particle.py` 中粒子的初始位置或颜色，观察变化。
3.  **预习**：思考一下，如果我们想让这些粒子“动”起来（比如全部匀速向右移动），应该修改哪部分代码？如何修改？（提示：在 `render_particles` 之前更新粒子的 `position`）。

**下次课预告（12/19）：**
我们将进入激动人心的 **Stage 2：SPH算法核心实现**。让这些静止的粒子，在重力和彼此相互作用下，像真正的液体一样流动起来！请带着你对“如何让粒子动起来”的思考来上课。

**遇到问题随时在课程群里提问！**
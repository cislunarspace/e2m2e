# 引言

> 本文作者：[天疆说](https://gitee.com/cislunarspace)
>
> 本站地址：[https://cislunarspace.cn](https://cislunarspace.cn)

在学习和研究地月空间相关领域的内容时，首先面临的是资料查询问题。资料主要包括文献和各类数据，如星历数据等。对于中国学者而言，访问国外网站下载内容常存在障碍。因此，建立一个专门的地月空间资料库十分必要，该库能提供各类数据资源，便于研究人员查询与下载。

其次，各类工具的获取与使用也存在困难。例如，地月空间轨道设计与分析需使用STK、GMAT等专业软件，而这些工具对初学者而言门槛较高。建立专门的工具资源库，提供下载链接、使用教程和技术支持，有助于研究人员更高效地利用这些工具开展研究。

为实现研究落地，还需进行算法实现，这要求研究人员具备程序设计与编程能力。同时，借鉴开源代码至关重要。然而，根据观察，航空宇航科学与技术专业的本科生和研究生在学习过程中，普遍缺乏系统的程序设计与编程训练，对GitHub等平台上的开源代码学习与使用也不够熟悉。因此，该知识库还将提供高阶编程技巧，帮助研究人员提升编程能力，更好地开展地月空间相关的算法开发与应用。

## 代码库

### e2m2e

[e2m2e](https://gitee.com/cislunarspace/e2m2e)是一个基于圆型限制性三体问题（CR3BP）的Python库，专注于设计和分析地月空间转移轨道。

如下是示例调用：
```python
import e2m2e

# 1. 创建地月系统
system = e2m2e.CR3BP_System.from_known_system("earth_moon")
system.compute_libration_points()
system.set_characteristic_scales(distance=384400, period=27.32 * 86400)

print(f"地月系统: {system}")
print(f"L1点: {system.L1}")
print(f"L2点: {system.L2}")

# 2. 创建动力学对象
dynamics = e2m2e.CR3BP_Dynamics(system)

# 3. 设计Lyapunov轨道（微分修正）
dc = e2m2e.DifferentialCorrection(dynamics)
dc.setup_2D_symmetric_x_fixed_x0(x0=system.L1[0] + 0.01)

# 初始猜测
initial_state = [system.L1[0] + 0.01, 0, 0, 0, 0.1, 0]
orbit, result = dc.correct_orbit(initial_state, t_half=1.5)

if orbit is not None:
    print(f"Lyapunov轨道周期: {orbit.period:.4f}")

    # 4. 可视化
    viz = e2m2e.OrbitVisualizer(system)
    viz.create_overview_plot(orbit)
    viz.show()

# 5. 轨道族延拓
cont = e2m2e.Continuation(dc, param="x0", step=0.001)
family = cont.natural_continuation(
    seed_state=result['state'],
    seed_t_half=result['t_half'],
    n_orbits=20
)

# 6. 转移轨道设计
transfer = e2m2e.EarthMoonTransfer(system, dynamics)
# ... 设计具体的转移轨道
```

### scipy

scipy是一个Python科学计算库，提供了大量的数值算法和工具，广泛应用于地月空间轨道设计与分析中。

如下是安装命令：
```cmd
python -m pip install scipy
```

### r2s2

r2s2是一个地月空间时空坐标转换库。

如下是安装命令：
```cmd
python -m pip install r2s2
```


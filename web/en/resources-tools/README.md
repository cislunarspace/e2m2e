---
layout: Page
permalink: /en/resources-tools/
wechatShare:
  title: Cislunar Space Resources & Tools
  desc: One-stop learning for cislunar space research frontiers, terminology, and tool resources.
  image: /logo.png
---

> Author: [CislunarSpace](https://gitee.com/cislunarspace)
>
> Website: [https://cislunarspace.cn](https://cislunarspace.cn)

# Introduction

When studying and researching content related to cislunar space, the first challenge is finding reference materials. These mainly include literature and various types of data, such as ephemeris data. For Chinese scholars, accessing and downloading content from foreign websites often presents difficulties. Therefore, establishing a dedicated cislunar space data repository is essential — one that provides various data resources for researchers to query and download.

Secondly, the acquisition and use of various tools also presents challenges. For example, cislunar orbit design and analysis require professional software such as STK and GMAT, which have a steep learning curve for beginners. Establishing a dedicated tool resource repository with download links, usage tutorials, and technical support helps researchers utilize these tools more efficiently.

To translate research into practice, algorithm implementation is required, demanding programming and coding skills. At the same time, learning from open-source code is crucial. However, based on observation, undergraduate and graduate students in the field of Aeronautics, Astronautics, Science, and Technology generally lack systematic programming training and are unfamiliar with using open-source code on platforms like GitHub. Therefore, this knowledge base also provides advanced programming techniques to help researchers improve their coding skills and better carry out algorithm development and applications related to cislunar space.

## Code Libraries

### e2m2e

[e2m2e](https://gitee.com/cislunarspace/e2m2e) is a Python library based on the Circular Restricted Three-Body Problem (CR3BP), focused on designing and analyzing cislunar space transfer trajectories.

Here is an example usage:
```python
import e2m2e

# 1. Create the Earth-Moon system
system = e2m2e.CR3BP_System.from_known_system("earth_moon")
system.compute_libration_points()
system.set_characteristic_scales(distance=384400, period=27.32 * 86400)

print(f"Earth-Moon System: {system}")
print(f"L1 Point: {system.L1}")
print(f"L2 Point: {system.L2}")

# 2. Create dynamics object
dynamics = e2m2e.CR3BP_Dynamics(system)

# 3. Design Lyapunov orbit (differential correction)
dc = e2m2e.DifferentialCorrection(dynamics)
dc.setup_2D_symmetric_x_fixed_x0(x0=system.L1[0] + 0.01)

# Initial guess
initial_state = [system.L1[0] + 0.01, 0, 0, 0, 0.1, 0]
orbit, result = dc.correct_orbit(initial_state, t_half=1.5)

if orbit is not None:
    print(f"Lyapunov Orbit Period: {orbit.period:.4f}")

    # 4. Visualization
    viz = e2m2e.OrbitVisualizer(system)
    viz.create_overview_plot(orbit)
    viz.show()

# 5. Orbit family continuation
cont = e2m2e.Continuation(dc, param="x0", step=0.001)
family = cont.natural_continuation(
    seed_state=result['state'],
    seed_t_half=result['t_half'],
    n_orbits=20
)

# 6. Transfer trajectory design
transfer = e2m2e.EarthMoonTransfer(system, dynamics)
# ... design specific transfer trajectories
```

### scipy

scipy is a Python scientific computing library that provides a wide range of numerical algorithms and tools, widely used in cislunar orbit design and analysis.

Installation command:
```cmd
python -m pip install scipy
```

### r2s2

r2s2 is a cislunar space-time coordinate transformation library.

Installation command:
```cmd
python -m pip install r2s2
```

"""e2m2e.algorithm.forces 模块测试包。

按行为层分三个子包（对照 integrators 重构模式）：

- ``models/``：力模型个体行为（构造校验、``to_rust_spec`` 序列化契约、
  Rust 端到端传播物理）；
- ``container/``：ForceModel 容器编排行为（聚合/启停、传播边界、STM、
  机动编排、LEO 端到端场景）；
- ``config/``：配置驱动（``from_config`` / ``to_config`` 往返、
  摄动开关映射）。

共享基准物理（Datum.WGS84 常量、LEO 场景 fixture、开普勒转换工具）
集中在 ``conftest.py``。
"""

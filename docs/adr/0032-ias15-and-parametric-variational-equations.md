# ADR 0032：纳入 ASSIST 两项算法（IAS15 积分器、参数敏感变分方程），MERCURIUS 不纳入

**状态**：已采纳
**日期**：2026-08-26
**关联**：ADR 0002（Rust 积分器内核）、ADR 0018（力-雅可比三元组契约）、ADR 0020（显式失败）

## 背景

评估了两篇论文的算法对本仓的适用性：ASSIST（Holman et al. 2023，星历级
试验粒子积分器）与 MERCURIUS（Rein et al. 2019，混合辛积分器）。结论：
MERCURIUS 面向巨行星系统亿年尺度演化（Wisdom-Holman 分裂要求主导 Kepler
项 + 全相互作用有质量天体），与本仓「无质量航天器在地月空间飞任务时间
尺度」的问题域不匹配，其治的病（辛积分器近距交会发散）由现有自适应 RK
覆盖，**不纳入**。ASSIST 的技术栈与本仓同构（SPICE 星历 + N 体 + 高精度
力模型 + 变分方程），其中两项填补本仓真实空缺，**纳入**：

1. 现有积分器族（PD45/PD78/RK89、ABM、Cowell）没有高阶变阶预测-校正
   方法，也没有补偿求和；长弧段高精度外推（如轨道寿命分析）缺少
   Brouwer 律误差增长（n^1/2）的选项。
2. STM 传播只覆盖状态对初值的 6×6 偏导（ADR 0018），没有对力模型参数
   （Cr、Cd）的一阶偏导——测定轨与协方差传播需要它。低推力灵敏度已有
   A·S+B 结构（`augmented_state.rs`），但只接了控制参数。

许可证约束：ASSIST/REBOUND 为 GPL v3，本仓 Apache-2.0，不能引用其代码；
两文算法均按论文公开的数学描述自行实现。

## 决策

1. **IAS15 积分器进 `e2m2e-propagation`（`ias15.rs`）。**
   按 Rein & Spiegel (2015) 与 Everhart (1985) 的公开算法实现：8 个左
   Radau 节点（P₇+P₈ 的根，数值核对到机器精度）、Newton 基插值多项式 +
   逐节点 Gauss-Seidel 校正（≤12 扫描）、二阶双重积分（位置）+ 单积分
   （速度以外的额外一阶分量，STM/敏感列直接复用）、Neumaier-Kahan 补偿
   求和。与论文 b 系数基只差基变换，收敛不动点相同。
2. **参数敏感列纳入 STM 增广系统。** `CompiledForce` 增加
   `SensParam`（当前仅 `Cr`/`Cd`，两者与加速度严格线性，`∂a/∂p = a/p`
   解析）；`compiled_stm.rs` 增广维度扩为 `42 + 6·n_params`，每列满足
   `Ṡ = A·S + [0; ∂a/∂p]`，初值零。`sens` 为空时与旧 42 维路径逐位一致
   （原 `propagate_compiled_stm` 签名保留，委托新实现）。
3. **IAS15 的误差估计按状态更新量标定，并含噪声地板处理。** 最高阶项
   G₇ 经积分权重 `∫P₇`（Gauss-Radau 相消）折算成更新误差，而非节点值
   ——否则插值噪声地板（不随 h 下降）会被误判为截断误差导致死循环拒步。
   星历力模型（SPICE 求值、第三体直接/间接项相消）的加速度有效光滑度
   实测约 1e-11 相对量级，7 阶均差把它放大成不随步长下降的误差估计；
   连续拒步 eps 下降不足 2 倍即判定到达地板，把有效容差抬到地板上方
   接受并继续。纯解析力（点质量）无此地板，严格按 tol 控制。
4. **对外接缝。** Rust 绑定 `propagate_compiled_ias15_py`（with_stm 与
   sens_params 可选）与 `propagate_compiled_stm_py` 追加可选 `sens_params`
   （ABI 升至 v22）；Python 侧 `ForceModel.propagate` 新增
   `integrator="rk"|"ias15"` 与 `sens_params=["srp_cr"|"drag_cd"]`
   （需 `with_stm=True`；标签在 Python 层解析为 force 下标，歧义/缺失
   显式报错，遵守 ADR 0020）。

## 理由

- **IAS15 而不是再一张 Butcher 表**：RK 族加方法只需系数表，但变阶
  预测-校正对光滑解的效率与补偿求和的长弧舍入行为是 RK 给不了的；
  IAS15 的近距交会自缩步长由 ASSIST 的 Apophis 算例验证。
- **Newton 基自实现而非照抄系数表**：Everhart 的 c/d/r 递推系数与
  REBOUND 的硬编码常数都可用 Gauss-Legendre 积分从节点精确生成
  （被积函数 ≤8 次，16 点 GL 精确到舍入），自证正确且不碰 GPL 代码。
- **敏感列只收线性参数**：Cr/Cd 的 `∂a/∂p` 解析且精确（`a/p`），覆盖
  测定轨最主要的两个随机力模型误差源；非线性参数（如大气密度模型
  参数）需要数值差分列，等有真实需求再加（扩展点：`SensParam` 枚举 +
  `param_accel_derivative`）。
- **不跟随 ASSIST 的全 PPN / Marsden A1A2A3 / 太阳 J2**：中心天体 1PN
  （Schwarzschild + LT + de Sitter）本仓已有；全 PPN 的价值在小行星
  mas 级星历，Marsden 模型服务对象是彗星，太阳 J2 在地月空间可忽略
  ——均超出业务范围。

## 结果

### 新增

- `crates/e2m2e-propagation/src/ias15.rs`：IAS15 引擎（含 Kepler 解析解、
  e=0.9 整圈闭合、out-and-back、长弧能量等 Rust 单测）。
- `crates/e2m2e-forces/src/forces/compiled_ias15.rs`：编译力模型的 IAS15
  驱动（状态 / +STM / +敏感列，低推力开关机边界截断）。
- `SensParam` 与 `param_accel_derivative`（`compiled.rs`）；
  `propagate_compiled_stm_sens`（`compiled_stm.rs`）。
- 绑定 `propagate_compiled_ias15_py`，`propagate_compiled_stm_py` 加可选
  `sens_params`；ABI v22。
- `ForceModel.propagate(integrator=..., sens_params=...)`。
- 测试：`tests/numerical/integrators/methods/test_ias15.py`（解析解/守恒量/
  后端对照）、`tests/numerical/forces/container/test_force_model_sensitivity.py`
  （跨积分器敏感列一致 ~1e-12、shadow-particle FD 对照、契约报错）。

### 不变

- RK 族、ABM、Cowell 及既有传播路径行为（`sens` 为空逐位一致）。
- `ForceModel.propagate` 默认行为（`integrator="rk"`，无敏感列）。

### 取舍

- IAS15 在星历力模型下的有效精度被星历采样光滑度限制在 ~1e-11 相对
  量级（决策 3），纯解析力模型下不受限。追求更高精度需先解决星历
  取值链的光滑度，另行评估。
- 敏感列每条参数使增广维度 +6，STM 路径成本随之线性增长；Cr/Cd 同开
  为 54 维，可接受。

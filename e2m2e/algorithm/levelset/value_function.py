"""值函数网格的任意点值/梯度查询（#499，ADR 0032 决策 4）。

值函数落地后是 ``(时间快照, *状态网格)`` 形状的 numpy 数组。本模块提供
离网点查询：空间维用张量积局部三次插值（Lagrange 型，边界自动降阶），
梯度为**插值函数的解析导数**——不是"网格中心差分再插值"；时间维做线性
插值，必选。

精度口径：三次插值的值为 O(h⁴)、解析梯度为 O(h³)，相对中心差分的
O(h²) 高一阶以上；对不超过三次的多项式精确（机器精度）。

维度无关：接口不假设状态维数、物理含义与单位，2D 与 4D/5D 同一路径。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from e2m2e.exceptions import E2M2EError

if TYPE_CHECKING:
    import numpy.typing as npt

__all__ = ["ValueFunctionQueryError", "value_function_gradient"]

#: 空间插值最高阶数（三次）；网格维节点不足时自动降为 n-1 次
_MAX_DEGREE = 3


class ValueFunctionQueryError(E2M2EError, ValueError):
    """值函数查询越界（状态出网格、时间出时间轴）时抛出。

    同时继承 :class:`ValueError`，调用方可按值错误惯例捕获。
    """


def value_function_gradient(
    axes: tuple["npt.ArrayLike", ...],
    values: "npt.ArrayLike",
    times: "npt.ArrayLike",
    state: "npt.ArrayLike",
    time: float,
) -> tuple[float, "npt.NDArray[np.floating]"]:
    """查询值函数在任意状态与时刻的值与状态梯度。

    Args:
        axes: 各状态维网格坐标，长度 n 的元组；每个轴一维、严格递增、
            至少 2 个节点。
        values: 值函数数组，形状 ``(len(times), *grid_shape)``。
        times: 时间快照轴，一维严格递增。仅单快照时视为定常场——
            任意 ``time`` 均返回该快照结果，不做越界检查。
        state: 查询状态，形状 ``(n,)``，须落在各轴范围内。
        time: 查询时刻，须落在 ``times`` 范围内（单快照除外）。

    Returns:
        ``(value, gradient)``：标量值与形状 ``(n,)`` 的状态梯度。
        多快照时两相邻快照各自做空间插值再按时间线性混合。

    Raises:
        ValueFunctionQueryError: 状态出网格或时间出时间轴。
        ValueError: 输入形状或单调性不合法。
    """
    axes_np, values_np, times_np, state_np = _validate(axes, values, times, state)

    if times_np.size == 1:
        return _spatial_query(axes_np, values_np[0], state_np)

    if not (times_np[0] <= time <= times_np[-1]):
        raise ValueFunctionQueryError(
            f"时间 {time!r} 超出时间轴 [{times_np[0]!r}, {times_np[-1]!r}]"
        )
    hi = int(np.searchsorted(times_np, time, side="right"))
    lo = max(0, min(hi - 1, times_np.size - 2))
    hi = lo + 1
    alpha = float((time - times_np[lo]) / (times_np[hi] - times_np[lo]))

    value_lo, gradient_lo = _spatial_query(axes_np, values_np[lo], state_np)
    if alpha == 0.0:
        return value_lo, gradient_lo
    value_hi, gradient_hi = _spatial_query(axes_np, values_np[hi], state_np)
    return (
        (1.0 - alpha) * value_lo + alpha * value_hi,
        (1.0 - alpha) * gradient_lo + alpha * gradient_hi,
    )


def _validate(
    axes: tuple["npt.ArrayLike", ...],
    values: "npt.ArrayLike",
    times: "npt.ArrayLike",
    state: "npt.ArrayLike",
) -> tuple[
    tuple["npt.NDArray[np.floating]", ...],
    "npt.NDArray[np.floating]",
    "npt.NDArray[np.floating]",
    "npt.NDArray[np.floating]",
]:
    if not axes:
        raise ValueError("axes 不能为空")
    axes_np = tuple(np.asarray(axis, dtype=float) for axis in axes)
    for dim, axis in enumerate(axes_np):
        if axis.ndim != 1 or axis.size < 2:
            raise ValueError(f"axes[{dim}] 须为一维且至少 2 个节点")
        if not np.all(np.diff(axis) > 0):
            raise ValueError(f"axes[{dim}] 须严格递增")
        if not np.all(np.isfinite(axis)):
            raise ValueError(f"axes[{dim}] 含非有限值")

    values_np = np.asarray(values, dtype=float)
    grid_shape = tuple(axis.size for axis in axes_np)
    if values_np.ndim != len(axes_np) + 1 or values_np.shape[1:] != grid_shape:
        raise ValueError(
            f"values 形状须为 (len(times), {grid_shape})，当前 {values_np.shape}"
        )

    times_np = np.asarray(times, dtype=float)
    if times_np.ndim != 1 or times_np.size < 1:
        raise ValueError("times 须为一维非空")
    if values_np.shape[0] != times_np.size:
        raise ValueError(
            f"values 时间维 {values_np.shape[0]} 与 times 长度 {times_np.size} 不一致"
        )
    if times_np.size > 1 and not np.all(np.diff(times_np) > 0):
        raise ValueError("times 须严格递增")

    state_np = np.asarray(state, dtype=float).reshape(-1)
    if state_np.size != len(axes_np):
        raise ValueError(f"state 维数须为 {len(axes_np)}，当前 {state_np.size}")
    if not np.all(np.isfinite(state_np)):
        raise ValueError("state 含非有限值")
    return axes_np, values_np, times_np, state_np


def _spatial_query(
    axes: tuple["npt.NDArray[np.floating]", ...],
    snapshot: "npt.NDArray[np.floating]",
    state: "npt.NDArray[np.floating]",
) -> tuple[float, "npt.NDArray[np.floating]"]:
    """单时间快照的空间插值：返回值与该点解析梯度。"""
    stencils: list[tuple["npt.NDArray[np.intp]", "npt.NDArray[np.floating]", "npt.NDArray[np.floating]"]] = []
    for dim, (axis, coordinate) in enumerate(zip(axes, state, strict=True)):
        if not (axis[0] <= coordinate <= axis[-1]):
            raise ValueFunctionQueryError(
                f"状态第 {dim} 维坐标 {coordinate!r} 超出网格 [{axis[0]!r}, {axis[-1]!r}]"
            )
        stencils.append(_lagrange_stencil(axis, coordinate))

    block = snapshot[np.ix_(*[indices for indices, _, _ in stencils])]
    value = float(_contract(block, [weights for _, weights, _ in stencils]))
    gradient = np.empty(len(axes))
    for dim in range(len(axes)):
        mixed = [
            derivative if d == dim else weights
            for d, (_, weights, derivative) in enumerate(stencils)
        ]
        gradient[dim] = _contract(block, mixed)
    return value, gradient


def _lagrange_stencil(
    axis: "npt.NDArray[np.floating]", coordinate: float
) -> tuple["npt.NDArray[np.intp]", "npt.NDArray[np.floating]", "npt.NDArray[np.floating]"]:
    """取包含查询点的局部 Lagrange 模板，返回 (节点索引, 基函数权重, 基函数导数)。

    次数为 ``min(3, n-1)``；靠近边界时模板向网格外侧平移（不超出网格），
    保持次数不变。
    """
    n = axis.size
    degree = min(_MAX_DEGREE, n - 1)
    width = degree + 1

    hi = int(np.searchsorted(axis, coordinate, side="right"))
    start = hi - (width + 1) // 2
    start = max(0, min(start, n - width))
    nodes = axis[start : start + width]

    weights = np.ones(width)
    derivatives = np.zeros(width)
    for i in range(width):
        for j in range(width):
            if j == i:
                continue
            weights[i] *= (coordinate - nodes[j]) / (nodes[i] - nodes[j])
        # 导数：L_i'(x) = L_i(x) * Σ_{m≠i} 1/(x - x_m)；坐标与节点重合时
        # 退化为 Σ 消去法，直接对基函数展开求导更稳，此处用定义式：
        # L_i'(x) = Σ_{m≠i} [ Π_{j≠i,m} (x - x_j) ] / Π_{j≠i} (x_i - x_j)
        denominator = np.prod(nodes[i] - np.delete(nodes, i))
        total = 0.0
        for m in range(width):
            if m == i:
                continue
            keep = [j for j in range(width) if j != i and j != m]
            total += float(np.prod(coordinate - nodes[keep])) if keep else 1.0
        derivatives[i] = total / float(denominator)

    return np.arange(start, start + width, dtype=np.intp), weights, derivatives


def _contract(
    block: "npt.NDArray[np.floating]", weights: list["npt.NDArray[np.floating]"]
) -> float:
    """张量积求值：逐维把局部基函数权重收缩进模板块。"""
    out = block
    for w in weights:
        out = np.tensordot(w, out, axes=(0, 0))
    return float(out)

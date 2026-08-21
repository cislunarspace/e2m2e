//! CR3BP Hamiltonian 与 e2m2e-forces 解析动力学的对拍（issue #497 验收：
//! 零控向量场与 propagate_cr3bp_py 所用 CR3BP 动力学逐点一致）。
//!
//! propagate_cr3bp_py 的动力学内核是 e2m2e-forces 的 `cr3bp_eom`
//! （6 维，含 z 方向）。平面模型应与其 z = vz = 0 截面逐位一致。

use e2m2e_forces::cr3bp::{cr3bp_eom, propagate_cr3bp};
use e2m2e_hjb_dynamics::Cr3bpSynodic;

const MU_EARTH_MOON: f64 = 0.01215;

fn add_scaled(state: [f64; 4], k: [f64; 4], scale: f64) -> [f64; 4] {
    [
        state[0] + scale * k[0],
        state[1] + scale * k[1],
        state[2] + scale * k[2],
        state[3] + scale * k[3],
    ]
}

/// 随机（确定性伪随机）状态下，平面向量场等于 cr3bp_eom 的平面切片。
#[test]
fn vector_field_matches_cr3bp_eom_planar_slice() {
    let h = Cr3bpSynodic::new(MU_EARTH_MOON, 0.5, 0.1);
    for k in 0..200 {
        let s = |i: usize| ((k * 13 + i * 29) % 101) as f64 / 50.0 - 1.0;
        let state4 = [s(0) + 0.5, s(1), s(2), s(3)];
        let state6 = [state4[0], state4[1], 0.0, state4[2], state4[3], 0.0];
        let f4 = h.vector_field(state4);
        let f6 = cr3bp_eom(MU_EARTH_MOON, &state6);
        let planar6 = [f6[0], f6[1], f6[3], f6[4]];
        for d in 0..4 {
            assert!(
                (f4[d] - planar6[d]).abs() < 1e-14,
                "状态 {state4:?} 第 {d} 维：{} vs {}",
                f4[d],
                planar6[d]
            );
        }
    }
}

/// μ 取值敏感性：不同 μ 下两实现仍逐项一致（防止参数位置写反）。
#[test]
fn vector_field_parity_across_mu() {
    for mu in [0.01215, 0.1, 0.3] {
        let h = Cr3bpSynodic::new(mu, 0.5, 0.1);
        let state4 = [0.8, 0.2, -0.1, 0.4];
        let state6 = [state4[0], state4[1], 0.0, state4[2], state4[3], 0.0];
        let f4 = h.vector_field(state4);
        let f6 = cr3bp_eom(mu, &state6);
        assert!((f4[2] - f6[3]).abs() < 1e-14, "μ = {mu}");
        assert!((f4[3] - f6[4]).abs() < 1e-14, "μ = {mu}");
    }
}

/// 无控轨迹对拍（issue #497 验收：轨道周期对照）。同一初值传播一个会合
/// 周期 2π：本 crate 四维向量场用固定步长 RK4 积分，参考为
/// propagate_cr3bp（PD78 自适应，传播器实际使用的动力学路径），
/// 末态应一致。
#[test]
fn uncontrolled_trajectory_matches_propagator() {
    let h = Cr3bpSynodic::new(MU_EARTH_MOON, 0.5, 0.1);
    let state0 = [0.8, 0.0, 0.0, 0.4];
    let t_final = 2.0 * std::f64::consts::PI;

    let state6 = [state0[0], state0[1], 0.0, state0[2], state0[3], 0.0];
    let reference = propagate_cr3bp(
        MU_EARTH_MOON,
        (0.0, t_final),
        &[t_final],
        &state6,
        1e-12,
        1e-12,
        None,
        None,
    )
    .expect("参考传播应成功");
    let ref_state = reference.states.last().expect("至少一个输出点");

    // 固定步长 RK4，步长 2π/100000 ≈ 6.3e-5，全局截断误差远低于容差。
    let steps = 100_000usize;
    let dt = t_final / steps as f64;
    let mut s = state0;
    for _ in 0..steps {
        let k1 = h.vector_field(s);
        let k2 = h.vector_field(add_scaled(s, k1, dt / 2.0));
        let k3 = h.vector_field(add_scaled(s, k2, dt / 2.0));
        let k4 = h.vector_field(add_scaled(s, k3, dt));
        for d in 0..4 {
            s[d] += dt * (k1[d] + 2.0 * k2[d] + 2.0 * k3[d] + k4[d]) / 6.0;
        }
    }

    let planar_ref = [ref_state[0], ref_state[1], ref_state[3], ref_state[4]];
    for d in 0..4 {
        assert!(
            (s[d] - planar_ref[d]).abs() < 1e-8,
            "第 {d} 维：RK4 {} vs PD78 {}",
            s[d],
            planar_ref[d]
        );
    }
}

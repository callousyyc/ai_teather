"""降压电路从零启动: 看电感【电压】怎么跳、电感【电流】怎么爬、负载电压怎么慢慢建立。

关键: 电感电压不是电感自己"长"出来的, 而是两端电位相减: v_L = V_S - U
  V_S 由开关决定 (瞬间跳变), U 由电容托住 (变化很慢)
  -> v_L 跟着 V_S 瞬间跳; 真正"慢慢爬"的是电感电流 i_L
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.plotting import setup

E, D, f = 52.0, 0.6, 20e3          # 母线, 占空比, 开关频率
L, C, R = 200e-6, 100e-6, 1.0      # 电感, 输出电容, 负载电阻
T = 1 / f
dt = T / 400
t = np.arange(0, 4e-3, dt)

vs = np.where((t % T) < D * T, E, 0.0)   # 开关节点 (同步整流: 关断时下管导通, 接地)
iL = np.zeros_like(t); U = np.zeros_like(t); vL = np.zeros_like(t)
for k in range(len(t) - 1):
    vL[k] = vs[k] - U[k]                         # KVL: 电感电压 = 左端 - 右端
    iL[k + 1] = iL[k] + vL[k] / L * dt           # 电感: 电压决定电流的变化速度
    U[k + 1] = U[k] + (iL[k] - U[k] / R) / C * dt  # 电容: 电流差决定电压的变化速度
vL[-1] = vs[-1] - U[-1]

plt = setup()
fig = plt.figure(figsize=(8, 7.5))
a1 = fig.add_subplot(3, 1, 1)
a1.plot(t * 1e3, U, c="C4", label="负载电压 U")
a1.axhline(D * E, ls="--", c="r", label=f"D·E = {D*E:.1f} V")
a1.set_ylabel("U / V"); a1.legend(loc="lower right")
a1.set_title("① 从零启动：负载电压要几十个周期才慢慢建立到 31.2V（这段叫“暂态”，不是稳态）")
a1.axvspan(0, 0.15, color="orange", alpha=0.2); a1.axvspan(3.85, 4.0, color="green", alpha=0.2)
a1.set_xlabel("t / ms")


def zoom(ax_v, ax_i, t0, title):
    m = (t >= t0) & (t < t0 + 3 * T)
    tt = (t[m] - t0) * 1e6
    ax_v.plot(tt, vs[m], c="C0", alpha=0.5, label="开关节点 V_S")
    ax_v.plot(tt, vL[m], c="C1", lw=2, label="电感电压 v_L")
    ax_v.plot(tt, U[m], c="C4", label="负载电压 U")
    ax_v.axhline(0, c="k", lw=0.8); ax_v.set_ylim(-40, 58); ax_v.set_ylabel("V")
    ax_v.set_title(title, fontsize=10); ax_v.legend(loc="lower right", fontsize=7)
    ax_i.plot(tt, iL[m], c="C3"); ax_i.set_ylabel("电感电流 i_L / A"); ax_i.set_xlabel("t / µs")


zoom(fig.add_subplot(3, 2, 3), fig.add_subplot(3, 2, 5), 0.0,
     "② 刚启动（橙色区）：U≈0，v_L 在 +52/0 之间跳\n正面积 远大于 负面积 → 电流一个周期比一个周期大")
zoom(fig.add_subplot(3, 2, 4), fig.add_subplot(3, 2, 6), 4e-3 - 3 * T,
     "③ 稳态（绿色区）：v_L 在 +20.8/−31.2 之间跳\n正面积 = 负面积 → 电流每周期回到原值")
fig.tight_layout()
out = Path(__file__).with_suffix(".png"); fig.savefig(out); print(out)
m = t > 3.85e-3
print("steady U avg %.2f  vL hi %.1f lo %.1f  iL avg %.1f" % (U[m].mean(), vL[m].max(), vL[m].min(), iL[m].mean()))

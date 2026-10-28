"""伏秒平衡 = 电感电压的平均值为 0。
开关节点电压 V_S = 电感电压 v_L + 负载电压 U, 电感"扛"走跳变的部分, 负载只剩平均值。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.plotting import setup

E, D, T = 52.0, 0.6, 1.0           # 母线电压, 占空比, 周期(归一化)
U = D * E                          # 稳态负载电压
t = np.linspace(0, 2 * T, 2000)
on = (t % T) < D * T
vs = np.where(on, E, 0.0)
vl = vs - U                        # KVL: v_L = V_S - U

plt = setup()
fig, ax = plt.subplots(3, 1, sharex=True, figsize=(7.5, 6))
ax[0].plot(t, vs); ax[0].axhline(vs.mean(), ls="--", c="r", label=f"平均 = {vs.mean():.1f} V")
ax[0].set_ylabel("V_S / V"); ax[0].set_title("① 开关节点电压 V_S（52V / 0V 跳变）"); ax[0].legend(loc="upper right")
ax[1].plot(t, vl, c="C1")
ax[1].fill_between(t, vl, 0, where=vl > 0, color="C2", alpha=0.35, label=f"正面积 {E-U:.1f}V × {D}T = {(E-U)*D:.2f}")
ax[1].fill_between(t, vl, 0, where=vl < 0, color="C3", alpha=0.35, label=f"负面积 {U:.1f}V × {1-D:.1f}T = {U*(1-D):.2f}")
ax[1].axhline(0, c="k", lw=0.8); ax[1].set_ylabel("v_L / V")
ax[1].set_title("② 电感电压 v_L：正面积 = 负面积 → 平均值 = 0（伏秒平衡）"); ax[1].legend(loc="lower right", fontsize=8)
ax[2].plot(t, np.full_like(t, U), c="C4"); ax[2].set_ylim(0, 60)
ax[2].set_ylabel("U / V"); ax[2].set_xlabel("t / T")
ax[2].set_title(f"③ 负载电压 U = V_S − v_L = {U:.1f} V（每个瞬间都一样）")
fig.tight_layout()
out = Path(__file__).with_suffix(".png"); fig.savefig(out); print(out)

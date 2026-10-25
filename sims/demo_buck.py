"""降压斩波电路 (Buck) 理想波形: 改 D、L 看电感电流纹波变化。"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.plotting import setup

E, D, L, R, f = 100.0, 0.4, 1e-3, 10.0, 20e3   # 电源电压, 占空比, 电感, 负载, 开关频率
T = 1 / f
Uo = D * E                       # 理想输出电压 Uo = D·E
Io = Uo / R
dI = (E - Uo) * D * T / L        # 电感电流峰峰纹波

t = np.linspace(0, 3 * T, 3000)
phase = (t % T) / T
uo = np.where(phase < D, E, 0.0)  # 二极管两端电压 (斩波输出)
iL = np.where(phase < D, Io - dI / 2 + dI * phase / D, Io + dI / 2 - dI * (phase - D) / (1 - D))

plt = setup()
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7, 4.5))
ax[0].plot(t * 1e6, uo); ax[0].axhline(Uo, ls="--", c="r", label=f"平均值 Uo = D·E = {Uo:.0f} V")
ax[0].set_ylabel("u_o / V"); ax[0].legend(loc="upper right"); ax[0].set_title(f"降压斩波  E={E:.0f}V  D={D}  L={L*1e3:.0f}mH")
ax[1].plot(t * 1e6, iL, c="C1"); ax[1].set_ylabel("i_L / A"); ax[1].set_xlabel("t / μs")
ax[1].set_title(f"电感电流纹波 ΔI = {dI:.2f} A")
fig.tight_layout()
out = Path(__file__).with_suffix(".png")
fig.savefig(out)
print(out)

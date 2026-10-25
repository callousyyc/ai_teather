"""M1.1 电感: 电压决定的是电流的"变化速度", 不是电流本身。

就像嵌入式里每个 tick 做一次累加: i += (v / L) * dt
改 L、V、T_ON 看电流斜率和纹波怎么变。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.plotting import setup

L = 100e-6      # 电感 100 µH (ebike 轮毂电机一相电感的量级)
V = 24.0        # 导通时加在电感上的电压 / V
T_ON = 10e-6    # 每段持续 10 µs
dt = 0.05e-6

t = np.arange(0, 5 * T_ON, dt)
seg = (t // T_ON).astype(int)
v = np.select([seg == 0, seg == 1, seg == 2, seg == 3], [V, 0.0, -V, V], 0.0)

i = np.zeros_like(t)
for k in range(1, len(t)):          # 电感方程的离散形式: 电流 = 电压的累加
    i[k] = i[k - 1] + v[k - 1] / L * dt

plt = setup()
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(7, 4.5))
ax[0].step(t * 1e6, v, where="post"); ax[0].set_ylabel("v_L / V")
ax[0].set_title(f"加在电感上的电压   L = {L*1e6:.0f} µH")
for k, txt in enumerate(["+24V", "0V", "-24V", "+24V", "0V"]):
    ax[0].text((k + 0.5) * T_ON * 1e6, 27, txt, ha="center")
ax[0].set_ylim(-30, 34)
ax[1].plot(t * 1e6, i, c="C1"); ax[1].set_ylabel("i_L / A"); ax[1].set_xlabel("t / µs")
ax[1].set_title(f"电感电流: 每 10 µs 变化 ΔI = V·Δt / L = {V*T_ON/L:.1f} A")
fig.tight_layout()
out = Path(__file__).with_suffix(".png")
fig.savefig(out)
print(out, "dI =", V * T_ON / L)

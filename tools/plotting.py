"""画波形用的公共设置: 中文字体、负号显示、统一风格。

    from tools.plotting import setup
    plt = setup()
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def setup():
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.alpha"] = 0.3
    plt.rcParams["figure.dpi"] = 110
    return plt

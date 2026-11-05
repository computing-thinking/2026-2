"""10주차 문제 4 그림 두 장을 강의자료 폴더에 만든다.

    컴퓨팅사고_10주차_다리_지도.png   쾨니히스베르크 지도 (생각하기 판·풀이판 공용)
    컴퓨팅사고_10주차_다리_그래프.png  왼쪽: 지도 위에 오일러가 그린 점과 선 / 오른쪽: 점 4개 · 선 7개만 남긴 그래프 (풀이판)

    python tools/draw_w10_bridges.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Rectangle, FancyArrowPatch, PathPatch
from matplotlib.path import Path

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
TEAL, CORAL, GRAY, DARK = "#0EA5A4", "#FF6B5A", "#6B7280", "#1F2937"
WATER, LAND, LAND_EDGE, BRIDGE = "#BFE3F5", "#F5E6C8", "#C9A96E", "#8B5A2B"

# 땅의 중심(정점 자리)과 다리 (가로 중심, 세로 중심, 너비, 높이) — 다리는 양쪽 땅 안까지 들어가게 길게 그린다
CENTER = {"N": (5, 6.0), "S": (5, 1.0), "W": (3.2, 3.5), "E": (9.0, 3.5)}
BRIDGES = [("N", "W", 2.3, 4.65, 0.38, 1.0), ("N", "W", 4.1, 4.65, 0.38, 1.0),   # ① ②
           ("S", "W", 2.3, 2.35, 0.38, 1.0), ("S", "W", 4.1, 2.35, 0.38, 1.0),   # ③ ④
           ("N", "E", 8.6, 4.4, 0.38, 0.9), ("S", "E", 8.6, 2.6, 0.38, 0.9),     # ⑤ ⑥
           ("W", "E", 5.6, 3.5, 2.0, 0.34)]                                      # ⑦


def draw_map(ax, overlay=False):
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 7, fc=WATER, ec="none", zorder=0))
    land = dict(fc=LAND, ec=LAND_EDGE, lw=2, zorder=2)
    ax.add_patch(Polygon([(0, 7), (10, 7), (10, 4.9), (7.4, 4.4), (5.6, 4.9), (3.2, 5.0), (0.9, 4.7), (0, 4.9)], closed=True, **land))
    ax.add_patch(Polygon([(0, 0), (10, 0), (10, 2.1), (7.4, 2.6), (5.6, 2.1), (3.2, 2.0), (0.9, 2.3), (0, 2.1)], closed=True, **land))
    ax.add_patch(Ellipse((3.2, 3.5), 3.0, 1.9, **land))
    ax.add_patch(Polygon([(10, 2.75), (10, 4.25), (7.9, 4.0), (6.4, 3.5), (7.9, 3.0)], closed=True, **land))
    for k, (a, b, x, y, w, h) in enumerate(BRIDGES, 1):
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=BRIDGE, ec=DARK, lw=1.2, zorder=5))
        if not overlay:
            ax.text(x, y, "①②③④⑤⑥⑦"[k - 1], ha="center", va="center", color="white", fontsize=12, fontweight="bold", zorder=7)
    ax.text(0.3, 3.5, "강", color="#2B6CB0", fontsize=14, fontweight="bold", ha="left", va="center", zorder=6)
    if overlay:
        for a, b, x, y, w, h in BRIDGES:                       # 다리 가운데를 지나는 곡선 = 변
            p0, p2 = CENTER[a], CENTER[b]
            c = (2 * x - (p0[0] + p2[0]) / 2, 2 * y - (p0[1] + p2[1]) / 2)
            ax.add_patch(PathPatch(Path([p0, c, p2], [Path.MOVETO, Path.CURVE3, Path.CURVE3]), fc="none", ec=CORAL, lw=3.2, zorder=8))
        for v, (x, y) in CENTER.items():                       # 땅의 중심 = 정점
            ax.add_patch(Ellipse((x, y), 0.8, 0.8, fc=TEAL, ec=DARK, lw=1.5, zorder=9))
            ax.text(x, y, v, ha="center", va="center", color="white", fontsize=15, fontweight="bold", zorder=10)
    else:
        t = dict(ha="center", va="center", color=DARK, fontsize=15, fontweight="bold", zorder=6)
        ax.text(5, 6.0, "북쪽 땅  N", **t); ax.text(5, 1.0, "남쪽 땅  S", **t)
        ax.text(3.2, 3.5, "섬  W", **t); ax.text(9.0, 3.5, "동쪽 땅  E", **t)
        ax.text(9.85, 6.75, "다리: N–W ①②  S–W ③④  N–E ⑤  S–E ⑥  W–E ⑦", ha="right", va="top", color=GRAY, fontsize=10.5, zorder=6,
                bbox=dict(fc="white", ec=LAND_EDGE, lw=1, boxstyle="round,pad=0.35"))


def draw_graph(ax):
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.set_aspect("equal"); ax.axis("off")
    P = {"N": (5, 6.0), "S": (5, 1.0), "W": (1.8, 3.5), "E": (8.4, 3.5)}
    edges = [("N", "W", 0.35), ("N", "W", -0.35), ("S", "W", 0.35), ("S", "W", -0.35), ("N", "E", 0), ("S", "E", 0), ("W", "E", 0)]
    for a, b, rad in edges:
        ax.add_patch(FancyArrowPatch(P[a], P[b], connectionstyle=f"arc3,rad={rad}", arrowstyle="-", color=GRAY, lw=3, zorder=1,
                                     shrinkA=22, shrinkB=22))
    deg = {"N": 3, "W": 5, "E": 3, "S": 3}
    for v, (x, y) in P.items():
        ax.add_patch(Ellipse((x, y), 0.9, 0.9, fc=TEAL, ec=DARK, lw=1.5, zorder=3))
        ax.text(x, y, v, ha="center", va="center", color="white", fontsize=17, fontweight="bold", zorder=4)
        dx, dy = {"N": (0.9, 0.3), "S": (0.9, -0.3), "W": (-0.3, 0.85), "E": (0.3, 0.85)}[v]
        ax.text(x + dx, y + dy, f"차수 {deg[v]}", ha="center", va="center", color=CORAL, fontsize=12.5, fontweight="bold", zorder=4)


def fig_map():
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=120)
    draw_map(ax)
    fig.suptitle("쾨니히스베르크 — 땅 4 곳과 다리 7 개", color=TEAL, fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.03, "다리 7 개를 모두 정확히 한 번씩만 건너는 산책길이 있을까?", ha="center", color=CORAL, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_10주차_다리_지도.png"), facecolor="white")


def fig_graph():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.6), dpi=120)
    draw_map(ax1, overlay=True); draw_graph(ax2)
    ax1.set_title("① 오일러의 그림 — 땅마다 점 하나, 다리마다 선 하나", color=TEAL, fontsize=14, fontweight="bold", pad=10)
    ax2.set_title("② 지도를 지우면 — 정점 4 개와 변 7 개의 그래프", color=TEAL, fontsize=14, fontweight="bold", pad=10)
    fig.text(0.5, 0.03, "땅의 모양 · 다리의 길이 · 강의 폭은 사라졌지만 ‘어느 땅이 어느 땅과 몇 개의 다리로 이어지나’는 그대로입니다",
             ha="center", color=GRAY, fontsize=12.5)
    fig.subplots_adjust(top=0.9, bottom=0.1, left=0.02, right=0.98, wspace=0.06)
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_10주차_다리_그래프.png"), facecolor="white")


if __name__ == "__main__":
    fig_map(); fig_graph(); print("저장 완료")

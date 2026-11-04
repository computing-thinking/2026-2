"""10주차 문제 4 그림 두 장을 강의자료 폴더에 만든다.

    컴퓨팅사고_10주차_다리_지도.png   쾨니히스베르크 지도 (생각하기 판·풀이판 공용)
    컴퓨팅사고_10주차_다리_그래프.png  점 4개 · 선 7개로 추상화한 그래프 (풀이판)

    python tools/draw_w10_bridges.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon, Rectangle, FancyArrowPatch

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
TEAL, CORAL, GRAY, DARK = "#0EA5A4", "#FF6B5A", "#6B7280", "#1F2937"
WATER, LAND, LAND_EDGE, BRIDGE = "#BFE3F5", "#F5E6C8", "#C9A96E", "#8B5A2B"


def bridge(ax, x, y, w, h):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=BRIDGE, ec=DARK, lw=1.2, zorder=5))


def draw_map():
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=120)
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 10, 7, fc=WATER, ec="none", zorder=0))
    land = dict(fc=LAND, ec=LAND_EDGE, lw=2, zorder=2)
    ax.add_patch(Polygon([(0, 7), (10, 7), (10, 4.9), (7.4, 4.4), (5.6, 4.9), (3.2, 5.0), (0.9, 4.7), (0, 4.9)], closed=True, **land))
    ax.add_patch(Polygon([(0, 0), (10, 0), (10, 2.1), (7.4, 2.6), (5.6, 2.1), (3.2, 2.0), (0.9, 2.3), (0, 2.1)], closed=True, **land))
    ax.add_patch(Ellipse((3.2, 3.5), 3.0, 1.9, **land))
    ax.add_patch(Polygon([(10, 2.75), (10, 4.25), (7.9, 4.0), (6.4, 3.5), (7.9, 3.0)], closed=True, **land))
    spots = [(2.3, 4.35, 0.38, 0.75), (4.1, 4.35, 0.38, 0.75),      # ① ② N–W
             (2.3, 2.65, 0.38, 0.75), (4.1, 2.65, 0.38, 0.75),      # ③ ④ S–W
             (8.6, 4.35, 0.38, 0.75), (8.6, 2.65, 0.38, 0.75),      # ⑤ N–E  ⑥ S–E
             (5.6, 3.5, 1.1, 0.34)]                                 # ⑦ W–E
    for k, (x, y, w, h) in enumerate(spots, 1):
        bridge(ax, x, y, w, h)
        ax.text(x, y, "①②③④⑤⑥⑦"[k - 1], ha="center", va="center", color="white", fontsize=12, fontweight="bold", zorder=7)
    ax.text(9.85, 6.75, "다리: N–W ①②  S–W ③④  N–E ⑤  S–E ⑥  W–E ⑦", ha="right", va="top", color=GRAY, fontsize=10.5, zorder=6,
            bbox=dict(fc="white", ec=LAND_EDGE, lw=1, boxstyle="round,pad=0.35"))
    t = dict(ha="center", va="center", color=DARK, fontsize=15, fontweight="bold", zorder=6)
    ax.text(5, 6.0, "북쪽 땅  N", **t); ax.text(5, 1.0, "남쪽 땅  S", **t)
    ax.text(3.2, 3.5, "섬  W", **t); ax.text(9.0, 3.5, "동쪽 땅  E", **t)
    ax.text(0.3, 3.5, "강", color="#2B6CB0", fontsize=14, fontweight="bold", ha="left", va="center", zorder=6)
    fig.suptitle("쾨니히스베르크 — 땅 4 곳과 다리 7 개", color=TEAL, fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.03, "다리 7 개를 모두 정확히 한 번씩만 건너는 산책길이 있을까?", ha="center", color=CORAL, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_10주차_다리_지도.png"), facecolor="white")


def draw_graph():
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=120)
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
    fig.suptitle("다시 그린 문제 — 정점 4 개와 변 7 개의 그래프", color=TEAL, fontsize=16, fontweight="bold", y=0.98)
    fig.text(0.5, 0.03, "땅은 점으로, 다리는 선으로. 땅의 모양·다리의 길이·강의 폭은 지웠다", ha="center", color=GRAY, fontsize=12.5)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_10주차_다리_그래프.png"), facecolor="white")


if __name__ == "__main__":
    draw_map(); draw_graph(); print("저장 완료")

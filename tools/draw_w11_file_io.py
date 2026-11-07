"""11주차 1-2 그림 — 파일을 열고 · 쓰고 · 닫는 세 단계를 강의자료 폴더에 PNG 로 만든다.

    컴퓨팅사고_11주차_파일_열고닫기.png
      ① open()  : 프로그램과 디스크의 파일 사이에 통로(파일 객체 f)가 연결된다. 통로 안에 버퍼(임시 바구니)가 있다
      ② write() : 쓴 내용은 먼저 버퍼에 쌓인다. 디스크의 파일은 아직 비어 있다
      ③ close() : 버퍼에 남은 것을 디스크로 보내고 통로를 끊는다. 이제야 파일에 내용이 있다

    python tools/draw_w11_file_io.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
TEAL, CORAL, GRAY, DARK, AMBER = "#0EA5A4", "#FF6B5A", "#6B7280", "#1F2937", "#F59E0B"
PALE_TEAL, PALE_GRAY, PALE_AMBER, DISK = "#E6F7F6", "#F3F4F6", "#FFF7E6", "#DDE3EA"


def box(ax, x, y, w, h, text, fc, ec, fs=11, bold=False, color=DARK, lw=1.8, style="round,pad=0.02,rounding_size=0.25"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=lw, zorder=3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color,
            fontweight="bold" if bold else "normal", zorder=4, linespacing=1.5)


def disk(ax, x, y, w, h, title, lines, empty_note=None):
    """디스크 위의 파일 — 원통 느낌의 상자 위에 파일 아이콘"""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=DISK, ec=GRAY, lw=1.8, zorder=3))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="center", fontsize=10, color=GRAY, fontweight="bold", zorder=4)
    # 파일 문서 모양
    fx, fy, fw, fh = x + 0.35, y + 0.35, w - 0.7, h - 1.0
    ax.add_patch(Rectangle((fx, fy), fw, fh, fc="white", ec=DARK, lw=1.4, zorder=4))
    ax.text(fx + fw / 2, fy + fh - 0.28, "memo.txt", ha="center", va="center", fontsize=9.5, color=DARK, fontweight="bold", zorder=5)
    ax.plot([fx + 0.2, fx + fw - 0.2], [fy + fh - 0.5] * 2, color=GRAY, lw=0.8, zorder=5)
    if lines:
        for i, ln in enumerate(lines):
            ax.text(fx + 0.2, fy + fh - 0.85 - 0.42 * i, ln, ha="left", va="center", fontsize=8.5, color=DARK, zorder=5)
    elif empty_note:
        ax.text(fx + fw / 2, fy + fh / 2 - 0.2, empty_note, ha="center", va="center", fontsize=8.5, color=CORAL, zorder=5, linespacing=1.4)


def pipe(ax, x0, x1, y, h, connected, buffer_lines, label):
    """프로그램과 파일 사이의 통로(파일 객체). 안에 버퍼 상자"""
    if connected:
        ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, fc=PALE_TEAL, ec=TEAL, lw=1.8, zorder=2))
        ax.text((x0 + x1) / 2, y + h / 2 + 0.22, label, ha="center", va="bottom", fontsize=10, color=TEAL, fontweight="bold", zorder=4)
    else:
        ax.add_patch(Rectangle((x0, y - h / 2), x1 - x0, h, fc="none", ec=GRAY, lw=1.4, ls=(0, (4, 3)), zorder=2))
        ax.text((x0 + x1) / 2, y + h / 2 + 0.22, label, ha="center", va="bottom", fontsize=10, color=GRAY, zorder=4)
    # 버퍼
    bw, bh = 2.3, h - 0.5
    bx, by = (x0 + x1) / 2 - bw / 2, y - bh / 2
    ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=PALE_AMBER if buffer_lines else "white", ec=AMBER if connected else GRAY, lw=1.4, zorder=3))
    ax.text(bx + bw / 2, by + bh - 0.22, "버퍼 (임시 바구니)", ha="center", va="center", fontsize=8.5, color=AMBER if connected else GRAY, zorder=4)
    for i, ln in enumerate(buffer_lines):
        ax.text(bx + bw / 2, by + bh - 0.6 - 0.38 * i, ln, ha="center", va="center", fontsize=8.5, color=DARK, zorder=4)
    if connected and not buffer_lines:
        ax.text(bx + bw / 2, by + bh / 2 - 0.15, "(비어 있음)", ha="center", va="center", fontsize=8.5, color=GRAY, zorder=4)


def arrow(ax, p, q, color, text=None, ty=0.3, lw=2.2, style="-|>"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=18, color=color, lw=lw, zorder=6))
    if text:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + ty, text, ha="center", va="center", fontsize=9.5, color=color, fontweight="bold", zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))


def panel(ax, step, title, code, connected, buffer_lines, file_lines, empty_note, arrows, closed_badge=False):
    ax.set_xlim(0, 10); ax.set_ylim(-0.7, 6.2); ax.set_aspect("equal"); ax.axis("off")
    # 제목 띠
    ax.add_patch(FancyBboxPatch((0.15, 5.35), 9.7, 0.7, boxstyle="round,pad=0.02,rounding_size=0.2", fc=DARK, ec="none", zorder=3))
    ax.text(0.55, 5.7, step, ha="center", va="center", fontsize=12, color=DARK, fontweight="bold", zorder=5,
            bbox=dict(boxstyle="circle,pad=0.25", fc=AMBER, ec="none"))
    ax.text(1.1, 5.7, title, ha="left", va="center", fontsize=12, color="white", fontweight="bold", zorder=4)
    ax.text(9.7, 5.7, code, ha="right", va="center", fontsize=10.5, color="#F9FAFB", zorder=4)
    # 프로그램(왼쪽) · 통로 · 디스크(오른쪽)
    box(ax, 0.3, 1.3, 2.2, 2.6, "프로그램\n(메모리)", PALE_GRAY, DARK, fs=11, bold=True)
    pipe(ax, 2.5, 7.3, 2.6, 1.9, connected, buffer_lines, "파일 객체 f  — 통로" if connected else "통로 없음")
    disk(ax, 7.3, 0.6, 2.5, 3.9, "디스크", file_lines, empty_note)
    for a in arrows:
        arrow(ax, *a)
    if closed_badge:
        ax.text(4.9, 0.4, "f.closed == True", ha="center", va="center", fontsize=9.5, color=TEAL, family="Consolas",
                bbox=dict(boxstyle="round,pad=0.3", fc=PALE_TEAL, ec=TEAL))


def main():
    fig, axes = plt.subplots(3, 1, figsize=(9.6, 16.5))
    panel(axes[0], "①", "열기 — 통로를 만든다", 'f = open("memo.txt", "w")', True, [], [], "(비어 있음)", [])
    panel(axes[1], "②", "쓰기 — 버퍼에 쌓인다", 'f.write("첫 줄입니다\\n")', True, ["첫 줄입니다", "둘째 줄입니다"], [], "아직\n비어 있음!",
          [((2.5, 2.6), (3.6, 2.6), CORAL, None), ((6.2, 2.6), (7.3, 2.6), GRAY, "아직 안 감", 0.45, 1.6, "-")])
    panel(axes[2], "③", "닫기 — 버퍼를 비우고 통로를 끊는다", "f.close()", False, [], ["첫 줄입니다", "둘째 줄입니다"], None,
          [((6.2, 2.6), (7.3, 2.6), TEAL, "디스크로!", 0.45)], closed_badge=True)
    axes[0].text(4.9, -0.3, "open() 이 프로그램과 디스크의 파일 사이에 통로를 만들고, 이름표 f 를 붙입니다", ha="center", va="center", fontsize=9.5, color=TEAL)
    axes[1].text(3.05, 3.15, "write()", ha="center", va="bottom", fontsize=9.5, color=CORAL, fontweight="bold", family="Consolas")
    axes[1].text(4.9, -0.3, "write() 는 디스크가 아니라 버퍼에 씁니다. 디스크는 느리니 모아서 한 번에 보내려는 것입니다", ha="center", va="center", fontsize=9.5, color=CORAL)
    axes[2].text(4.9, -0.3, "close() 가 버퍼에 남은 것을 디스크로 보내고 통로를 끊습니다. 닫지 않으면 버퍼의 내용이 디스크에 없을 수 있습니다", ha="center", va="center", fontsize=9.5, color=GRAY)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.08)
    out = os.path.join(DEST, "컴퓨팅사고_11주차_파일_열고닫기.png")
    fig.savefig(out, dpi=110, facecolor="white")
    print("saved", os.path.normpath(out))


if __name__ == "__main__":
    main()

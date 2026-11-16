import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 12주차 그림 두 장을 강의자료 폴더에 PNG 로 만든다. build_w12 가 base64 로 본문에 넣는다.
#   컴퓨팅사고_12주차_학습과추론.png  — 학습(데이터 → 모델 조정) 과 추론(새 입력 → 답) 두 단계
#   컴퓨팅사고_12주차_RNN펼침.png     — 단어를 한 개씩 읽으며 메모(h)를 갱신하는 RNN 을 시간 순서로 펼친 그림
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
TEAL, CORAL, GRAY, DARK, AMBER = "#0EA5A4", "#FF6B5A", "#6B7280", "#1F2937", "#F59E0B"


def box(ax, x, y, w, h, text, fc, ec=None, tc="#FFFFFF", fs=12, bold=True, style="round,pad=0.02,rounding_size=0.12"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec or fc, lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs,
            fontweight="bold" if bold else "normal", linespacing=1.5)


def arrow(ax, x0, y0, x1, y1, color=DARK, lw=2, label=None, lx=0, ly=0.18, fs=10):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=18, color=color, lw=lw))
    if label:
        ax.text((x0 + x1) / 2 + lx, (y0 + y1) / 2 + ly, label, ha="center", va="center", color=color, fontsize=fs)


def draw_train_infer():
    fig, ax = plt.subplots(figsize=(11, 5.2), dpi=130)
    ax.set_xlim(0, 11); ax.set_ylim(0, 5.2); ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    # ── 위: 학습 ──
    ax.text(0.2, 4.85, "① 학습 (training) — 데이터로 모델 안의 숫자를 맞춰 간다", color=TEAL, fontsize=13, fontweight="bold")
    box(ax, 0.3, 3.3, 2.3, 1.1, "훈련 데이터\n문서 + 정답(레이블)", "#E6F7F6", TEAL, DARK, 11)
    box(ax, 3.6, 3.3, 2.0, 1.1, "모델\n(매개변수 w)", TEAL, None, "#FFFFFF", 12)
    box(ax, 6.6, 3.3, 1.7, 1.1, "예측", "#F3F4F6", GRAY, DARK, 12)
    box(ax, 9.0, 3.3, 1.7, 1.1, "손실\n(틀린 정도)", "#FFF0EE", CORAL, DARK, 11)
    arrow(ax, 2.6, 3.85, 3.6, 3.85, label="문서", ly=0.2)
    arrow(ax, 5.6, 3.85, 6.6, 3.85)
    arrow(ax, 8.3, 3.85, 9.0, 3.85, label="정답과 비교", ly=0.3, fs=9)
    # 되돌아가는 화살표 (손실 → 모델 조정)
    ax.add_patch(FancyArrowPatch((9.85, 3.3), (4.6, 3.3), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>",
                                 mutation_scale=18, color=CORAL, lw=2, ls="--"))
    ax.text(7.2, 2.05, "손실이 줄어드는 쪽으로 w 를 조금씩 고친다 — 에포크마다 반복", color=CORAL, fontsize=10, ha="center")
    # ── 아래: 추론 ──
    ax.text(0.2, 1.75, "② 추론 (inference) — 다 배운 모델에 새 입력을 넣어 답을 받는다", color=DARK, fontsize=13, fontweight="bold")
    box(ax, 0.3, 0.25, 2.3, 1.1, "새 문서\n(정답 없음)", "#F3F4F6", GRAY, DARK, 11)
    box(ax, 3.6, 0.25, 2.0, 1.1, "학습된 모델\n(w 고정)", TEAL, None, "#FFFFFF", 12)
    box(ax, 6.6, 0.25, 1.7, 1.1, "주제", AMBER, None, DARK, 13)
    arrow(ax, 2.6, 0.8, 3.6, 0.8)
    arrow(ax, 5.6, 0.8, 6.6, 0.8, label="예측", ly=0.2)
    ax.text(9.0, 0.8, "“스포츠”  “경제”\n“날씨”  “음식”", color=GRAY, fontsize=11, ha="center", va="center")
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_12주차_학습과추론.png"), bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)


def draw_rnn():
    words = ["손흥민", "두", "골", "역전승"]
    n = len(words)
    fig, ax = plt.subplots(figsize=(11, 4.6), dpi=130)
    ax.set_xlim(0, 11); ax.set_ylim(0, 4.6); ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")
    x0, step = 0.9, 2.35
    # 처음 메모 h0
    box(ax, 0.05, 2.0, 0.75, 0.8, "h0\n0", "#F3F4F6", GRAY, DARK, 10)
    for t, w in enumerate(words):
        x = x0 + t * step
        box(ax, x, 0.3, 1.5, 0.8, w, "#E6F7F6", TEAL, DARK, 12)                 # 단어
        box(ax, x, 1.75, 1.5, 1.3, "RNN 칸\n(같은 w)", TEAL, None, "#FFFFFF", 11)  # RNN 셀
        arrow(ax, x + 0.75, 1.1, x + 0.75, 1.75, label="단어 벡터", lx=0.72, ly=0.0, fs=9)
        if t == 0:
            arrow(ax, 0.8, 2.4, x, 2.4)
        if t < n - 1:
            arrow(ax, x + 1.5, 2.4, x + step, 2.4, label=f"h{t + 1}  메모", ly=0.22, fs=10)
    xe = x0 + (n - 1) * step + 1.5
    box(ax, xe + 0.55, 1.95, 1.0, 0.9, "주제\n점수", AMBER, None, DARK, 11)
    arrow(ax, xe, 2.4, xe + 0.55, 2.4, label=f"h{n}", ly=0.22, fs=10)
    ax.text(xe + 1.05, 1.55, "→ 스포츠 0.97", color=DARK, fontsize=11, ha="center")
    ax.text(5.5, 4.2, "단어를 한 개씩 읽으며 메모(h)를 갱신한다 — 네 칸은 같은 매개변수를 쓰는 한 칸을 시간 순서로 펼친 것",
            color=DARK, fontsize=11.5, ha="center")
    ax.text(5.5, 3.65, "h(t) = tanh( 단어(t) · W_x  +  h(t-1) · W_h  +  b )", color=TEAL, fontsize=12, ha="center", family="Malgun Gothic")
    fig.savefig(os.path.join(DEST, "컴퓨팅사고_12주차_RNN펼침.png"), bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)


if __name__ == "__main__":
    draw_train_infer()
    draw_rnn()
    print("saved 2 figures")

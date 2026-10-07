import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 4·5주차 노트북을 수업 사이트용으로 변환해 2026-2_github/content 에 저장 (원본은 수정하지 않음)
import sys
from site_common import *

SRC = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
DST = os.path.join(SRC, "2026-2_github", "content")
sys.stdout.reconfigure(encoding="utf-8")

COMMON = [
    (BANNER_OLD, BANNER_NEW),
    (OLD_CHECK_HEAD, CHECK_PREFIX),
    ("수업 후 <code style=\"background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;\">파일 → 저장</code> 으로 오늘 작성한 내용을 내 Drive 에 저장해 두세요.",
     "수업 후 <code style=\"background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;\">File → Download</code> 로 오늘 작성한 내용을 내려받아 두세요."),
]

W4 = [
    ("## 1-0. Colab 시작하기 (약 10분)\n\n**① 내 사본 만들기** — 메뉴에서 `파일 → Drive에 사본 저장` 을 누르세요. 사본이 아니면 작성한 내용이 저장되지 않습니다.\n\n**② 셀(cell)**",
     "## 1-0. 노트북 시작하기 (약 10분)\n\n" + INTRO_SITE + "\n\n**⑤ 셀(cell)**"),
    ("**③ 실행 방법**", "**⑥ 실행 방법**"),
    ("| 아래에 새 코드 셀 추가 | `Ctrl + M` 누른 뒤 `B` |", "| 아래에 새 코드 셀 추가 | `Esc` 누른 뒤 `B` (또는 툴바의 `+`) |"),
    ("Colab 첫 실행과 기본 데이터 타입", "노트북 첫 실행과 기본 데이터 타입"),
    ("Colab에서 코드 셀을 실행하고", "노트북에서 코드 셀을 실행하고"),
    ("| **1교시** | Colab 첫 실행 · 기본 데이터 타입 |", "| **1교시** | 노트북 첫 실행 · 기본 데이터 타입 |"),
    ("Colab에는 편리한 기능이 하나 더 있습니다.", "노트북에는 편리한 기능이 하나 더 있습니다."),
    ("Colab 도 리눅스 서버라서 UTF-8 입니다.", "이 노트북이 실행되는 브라우저 안의 Python 도 UTF-8 입니다."),
    ("⚠️ Colab에서 특히 주의 — 셀 실행 ‘순서’", "⚠️ 노트북에서 특히 주의 — 셀 실행 ‘순서’"),
    ("꼬였다 싶으면 메뉴의 <b>런타임 → 세션 다시 시작</b>", "꼬였다 싶으면 메뉴의 <b>Kernel → Restart Kernel</b>"),
    ("Colab이 셀 마지막 줄의 값을 보여 주는 것은,", "노트북이 셀 마지막 줄의 값을 보여 주는 것은,"),
]

W5 = [
    ("**① 내 사본 만들기** — 메뉴에서 `파일 → Drive에 사본 저장` 을 누르세요. 사본이 아니면 작성한 내용이 저장되지 않습니다.\n\n**② 자가 점검 도구 준비**",
     INTRO_SITE + "\n\n**⑤ 자가 점검 도구 준비**"),
    ("보통 스페이스 4칸입니다. Colab에서는 콜론 뒤에", "보통 스페이스 4칸입니다. 코드 셀에서 콜론 뒤에"),
]

for fn, extra in [("컴퓨팅사고_4주차_Python기본문법1.ipynb", W4), ("컴퓨팅사고_5주차_Python기본문법2.ipynb", W5)]:
    nb = load(os.path.join(SRC, fn))
    for old, new in COMMON + extra:
        replace_once(nb, old, new)
    finalize(nb)
    left = [(i, src(c)[:80]) for i, c in enumerate(nb["cells"]) if "Colab" in src(c) and "Google Colab 등" not in src(c) and "Colab 용이" not in src(c) and "Colab 이면" not in src(c)]
    print(fn, "남은 Colab 언급:", left)
    save(nb, os.path.join(DST, fn))
    print("  →", os.path.join(DST, fn))

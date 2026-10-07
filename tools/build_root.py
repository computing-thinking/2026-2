import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 사이트 첫 화면용 안내 노트북(마크다운만) 생성 → content/컴퓨팅사고_시작하기.ipynb
import os, sys
from site_common import *
sys.stdout.reconfigure(encoding="utf-8")
DST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료\2026-2_github\content"
BOX = "box-sizing:border-box;max-width:100%;overflow-wrap:anywhere;width:auto;"

WEEKS = [  # (주차, 제목, 파일명, 부제)
    (4, "Python 기본 문법 (1)", "컴퓨팅사고_4주차_Python기본문법1.ipynb", "기본 데이터 타입 · 변수 · 식과 명령문"),
    (5, "Python 기본 문법 (2)", "컴퓨팅사고_5주차_Python기본문법2.ipynb", "리스트 · 튜플 · 딕셔너리 · 집합 · 조건과 if 문"),
    (6, "Python 반복문", "컴퓨팅사고_6주차_Python반복문.ipynb", "while · for · 컴프리헨션과 이터레이터 · 스택과 큐"),
]

def link(fn):
    return f"{SITE}/notebooks/index.html?path={fn}"

rows = "\n".join(f"| **{w}주차** | [{t}]({link(fn)}) | {sub} |" for w, t, fn, sub in WEEKS)

cells = []
def md(s): cells.append({"cell_type": "markdown", "id": new_id("root-%d-%s" % (len(cells), s[:40])), "metadata": {}, "source": None, "_s": s})

md(f'''<div style="background:#0EA5A4;color:#FFFFFF;padding:34px 36px;border-radius:18px;{BOX}">
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 2026-2</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">실습 노트북 시작하기</div>
<div style="font-size:1.25em;margin-top:6px;">설치도 로그인도 없이, 브라우저에서 바로 Python을 실행합니다</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 수업 사이트 (JupyterLite)</div>
</div>''')

md(f'''# 주차별 노트북

아래 링크를 누르면 그 주차 노트북이 열립니다. 처음 열 때 Python 을 준비하느라 10 ~ 20초쯤 걸립니다. 오른쪽 위에 **Python (Pyodide)** 가 보이면 준비된 것입니다.

| 주차 | 노트북 | 내용 |
|:---:|:---|:---|
{rows}

1 ~ 3주차는 슬라이드 수업이라 노트북이 없습니다. 새 주차는 수업 전에 이 목록에 추가됩니다.''')

md(f'''# 이 사이트는 어떻게 동작하나요?

이 사이트는 **서버 없이** 동작합니다. 링크를 열면 Python 실행기(Pyodide)가 여러분의 브라우저 안으로 내려와 거기서 코드를 실행합니다. 그래서 설치도 로그인도 필요 없고, 여러분이 쓴 코드는 어디로도 전송되지 않습니다.

<div style="background:#E6F7F6;color:#1F2937;border-left:6px solid #0EA5A4;padding:12px 18px;border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#0EA5A4;">🔑 꼭 기억할 한 가지 — 저장은 Download</b><br>노트북에 쓴 내용은 <b>지금 쓰는 이 브라우저 안에만</b> 저장됩니다. 다른 기기나 다른 브라우저에서는 보이지 않고, 브라우저 데이터를 지우면 사라집니다.<br>수업이 끝나면 메뉴에서 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;border:1px solid #BFE9E7;">File → Download</code> 로 파일을 내려받으세요. <b>파일이 내 손에 있어야 저장된 것입니다.</b> 과제 제출도 이 파일로 합니다.</div>

| 하고 싶은 일 | 방법 |
|:---|:---|
| 셀 실행 | 셀을 누르고 `Shift + Enter`, 또는 툴바의 **▶** 버튼 |
| 작업 보관 · 제출 | `File → Download` → PC는 다운로드 폴더, 아이패드는 ‘파일’ 앱 |
| 다른 기기에서 이어 하기 | 내려받은 파일을 그 기기에서 `File → Open…` → 업로드(⬆) |
| 처음 상태로 되돌리기 | `File → Open…` 에서 그 노트북을 삭제한 뒤 새로고침 → 원본을 다시 받아 옴 |
| 셀이 끝나지 않을 때 | 툴바의 **■** 버튼 (`Kernel → Interrupt Kernel`) |
| 변수가 꼬였을 때 | `Kernel → Restart Kernel` 뒤 위에서부터 다시 실행 |''')

md(f'''# 아이패드로 수업을 듣는 분께

- **Safari 일반 탭**에서 여세요. 사생활 보호 탭에서는 저장이 되지 않습니다.
- 셀 실행은 툴바의 **▶** 버튼이 편합니다. 외장 키보드가 있으면 `Shift + Enter` 도 됩니다.
- 들여쓰기는 **스페이스 4칸**입니다. 콜론(`:`) 뒤에서 줄을 바꾸면 자동으로 들여써 줍니다.
- Safari 는 **일주일 동안 열지 않은 사이트의 저장 내용을 지울 수 있습니다.** 수업 끝에 꼭 `File → Download` 하세요. 파일은 ‘파일’ 앱의 다운로드 폴더에 들어갑니다.

<div style="background:#F3F4F6;color:#1F2937;border-left:6px solid #6B7280;padding:12px 18px;border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#6B7280;">📎 Google Colab 은 쓰지 않습니다</b><br>이 수업의 노트북은 수업 사이트에서 여는 것을 전제로 만들었습니다. 파일을 내려받아 Google Colab 에서 열면 자가 점검 도구가 동작하지 않습니다. 문법을 몸에 익히는 기간에는 AI 자동완성 없이 직접 써 보는 것이 목표이기 때문입니다.</div>''')

for c in cells:
    s = c.pop("_s"); lines = s.split("\n"); c["source"] = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
out = os.path.join(DST, "컴퓨팅사고_시작하기.ipynb")
save(nb, out); print("saved", out, len(cells), "cells")

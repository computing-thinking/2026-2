import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 11주차 노트북 생성 스크립트 — 생각하기 판(수업용) · 풀이판(수업 후) · 과제 정답(교수용) 세 파일을 만든다
# 주제: 파일 입출력과 예외 처리 · 함수를 값처럼(일급 객체 · 데코레이터 · 타입 힌트)   — 2교시 분량
# 예제 문제 3개: 성적 파일로 평균 내기 · 튼튼한 성적 프로그램 · 함수 실행 시간 재기
#
# 셀마다 part 를 붙인다:  T(think) = 생각하기 판에만  /  S(solve) = 풀이판에만  /  BOTH = 두 판 모두
#   생각하기 판: 문법 설명 · 실행해 보는 셀 · 문제 띠 · 🤔 생각해 보기 상자 · 칠판 풀이를 받아 적는 빈 셀 · 실습(정답 없음) · 과제
#   풀이판:     문제 띠 · 🧠 풀이 상자 · 풀이 코드 · 정리 · 실습 정답
# 사용: python build_w11.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w11.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
THINK_NB = "컴퓨팅사고_11주차_파일과예외_생각하기.ipynb"
SOLVE_NB = "컴퓨팅사고_11주차_파일과예외_풀이.ipynb"
HW_SOL = "컴퓨팅사고_11주차_과제정답.ipynb"
T, S, BOTH = "think", "solve", "both"

# ───────────────────────── HTML 상자 (10주차 노트북과 같은 값) ─────────────────────────
BOX = "box-sizing:border-box;max-width:100%;overflow-wrap:anywhere;width:auto;"
IC_STYLE = "background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;border:1px solid #BFE9E7;"


def ic(s):
    return f'<code style="{IC_STYLE}">{html.escape(s)}</code>'


def fmt(s):
    """`코드` 표기를 인라인 코드 상자로 바꾼다 (HTML 상자 안에서 사용)."""
    out, parts = [], s.split("`")
    for i, p in enumerate(parts):
        out.append(ic(p) if i % 2 else p)
    return "".join(out)


def key(title, body):
    return (f'<div style="background:#E6F7F6;color:#1F2937;border-left:6px solid #0EA5A4;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#0EA5A4;">🔑 {fmt(title)}</b><br>{fmt(body)}</div>')


def note(title, body):
    return (f'<div style="background:#F3F4F6;color:#1F2937;border-left:6px solid #6B7280;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#6B7280;">📎 {fmt(title)}</b><br>{fmt(body)}</div>')


def fold(summary, body):
    """분량이 많은 참고 자료는 접어 둔다"""
    return (f'<details style="background:#F3F4F6;color:#1F2937;border-left:6px solid #6B7280;padding:10px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><summary style="cursor:pointer;color:#6B7280;font-weight:bold;">📎 {fmt(summary)}</summary>'
            f'<div style="margin-top:8px;">{fmt(body)}</div></details>')


def warn(title, body):
    return (f'<div style="background:#FFF0EE;color:#1F2937;border-left:6px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#FF6B5A;">⚠️ {fmt(title)}</b><br>{fmt(body)}</div>')


def think(title, body):
    """🧠 컴퓨팅 사고 상자 — 문제를 푸는 '생각의 단계'를 정리할 때 (풀이판)"""
    return (f'<div style="background:#FFF7E6;color:#1F2937;border-left:6px solid #F59E0B;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#B45309;">🧠 {fmt(title)}</b><br>{fmt(body)}</div>')


def ponder(title, body):
    """🤔 생각해 보기 상자 — 풀이 대신 학생이 스스로 답할 질문만 둔다 (생각하기 판)"""
    return (f'<div style="background:#FFF7E6;color:#1F2937;border-left:6px solid #F59E0B;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#B45309;">🤔 {fmt(title)}</b><br>{fmt(body)}</div>')


def task_box(label, title, minutes, body):
    m = f' <span style="color:#6B7280;font-weight:normal;">({minutes})</span>' if minutes else ""
    return (f'<div style="background:#FFFFFF;color:#1F2937;border:2px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:12px;margin:8px 0;line-height:1.7;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;'
            f'padding:2px 12px;border-radius:999px;font-weight:bold;">{label}</span>&nbsp; <b>{title}</b>{m}<br>{fmt(body)}</div>')


def boom(text):
    return ('<span style="background:#FFF0EE;color:#FF6B5A;border:1px solid #FF6B5A;padding:2px 10px;'
            f'border-radius:999px;font-weight:bold;">💥 일부러 오류를 내는 셀 — {text}</span>')


def code_block(code):
    return ('<pre style="background:#1F2937;color:#F9FAFB;padding:14px 16px;border-radius:10px;font-family:Consolas,monospace;'
            f'line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;box-sizing:border-box;max-width:100%;">{html.escape(code.strip())}</pre>')


def period(n, title, goals):
    lis = "".join(f"<li>{g}</li>" for g in goals)
    return (f'<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}">'
            f'<span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">{n}교시</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">{title}</span>'
            f'<span style="float:right;opacity:0.9;">⏱ 약 50분</span>'
            f'<ul style="margin:10px 0 0 0;line-height:1.7;">{lis}</ul></div>')


def problem(n, title, question):
    """문제 N 표지 — 세 문제의 시작을 알리는 띠"""
    return (f'<div style="background:#1F2937;color:#F9FAFB;padding:14px 22px;border-radius:12px;margin:12px 0;{BOX}">'
            f'<span style="background:#F59E0B;color:#1F2937;padding:3px 14px;border-radius:999px;font-weight:bold;">문제 {n}</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.3em;font-weight:bold;">{title}</span>'
            f'<div style="margin-top:8px;opacity:0.92;line-height:1.7;">{fmt(question)}</div></div>')


BREAK = '<div style="text-align:center;color:#6B7280;">☕ 쉬는 시간 — 10분</div>'
CHECK_HEAD = "# 🔍 자가 점검 — 수정하지 말고 실행만 하세요\n"
BLANK = '''
# 칠판의 풀이를 보며 직접 써 보세요



'''

# ───────────────────────── 셀 모으기 ─────────────────────────
CELLS = []          # (type, source, metadata, part)
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w11.py 가 사용


def md(src, part=T):
    CELLS.append(("markdown", src.strip("\n"), {}, part))


def code(src, raises=False, form=False, part=T):
    meta = {}
    if raises:
        meta["tags"] = ["raises-exception"]
    if form:
        meta["cellView"] = "form"
        meta["jupyter"] = {"source_hidden": True}
    CELLS.append(("code", src.strip("\n"), meta, part))


def blank():
    """생각하기 판 — 칠판 풀이를 받아 적는 빈 코드 셀"""
    code(BLANK, part=T)


def practice(label, title, minutes, body, skeleton, test, solution, raises=False, heading=None, show_answer=True,
             extra=None, extra_raises=False):
    """생각하기 판: ✏️ 상자 → 작성용 셀 → (추가 셀) → 🔍 점검 셀.   풀이판: 💡 정답 (show_answer 일 때)"""
    box = task_box(label, title, minutes, body)
    md((heading + "\n\n" if heading else "") + box, part=T)
    code(skeleton, raises=raises, part=T)
    if extra:
        code(extra, raises=extra_raises, part=T)
    name = label.split(" ", 1)[1]
    chk = CHECK_HEAD + f'check("{name}", lambda: {test})'
    code(chk, part=T)
    if show_answer:
        md((heading.replace("실습", "실습 정답") + "\n\n" if heading else "") +
           f'<b style="color:#FF6B5A;">💡 {label} 정답 예시</b> — {title}\n\n' + code_block(solution), part=S)
    PRACTICES.append((name, solution.strip("\n"), chk))


# ═════════════════════════ 표지 · 안내 ═════════════════════════
def cover(sub):
    return f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:34px 36px;border-radius:18px;{BOX}">
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 11주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">파일 입출력과 예외 처리 — 프로그램 밖의 세상과 만나다</div>
<div style="font-size:1.25em;margin-top:6px;">파일 읽고 쓰기 &nbsp;·&nbsp; 오류가 나도 멈추지 않는 프로그램 &nbsp;·&nbsp; 함수를 값처럼</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; {sub}</div>
</div>
'''


md(cover("수업용 노트북(설명 · 문제 · 실습) — 풀이는 칠판에서 함께 만듭니다"), part=T)
md(cover("풀이판 — 수업에서 칠판에 쓴 풀이와 코드를 정리한 것입니다"), part=S)

md('''
# 11주차 학습 안내

지금까지 프로그램이 다룬 데이터는 모두 **코드 안에** 적혀 있었습니다. 리스트에 점수를 직접 쓰고, 딕셔너리에 이름을 직접 넣었습니다. 그런데 진짜 데이터는 코드 밖에 있습니다. 엑셀 파일, 메모장, 센서 기록, 다른 프로그램이 남긴 결과. 오늘은 프로그램이 **밖의 세상**과 만나는 두 가지 방법을 배웁니다. 밖에서 데이터를 가져오는 **파일 입출력**, 그리고 밖의 세상이 내 뜻대로 되지 않을 때(파일이 없다, 숫자 자리에 글자가 있다) 멈추지 않고 대처하는 **예외 처리**입니다.

| 교시 | 주제 | 문제 |
|:---:|:---|:---|
| **1교시** | **파일 입출력** — 프로그램이 끝나도 남는 데이터 | ① 성적 파일로 평균 내기 |
| **2교시** | **예외 처리** — 오류가 나도 멈추지 않는 프로그램 &nbsp;·&nbsp; **함수를 값처럼** (일급 객체 · 데코레이터 · 타입 힌트) | ② 튼튼한 성적 프로그램 &nbsp; ③ 함수 실행 시간 재기 |

**오늘 수업을 마치면**

1. 텍스트 파일을 열어 읽고 쓰고, `with` 문으로 안전하게 닫을 수 있습니다.
2. 오류가 날 수 있는 코드를 `try` · `except` 로 감싸 프로그램이 멈추지 않게 하고, 오류 종류별로 다르게 대처할 수 있습니다.
3. 함수도 숫자나 문자열처럼 **값**이라는 것을 알고, 함수를 인자로 넘기거나 돌려받을 수 있습니다.
4. 데코레이터가 ‘함수를 포장하는 함수’임을 알고 `@` 문법을 읽을 수 있습니다. 타입 힌트를 읽고 쓸 수 있습니다.

''' + key("이 노트북을 읽는 법", "이 노트북에는 새 문법의 <b>설명과 실행해 보는 셀</b>, 그리고 세 문제의 <b>설명</b>이 있습니다. 세 문제의 <b>풀이와 코드는 없습니다.</b> 🤔 <b>생각해 보기</b> 상자의 질문을 놓고 먼저 스스로 궁리해 본 뒤, 수업에서 칠판의 풀이를 함께 따라갑니다. 칠판에서 나온 코드는 빈 셀에 직접 쳐 보세요.<br>회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요. 오늘은 일부러 오류를 내는 셀이 많습니다. 빨간 글씨는 무서운 것이 아니라 <b>안내문</b>입니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다.<br>풀이와 정리가 들어 있는 <b>풀이판</b>은 수업이 끝난 뒤 따로 올립니다."), part=T)

md('''
# 풀이판 읽는 법

''' + key("이 노트북은 수업 뒤에 봅니다", "수업용 노트북의 세 문제에 대해 칠판에서 함께 만든 <b>🧠 풀이 상자</b>와 <b>완성된 코드</b>, 각 교시의 <b>정리</b>, 실습의 <b>정답 예시</b>를 모았습니다.<br>코드 셀은 <b>위에서부터 차례로</b> 실행하세요. 앞 셀에서 만든 파일과 함수를 뒤에서 씁니다.<br>수업 시간에 빈 셀에 직접 쓴 코드와 여기의 코드를 <b>비교</b>해 보세요. 다른 점이 있다면 어느 쪽이 더 읽기 쉬운지, 둘 다 맞는지 생각해 보세요."), part=S)

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · 파일 입출력 — 프로그램이 끝나도 남는 데이터\n\n" + period(1, "파일 읽고 쓰기", [
    "변수는 프로그램이 끝나면 사라지고, 파일은 남는다는 것을 안다",
    "`open` · `write` · `read` · `close` 와 `with` 문으로 텍스트 파일을 읽고 쓴다",
    "줄 단위로 읽어 한 줄을 쪼개고 숫자로 바꾸는, 가장 흔한 데이터 처리의 모양을 익힌다",
    "파일을 열 때 인코딩을 지정하는 습관을 들인다",
]), part=BOTH)

md('''
## 1-0. 시작 전에

''' + INTRO_SITE + '''

**⑤ 자가 점검 도구 준비** — 아래 셀을 한 번 실행해 두세요. 실습 답을 스스로 확인할 때 씁니다. (코드 내용은 몰라도 됩니다.)
''')

code('''
#@title ▶ 먼저 실행하세요 — 자가 점검 도구 준비
import importlib.util as _ilu

def _in_class_site():
    # 수업 사이트(JupyterLite)에서 열었는지 확인합니다. Google Colab 이면 False 입니다.
    return _ilu.find_spec("google") is None or _ilu.find_spec("google.colab") is None

if not _in_class_site():
    print("⚠️ 이 노트북은 Google Colab 용이 아닙니다.")
    print("   LearnUs 에 올린 수업 사이트 링크로 열어 주세요. 여기서는 자가 점검이 동작하지 않습니다.")
    raise SystemExit

def check(name, test):
    """실습 답을 확인하는 도구입니다. 수정하지 마세요."""
    if not _in_class_site():
        print(f"⚠️ {name}: 수업 사이트에서 실행해야 점검할 수 있습니다.")
        return
    try:
        ok = test()
    except NameError as e:
        print(f"⏳ {name}: 아직 필요한 변수가 없습니다 → {e}")
        return
    except Exception as e:
        print(f"❌ {name}: 확인 중 오류가 났습니다 → {type(e).__name__}: {e}")
        return
    print(f"✅ {name}: 통과!" if ok else f"❌ {name}: 값이 다릅니다. 다시 확인해 보세요.")

# 수업 사이트에서는 %%writefile 로 방금 만든 .py 파일을 import 가 바로 찾지 못합니다 (파일 목록 캐시).
# import 때마다 캐시를 비우는 작은 장치를 끼워 둡니다.
import importlib as _il, sys as _sys

class _RefreshFinder:
    _busy = False                     # invalidate_caches 가 안에서 다시 import 를 일으켜도 되돌아 들어오지 않게

    @classmethod
    def find_spec(cls, name, path=None, target=None):
        if not cls._busy:
            cls._busy = True
            try:
                _il.invalidate_caches()
            finally:
                cls._busy = False
        return None

if not any(type(f).__name__ == "_RefreshFinder" for f in _sys.meta_path):
    _sys.meta_path.insert(0, _RefreshFinder())

print("준비 완료! 이제 수업을 시작합니다.")
''', form=True)

md('''
## 1-1. 변수는 사라지고, 파일은 남는다

1주차에 컴퓨터의 기억 장치가 두 종류라고 했습니다. **메모리**(RAM)는 빠르지만 전원이 꺼지면 비워집니다. **보조 기억 장치**(SSD · 하드디스크)는 느리지만 전원이 꺼져도 남습니다.

지금까지 우리가 만든 변수는 모두 메모리에 있었습니다. 메뉴에서 `Kernel → Restart Kernel` 을 누르면 어떻게 되나요? 변수가 **전부 사라집니다.** 수업에서 여러 번 겪었을 것입니다. 프로그램이 계산한 결과를 **남기려면** 보조 기억 장치에 써야 합니다. 그 단위가 **파일(file)** 입니다.

파일은 이름이 붙은 **바이트의 줄**입니다. 그 바이트를 어떻게 해석하느냐에 따라 두 종류로 나눕니다.

| 종류 | 안에 든 것 | 예 | 여는 도구 |
|:---|:---|:---|:---|
| **텍스트 파일** | 사람이 읽는 글자 (인코딩된 문자열) | `.txt` `.csv` `.py` `.ipynb` `.html` | 메모장 · 코드 편집기 · **오늘 배우는 Python 코드** |
| **바이너리 파일** | 글자가 아닌 데이터 | `.png` `.mp3` `.pptx` `.exe` | 전용 프로그램 (그림 뷰어, 음악 재생기) |

오늘은 텍스트 파일만 다룹니다. 지금 보고 있는 이 노트북도 텍스트 파일(`.ipynb`)입니다.

**예상해 보기** — 아래 셀은 프로그램이 지금 서 있는 폴더와 그 안의 파일 목록을 보여 줍니다. 무엇이 보일까요?
''')

code('''
import os

print("현재 작업 폴더:", os.getcwd())
print("이 폴더의 파일:", os.listdir("."))
''')

md('''
여러분이 지금까지 연 노트북 파일들이 보입니다. 파일을 열 때 이름만 적으면 Python 은 **이 폴더**에서 찾습니다. 이것을 **현재 작업 폴더**(current working directory)라고 합니다. 다른 폴더의 파일은 `data/scores.txt` 처럼 경로를 적습니다.

''' + fold("경로에 대하여 — 절대 경로와 상대 경로", "<b>절대 경로</b>는 맨 위 폴더부터 전부 적은 것입니다. Windows 는 `C:\\Users\\me\\data.txt`, 리눅스·맥·수업 사이트는 `/drive/data.txt`.<br><b>상대 경로</b>는 현재 작업 폴더를 기준으로 적은 것입니다. `data.txt` 는 바로 이 폴더, `data/a.txt` 는 아래 폴더, `../a.txt` 는 위 폴더.<br>Windows 의 `\\` 는 Python 문자열에서 특수 문자라 `\\\\` 로 두 번 쓰거나 `/` 로 바꿔 씁니다. `/` 는 어느 운영체제에서나 됩니다. 수업 사이트는 리눅스처럼 동작하므로 `/` 만 씁니다.") + '''

## 1-2. 파일에 쓰기 — `open` · `write` · `close`

파일을 다루는 일은 늘 세 단계입니다. **열고**, **읽거나 쓰고**, **닫습니다.** 냉장고와 같습니다. 문을 열고, 넣거나 꺼내고, 문을 닫습니다.

**예상해 보기** — `write` 는 무엇을 돌려줄까요? 그리고 출력에는 몇 줄이 보일까요?
''')

code('''
f = open("memo.txt", "w", encoding="utf-8")     # ① 열기 — "w" 는 쓰기 모드. 없으면 만들고, 있으면 비웁니다
n = f.write("첫 줄입니다\\n")                       # ② 쓰기 — 줄바꿈 \\n 은 직접 넣어야 합니다
f.write("둘째 줄입니다\\n")
f.close()                                        # ③ 닫기

print(n)
print(os.listdir("."))
''')

md('''
`write` 는 **쓴 글자 수**를 돌려줍니다 (`\\n` 도 한 글자). 그리고 파일 목록에 `memo.txt` 가 새로 생겼습니다. 메뉴의 `File → Open…` 에서도 보입니다. 열어 보면 두 줄이 들어 있습니다.

`print` 와 달리 `write` 는 **줄바꿈을 넣어 주지 않습니다.** `\\n` 을 빼면 두 줄이 한 줄로 이어집니다. 숫자도 바로 쓸 수 없습니다. `f.write(42)` 는 `TypeError` 입니다. f-string 으로 문자열을 만들어 씁니다.

`open` 의 두 번째 인자가 **모드**(mode)입니다.

| 모드 | 뜻 | 파일이 이미 있으면 | 파일이 없으면 |
|:---:|:---|:---|:---|
| `"r"` | 읽기 (기본값 — 생략 가능) | 처음부터 읽는다 | **오류** (`FileNotFoundError`) |
| `"w"` | 새로 쓰기 | **내용을 지우고** 새로 쓴다 | 만든다 |
| `"a"` | 덧붙이기 (append) | 끝에 이어 쓴다 | 만든다 |

**예상해 보기** — 아래 셀을 실행하면 `memo.txt` 는 몇 줄이 될까요? 모드를 `"w"` 로 바꾸면요?
''')

code('''
f = open("memo.txt", "a", encoding="utf-8")     # "a" — 끝에 덧붙입니다
f.write("셋째 줄 — 덧붙였습니다\\n")
f.close()

print(os.path.getsize("memo.txt"), "바이트")      # 파일 크기 (글자 수가 아닙니다 — 한글은 한 글자가 3바이트)
''')

md('''
### `with` 문 — 닫는 것을 잊지 않게

`close()` 를 잊으면 어떻게 될까요? 쓴 내용이 디스크에 **아직 안 갔을 수** 있습니다. Python 은 효율을 위해 쓸 내용을 잠시 모아 두었다가(버퍼) 닫을 때 한꺼번에 보냅니다. 닫지 않으면 마지막 내용이 사라질 수 있습니다. 냉장고 문을 안 닫은 것과 같습니다.

그래서 Python 은 **블록이 끝나면 자동으로 닫아 주는** 문법을 만들었습니다. `with` 문입니다. 앞으로 파일은 **항상 이 모양**으로 엽니다.
''')

code('''
with open("memo.txt", "a", encoding="utf-8") as f:      # as 뒤의 이름이 파일 객체입니다
    f.write("넷째 줄 — with 문으로 썼습니다\\n")
                                                        # 들여쓰기가 끝나면 자동으로 close() 됩니다
print("닫혔나요?", f.closed)
''')

md(boom("닫힌 파일에 쓰면?"))

code('''
f.write("다섯째 줄\\n")          # with 블록 밖 — f 는 이미 닫혔습니다
''', raises=True)

md('''
`ValueError: I/O operation on closed file` — “닫힌 파일에 입출력을 하려 했다”는 안내입니다. 파일 작업은 **`with` 블록 안에서만** 합니다.

''' + key("파일 쓰기 정리", "① 파일 작업은 <b>열기 → 쓰기 → 닫기</b>. `with open(...) as f:` 로 열면 블록 끝에서 <b>자동으로 닫힙니다.</b><br>② 모드: `\"w\"` 는 지우고 새로, `\"a\"` 는 끝에 덧붙이기. 읽기는 `\"r\"` 이고 생략할 수 있습니다.<br>③ `write` 는 <b>문자열만</b> 받고 <b>줄바꿈을 넣지 않습니다.</b> 숫자는 f-string 으로, 줄 끝에는 `\\n` 을 직접.<br>④ `encoding=\"utf-8\"` 은 항상 적습니다 (1-4 에서 이유를 봅니다)."))

md('''
## 1-3. 파일 읽기 — `read` · 줄 단위 `for` · `readlines`

읽기는 모드를 생략합니다. 읽는 방법은 세 가지입니다. 먼저 **통째로** 읽습니다.

**예상해 보기** — `repr(text)` 는 어떻게 보일까요? `print(text)` 와 무엇이 다를까요?
''')

code('''
with open("memo.txt", encoding="utf-8") as f:
    text = f.read()                  # 파일 전체를 문자열 하나로

print(repr(text))                    # 있는 그대로 — 줄바꿈이 \\n 으로 보입니다
print("----")
print(text)                          # 보통 출력 — \\n 이 줄바꿈으로 바뀝니다
print(type(text), len(text), "글자")
''')

md('''
파일의 내용은 **문자열 하나**입니다. 줄은 그 안의 `\\n` 으로 나뉘어 있을 뿐입니다. 4주차에서 본 `\\n` 이 파일에서는 ‘줄의 끝’이라는 뜻으로 쓰입니다.

데이터 파일은 보통 **한 줄이 한 건**입니다. 그래서 줄 단위로 읽는 일이 가장 많습니다. 파일 객체는 6주차의 이터레이터처럼 `for` 에 바로 넣을 수 있습니다.

**예상해 보기** — 아래 셀의 출력은 왜 줄 사이가 비어 보일까요?
''')

code('''
with open("memo.txt", encoding="utf-8") as f:
    for line in f:                   # 한 줄씩 — 메모리에 한 줄만 올리므로 큰 파일도 됩니다
        print(line)
''')

md('''
`line` 에는 줄 끝의 `\\n` 이 **포함되어** 있고, `print` 가 **또** 줄바꿈을 넣기 때문입니다. 두 가지 해결이 있습니다. `print(line, end="")` 로 `print` 의 줄바꿈을 끄거나, `line.strip()` 으로 양 끝의 공백과 줄바꿈을 **떼어 냅니다.** 데이터를 다룰 때는 거의 언제나 `strip()` 입니다. 줄 끝의 `\\n` 이 숫자나 이름에 붙어 따라다니면 안 되기 때문입니다.
''')

code('''
with open("memo.txt", encoding="utf-8") as f:
    for number, line in enumerate(f, start=1):       # 6주차 enumerate — 몇 번째 줄인지 함께
        print(number, repr(line.strip()))
''')

md('''
세 번째 방법은 줄들을 **리스트로** 받는 것입니다. 5주차의 문자열 메서드 `splitlines()` 를 쓰면 `\\n` 이 떨어진 깨끗한 리스트가 됩니다.
''')

code('''
with open("memo.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()    # 줄 단위 리스트 — \\n 은 떼어 줍니다

print(len(lines), "줄")
print(lines)
print(lines[-1])                     # 마지막 줄
''')

md('''
**예상해 보기** — 같은 파일을 한 번 열어 **두 번** 읽으면 두 번째는 무엇이 나올까요?
''')

code('''
with open("memo.txt", encoding="utf-8") as f:
    first = f.read()
    second = f.read()

print(len(first), "글자 /", len(second), "글자")
''')

md('''
두 번째는 **빈 문자열**입니다. 파일에는 ‘지금 어디까지 읽었는가’를 가리키는 위치가 있고, 한 번 끝까지 읽으면 그 위치가 끝에 가 있습니다. 책갈피가 마지막 장에 꽂힌 것입니다. 다시 읽으려면 **다시 엽니다.** 보통은 한 번 읽어 변수에 담아 두고 그 변수를 씁니다.

''' + key("파일 읽기 정리", "① `f.read()` — 전체를 문자열 하나로. 작은 파일, 통째로 쓸 때.<br>② `for line in f:` — 한 줄씩. 큰 파일, 한 줄이 한 건인 데이터. <b>줄 끝의 `\\n` 은 `strip()` 으로 뗀다.</b><br>③ `f.read().splitlines()` — 줄 리스트. 줄 수를 세거나 특정 줄을 집을 때.<br>④ 한 번 읽으면 끝까지 간다. 다시 읽으려면 다시 연다."))

md('''
## 1-4. 인코딩 — 왜 `encoding="utf-8"` 을 늘 적는가

4주차에서 글자는 숫자(코드)로, 숫자는 바이트로 저장된다고 했습니다. 그 규칙이 **문자 인코딩**이고, 오늘날의 표준은 **UTF-8** 입니다. 파일은 바이트이므로, 파일을 열 때 Python 은 “이 바이트를 어떤 규칙으로 글자로 바꿀까”를 알아야 합니다.

`encoding` 을 적지 않으면 **운영체제의 기본값**을 씁니다. 수업 사이트 · 리눅스 · 맥은 UTF-8 입니다. 그런데 **한국어 Windows 는 `cp949`** 라는 옛 규칙일 수 있습니다. 같은 코드가 내 노트북에서는 되고 친구 노트북에서는 깨지는 이유가 대개 이것입니다.

**예상해 보기** — UTF-8 로 쓴 `memo.txt` 를 `cp949` 규칙으로 읽으면 어떻게 될까요?
''')

md(boom("인코딩을 잘못 짚으면?"))

code('''
with open("memo.txt", encoding="cp949") as f:    # UTF-8 로 쓴 파일을 cp949 규칙으로 읽어 봅니다
    print(f.read())
''', raises=True)

md('''
`UnicodeDecodeError: 'cp949' codec can't decode byte ...` — “이 바이트를 cp949 규칙으로는 글자로 못 바꾸겠다”는 안내입니다. 운이 나쁘면 오류 대신 **엉뚱한 글자**(`ìë`, `\uc548\ub155` 같은 것)가 나오기도 합니다. 4주차에서 본 ‘한글 깨짐’이 바로 이것입니다.

대처는 간단합니다. **쓸 때도 읽을 때도 `encoding="utf-8"` 을 적습니다.** 그러면 어느 운영체제에서 열어도 같습니다.

''' + note("Windows 에서 받은 파일이 깨질 때", "메모장이나 엑셀(CSV 저장)에서 만든 파일은 `cp949` 일 수 있습니다. `encoding=\"utf-8\"` 로 열어 `UnicodeDecodeError` 가 나면 `encoding=\"cp949\"` 로 바꿔 보세요. 반대로 그 파일을 UTF-8 로 다시 저장하는 것이 더 좋은 해결입니다. 메모장의 ‘다른 이름으로 저장’에 인코딩 선택이 있습니다."))

# ── 문제 1 ──
md("## 1-5. " + problem(1, "성적 파일로 평균 내기", "학생 10명의 점수가 `scores.txt` 에 <b>한 줄에 한 명씩</b> `이름,점수` 모양으로 적혀 있습니다. 이 파일을 읽어 <b>평균</b>과 <b>최고점 학생</b>을 구하고, 결과를 `report.txt` 파일에 <b>써서 남기세요.</b> 점수가 100명, 1만 명이 되어도 코드는 바뀌지 않아야 합니다.<br>(점수를 코드에 직접 적지 않습니다. 코드는 파일의 내용을 모릅니다.)"), part=BOTH)

md('''
먼저 데이터 파일을 만듭니다. 실제로는 누군가 엑셀에서 저장하거나 다른 프로그램이 만들어 둔 파일이겠지만, 오늘은 우리가 직접 씁니다. 아래 셀을 실행하면 `scores.txt` 가 생깁니다.
''', part=BOTH)

code('''
students = [("김민준", 88), ("이서연", 95), ("박지호", 72), ("최수아", 91), ("정예준", 64),
            ("강하은", 85), ("조시우", 79), ("윤지아", 97), ("장도윤", 58), ("임하린", 83)]

with open("scores.txt", "w", encoding="utf-8") as f:
    for name, score in students:
        f.write(f"{name},{score}\\n")

with open("scores.txt", encoding="utf-8") as f:
    print(f.read())
''', part=BOTH)

md('''
''' + ponder("생각해 보기 — 한 줄을 어떻게 숫자로 바꾸나", "① `\"김민준,88\\n\"` 한 줄에서 이름과 점수를 따로 꺼내려면 5주차의 어떤 문자열 메서드를 쓰나요? 꺼낸 점수는 `str` 입니다. 더하려면 무엇이 필요한가요?<br>② 줄 끝의 `\\n` 을 떼지 않으면 어디에 붙어 따라다닐까요? 이름일까요, 점수일까요?<br>③ 읽은 점수들을 무엇에 모아야 평균과 최고점 학생을 둘 다 구할 수 있을까요? 리스트? 딕셔너리?<br>④ 결과를 `report.txt` 에 쓸 때 `f.write(average)` 라고 하면 어떻게 될까요?<br>⑤ 파일 이름을 `score.txt` 로 잘못 적으면 어떤 일이 일어날까요? 프로그램은 어디서 멈출까요?") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요. 파일을 읽어 딕셔너리로 돌려주는 함수부터 시작합니다.
''')
blank()

# ── 문제 1 풀이 ──
md('''
''' + think("분해 — 읽기 · 한 줄 처리 · 모으기 · 계산 · 쓰기", "파일 처리 프로그램은 거의 언제나 같은 다섯 단계입니다.<br>① <b>읽기</b>: `with open` 으로 열고 `for line in f` 로 한 줄씩.<br>② <b>한 줄 처리</b>: `strip()` 으로 `\\n` 을 떼고, `split(\",\")` 으로 쪼개고, 점수는 `int()` 로. 한 줄은 `이름,점수` 두 조각이므로 `name, score = ...` 로 한 번에 받습니다.<br>③ <b>모으기</b>: 이름으로 점수를 찾아야 하니 딕셔너리 `{이름: 점수}` 가 맞습니다.<br>④ <b>계산</b>: 평균은 `sum / len`, 최고점 학생은 값이 가장 큰 키.<br>⑤ <b>쓰기</b>: f-string 으로 문자열을 만들어 `write`.<br>①~③을 함수 `read_scores(filename)` 로 묶으면 파일이 바뀌어도, 1만 명이 되어도 코드는 그대로입니다. 7주차의 ‘한 가지 일을 하는 함수’입니다."), part=S)

code('''
def read_scores(filename):
    """이름,점수 파일을 읽어 {이름: 점수} 딕셔너리로 돌려준다."""
    scores = {}
    with open(filename, encoding="utf-8") as f:
        for line in f:
            name, score = line.strip().split(",")     # "김민준,88\\n" → "김민준,88" → ["김민준", "88"]
            scores[name] = int(score)                 # 점수는 문자열 → 정수
    return scores

scores = read_scores("scores.txt")
print(scores)
''', part=S)

code('''
average = sum(scores.values()) / len(scores)
best = max(scores, key=scores.get)        # 값(점수)이 가장 큰 키(이름) — key= 에 함수를 넘겼습니다. 2교시에서 다시 봅니다

print(f"학생 수 {len(scores)}명, 평균 {average:.1f}점, 최고점 {best} ({scores[best]}점)")
''', part=S)

code('''
with open("report.txt", "w", encoding="utf-8") as f:
    f.write(f"학생 수: {len(scores)}\\n")
    f.write(f"평균: {average:.1f}\\n")
    f.write(f"최고점: {best} ({scores[best]})\\n")

with open("report.txt", encoding="utf-8") as f:       # 제대로 써졌는지 다시 열어 확인
    print(f.read())
''', part=S)

md('''
`scores.txt` 의 줄을 100개로 늘려도 코드는 한 글자도 바뀌지 않습니다. 코드는 파일의 **내용**을 모르고 **모양**(한 줄에 `이름,점수`)만 압니다. 이것이 데이터를 코드 밖에 두는 이유입니다.

그런데 파일 이름을 잘못 적으면 어떻게 될까요?
''', part=S)

md(boom("없는 파일을 읽으면?"), part=BOTH)

code('''
read_scores("score.txt")         # scores.txt 를 score.txt 로 잘못 적었습니다
''', raises=True, part=S)

code('''
with open("score.txt", encoding="utf-8") as f:     # scores.txt 를 score.txt 로 잘못 적었습니다
    print(f.read())
''', raises=True, part=T)

md('''
`FileNotFoundError: [Errno 2] No such file or directory: 'score.txt'` — “그런 파일이 없다”는 안내입니다. 그리고 프로그램은 **거기서 멈춥니다.** 뒤에 100줄이 더 있어도 실행되지 않습니다. 파일이 없는 것은 프로그램의 잘못이 아니라 **밖의 세상**의 사정입니다. 밖의 사정으로 프로그램이 멈추지 않게 하는 방법이 2교시의 **예외 처리**입니다.
''', part=BOTH)

md(key("1교시 정리", "① 변수는 메모리에, 파일은 디스크에. 프로그램이 끝나도 남기려면 <b>파일</b>에 씁니다.<br>② 파일 작업은 <b>열기 → 읽기/쓰기 → 닫기</b>. `with open(이름, 모드, encoding=\"utf-8\") as f:` 한 줄이 열기와 닫기를 맡습니다.<br>③ 쓰기는 `\"w\"`(새로) · `\"a\"`(덧붙여), `write` 는 문자열만, 줄바꿈은 직접. 읽기는 `read()` · `for line in f` · `splitlines()`.<br>④ 데이터 파일은 <b>한 줄이 한 건</b>. 한 줄 처리의 기본형은 `line.strip().split(\",\")` 뒤 `int()`.<br>⑤ 코드는 파일의 <b>모양</b>만 알고 <b>내용</b>은 모릅니다. 그래서 데이터가 커져도 코드는 그대로입니다."), part=S)

# ── 1교시 실습 ──
practice("✏️ 실습 1-1", "일기장 — 덧붙이고 세기", "약 5분",
         "두 함수를 쓰세요.<br>`add_entry(filename, text)` — 파일 끝에 `text` 를 <b>한 줄로 덧붙입니다</b>(기존 내용은 그대로, 줄 끝에 `\\n`). 파일이 없으면 만들어집니다.<br>`count_lines(filename)` — 파일의 줄 수를 돌려줍니다.<br>힌트: 덧붙이기는 모드 `\"a\"`. 줄 수는 `splitlines()` 의 길이. 두 함수 모두 `with` 문과 `encoding=\"utf-8\"` 을 씁니다.",
         '''
# 여기에 두 함수를 정의하세요


add_entry("diary.txt", "11월 10일 — 파일 입출력을 배웠다")
add_entry("diary.txt", "11월 11일 — 예외 처리 복습")
print(count_lines("diary.txt"), "줄")
''',
         '(lambda fn: (open(fn, "w", encoding="utf-8").close(), add_entry(fn, "첫째"), add_entry(fn, "둘째"), add_entry(fn, "셋째"), count_lines(fn) == 3 and open(fn, encoding="utf-8").read() == "첫째\\n둘째\\n셋째\\n")[-1])("_check_diary.txt")',
         '''
def add_entry(filename, text):
    with open(filename, "a", encoding="utf-8") as f:      # "a" — 끝에 덧붙입니다
        f.write(text + "\\n")

def count_lines(filename):
    with open(filename, encoding="utf-8") as f:
        return len(f.read().splitlines())

add_entry("diary.txt", "11월 10일 — 파일 입출력을 배웠다")
add_entry("diary.txt", "11월 11일 — 예외 처리 복습")
print(count_lines("diary.txt"), "줄")        # 2 줄 (셀을 다시 실행하면 4, 6, … 으로 늘어납니다 — "a" 이니까요)
''', raises=True, heading="## 1교시 실습")

practice("✏️ 실습 1-2", "단어 세기", "약 5분",
         "텍스트 파일을 읽어 <b>단어 수</b>를 돌려주는 `count_words(filename)` 을 쓰세요. 단어는 공백으로 나뉜 조각입니다(5주차 `split()` — 인자 없이 부르면 공백과 줄바꿈 모두에서 나눕니다). 아래 셀이 먼저 `poem.txt` 를 만들어 둡니다.<br>`count_words(\"poem.txt\")` → `16`",
         '''
with open("poem.txt", "w", encoding="utf-8") as f:
    f.write("죽는 날까지 하늘을 우러러\\n한 점 부끄럼이 없기를,\\n잎새에 이는 바람에도\\n나는 괴로워했다.\\n별을 노래하는 마음으로\\n")

# 여기에 함수를 정의하세요


print(count_words("poem.txt"), "단어")
''',
         '(lambda fn: (open(fn, "w", encoding="utf-8").write("a b\\nc d e\\n\\nf\\n"), count_words(fn) == 6)[-1])("_check_words.txt") and count_words("poem.txt") == 16',
         '''
def count_words(filename):
    with open(filename, encoding="utf-8") as f:
        return len(f.read().split())          # split() 은 공백·줄바꿈 모두에서 나눕니다

print(count_words("poem.txt"), "단어")        # 16 단어
''', raises=True)

md(BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · 예외 처리 — 오류가 나도 멈추지 않는 프로그램 · 함수를 값처럼\n\n" + period(2, "예외 처리 · 일급 객체 · 데코레이터 · 타입 힌트", [
    "오류가 안내문임을 알고, `try` · `except` 로 프로그램이 멈추지 않게 한다",
    "오류 종류별로 다르게 대처하고, `raise` 로 잘못된 값을 일찍 거른다",
    "함수가 값이라는 것(일급 객체)을 알고, 함수를 인자로 넘기고 돌려받는다",
    "데코레이터가 ‘함수를 포장하는 함수’임을 알고 `@` 문법을 읽는다 · 타입 힌트로 함수의 입출력을 적는다",
]), part=BOTH)

md('''
## 2-1. 오류의 세 종류 — 그중 하나만 프로그램이 대처할 수 있다

| 종류 | 언제 드러나나 | 예 | 누가 고치나 |
|:---|:---|:---|:---|
| **문법 오류** (`SyntaxError`) | **실행 전에** Python 이 읽다가 | 괄호를 안 닫음, 콜론 빠짐 | 프로그래머가 코드를 |
| **논리 오류** | 실행은 되는데 **답이 틀림** | 평균을 낼 때 `len` 대신 `len - 1` | 프로그래머가 코드를 — 가장 찾기 어렵다 (10주차) |
| **실행 오류** = **예외**(exception) | 실행 **도중** 상황이 코드의 가정과 다를 때 | 파일이 없다, 숫자 자리에 글자, 0 으로 나눔 | **프로그램이 스스로** 대처할 수 있다 ← 오늘 |

지금까지 만난 빨간 글씨는 대부분 세 번째였습니다.

| 예외 | 뜻 | 만난 곳 |
|:---|:---|:---|
| `ValueError` | 종류는 맞는데 값이 이상하다 | `int("23.5")` |
| `TypeError` | 종류가 맞지 않는다 | `"1" + 1`, `f.write(42)` |
| `IndexError` · `KeyError` | 그 위치 · 그 키가 없다 | 리스트 끝 너머, 없는 딕셔너리 키 |
| `ZeroDivisionError` | 0 으로 나눴다 | 빈 리스트의 평균 |
| `FileNotFoundError` | 그 파일이 없다 | 1교시 끝 |
| `UnicodeDecodeError` | 그 인코딩으로 못 읽는다 | 1-4 |
| `RecursionError` | 재귀가 너무 깊다 | 10주차 |

예외가 나면 Python 은 **거기서 멈추고** 어디서 무슨 일이 났는지 알려 줍니다. 혼자 쓰는 코드라면 그걸 보고 고치면 됩니다. 그런데 **남이 쓰는** 프로그램이라면? 사용자가 나이에 `스물`이라고 적었다고 프로그램이 통째로 꺼지면 안 됩니다. 파일 하나가 없다고 1만 명의 성적 처리가 전부 멈추면 안 됩니다.

**예상해 보기** — 아래 셀에서 어느 줄까지 실행되고 멈출까요?
''')

md(boom("숫자 자리에 글자가 오면?"))

code('''
text = "23.5"
print("변환을 시작합니다")
n = int(text)                   # "23.5" 는 정수 모양이 아닙니다
print("정수:", n)               # 여기까지 올까요?
print("프로그램 끝")
''', raises=True)

md('''
## 2-2. `try` · `except` — 해 보고, 안 되면

“**해 보고**, 오류가 나면 **이렇게 하라**”를 적는 문법입니다.

```python
try:
    오류가 날 수 있는 코드
except 오류종류:
    오류가 났을 때 할 일
그 뒤의 코드   ← 오류가 났든 안 났든 계속 실행됩니다
```

**예상해 보기** — 이번에는 몇 줄이 출력될까요? `text` 를 `"42"` 로 바꾸면요?
''')

code('''
text = "23.5"
print("변환을 시작합니다")
try:
    n = int(text)
    print("정수:", n)                              # 오류가 나면 이 줄은 건너뜁니다
except ValueError:
    print(f"정수가 아닙니다: {text!r}")            # !r 은 repr — 따옴표를 붙여 보여 줍니다
print("프로그램 끝")                               # 어느 쪽이든 여기는 실행됩니다
''')

md('''
흐름은 두 갈래입니다. `try` 블록을 위에서부터 실행하다가 **오류가 나면** 나머지를 건너뛰고 `except` 블록으로 갑니다. **오류가 안 나면** `except` 블록은 건너뜁니다. 어느 쪽이든 그 뒤의 코드는 계속됩니다. 프로그램이 **멈추지 않았습니다.**

오류 객체를 `as 이름` 으로 받으면 Python 의 안내문을 그대로 쓸 수 있습니다. 이것을 함수로 묶어 여러 입력에 써 봅니다.
''')

code('''
def to_int(text):
    """문자열을 정수로. 안 되면 None 을 돌려준다."""
    try:
        return int(text)
    except ValueError as e:          # e 가 오류 객체 — 안내문이 들어 있습니다
        print(f"  (건너뜀: {e})")
        return None

for text in ["42", " 7 ", "23.5", "스물", ""]:
    print(repr(text), "→", to_int(text))
''')

md('''
`int()` 는 앞뒤 공백은 봐주지만 `"23.5"` · `"스물"` · 빈 문자열은 거부합니다. 전에는 첫 번째 거부에서 프로그램이 멈췄지만, 이제는 **다섯 개를 다 처리**합니다. 안 되는 것은 `None` 으로 표시하고 지나갑니다.

## 2-3. 오류 종류별로 다르게 — `except` 여러 개

한 블록에서 여러 종류의 오류가 날 수 있습니다. `except` 를 여러 개 두면 **종류별로** 다르게 대처합니다.

**예상해 보기** — 세 입력 각각 어느 `except` 로 갈까요?
''')

code('''
menu = ["김밥", "라면", "떡볶이"]

for choice in ["1", "5", "둘"]:
    try:
        index = int(choice)                 # "둘" 이면 여기서 ValueError
        print(choice, "→", menu[index])     # 5 면 여기서 IndexError
    except ValueError:
        print(choice, "→ 숫자로 골라 주세요")
    except IndexError:
        print(choice, "→ 0 부터", len(menu) - 1, "사이로 골라 주세요")
''')

md('''
`except` 는 위에서부터 **종류가 맞는 첫 번째** 것이 실행됩니다. 모든 오류를 한꺼번에 받으려면 맨 뒤에 `except Exception as e:` 를 둡니다. `Exception` 은 모든 예외의 부모 클래스입니다(9주차 상속). 다만 **어떤 오류인지 모른 채 삼키면** 나중에 원인을 찾기 어렵습니다. 종류를 아는 오류는 종류로 잡고, 마지막 그물은 안내문을 **출력**합니다.
''')

code('''
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("  0 으로 나눌 수 없습니다")
    except Exception as e:                           # 나머지 전부 — 마지막 그물
        print(f"  예상 못 한 오류: {type(e).__name__}: {e}")
    return None

print(safe_divide(10, 4))
print(safe_divide(10, 0))
print(safe_divide("10", 2))
''')

md(fold("`else` 와 `finally` — 필요할 때 찾아보세요", "`try` 에는 두 블록을 더 붙일 수 있습니다.<br>`else:` — `try` 블록이 <b>오류 없이 끝났을 때만</b> 실행. 오류가 날 수 있는 줄을 `try` 에, 그 결과를 쓰는 줄을 `else` 에 두면 ‘어디서 오류가 났나’가 분명해집니다.<br>`finally:` — 오류가 났든 안 났든 <b>반드시</b> 실행. 파일 닫기, 연결 끊기 같은 뒷정리를 둡니다. 1교시의 `with` 문이 바로 `finally: f.close()` 를 대신 써 주는 것입니다.<br>빈 `except:` (종류를 안 적은 것)는 쓰지 않습니다. 사용자가 중단한 것(`KeyboardInterrupt`)까지 삼켜 프로그램을 끌 수 없게 됩니다."))

md('''
## 2-4. `raise` — 내가 오류를 내다

지금까지는 Python 이 내는 오류를 **받았습니다.** 반대로 **내가 오류를 낼** 수도 있습니다. 왜 일부러 오류를 낼까요?

점수에 `150` 이 들어왔다고 합시다. 조용히 받아들이면 평균이 틀립니다. 그리고 **아무도 모릅니다.** 2-1 의 표에서 가장 찾기 어렵다고 한 **논리 오류**가 됩니다. 잘못된 값은 **들어오는 순간** 큰 소리로 막는 것이 낫습니다. 9주차에 `__init__` 에서 값을 검사하던 것과 같은 생각입니다.
''')

code('''
def register(name, score):
    if not 0 <= score <= 100:
        raise ValueError(f"점수는 0 ~ 100 사이여야 합니다: {name} = {score}")     # 여기서 멈추고 안내합니다
    return {"name": name, "score": score}

print(register("김민준", 88))

try:
    register("박지호", 150)
except ValueError as e:
    print("등록 실패 →", e)
''')

md(key("예외 처리 정리", "① 예외는 실행 <b>도중</b> 상황이 코드의 가정과 다를 때 납니다. 프로그래머의 잘못이 아닌 경우(파일 없음, 입력 오타)가 많으므로 <b>프로그램이 대처</b>해야 합니다.<br>② `try:` 해 보고 `except 종류:` 안 되면. 오류가 나면 `try` 의 나머지를 건너뛰고 `except` 로, 안 나면 `except` 를 건너뜁니다. 어느 쪽이든 <b>그 뒤는 계속</b>됩니다.<br>③ 종류별로 `except` 를 여러 개. `as e` 로 안내문을 받습니다. 빈 `except:` 는 쓰지 않습니다.<br>④ `raise ValueError(\"안내문\")` — 잘못된 값은 조용히 받지 말고 <b>들어오는 순간</b> 막습니다. 논리 오류를 예외로 바꾸는 것입니다.<br>⑤ `try` 의 범위는 <b>작게</b>. 오류가 날 줄만 감싸야 어디서 났는지 압니다."))

# ── 문제 2 ──
md("## 2-5. " + problem(2, "튼튼한 성적 프로그램", "1교시의 `read_scores` 는 파일이 없으면 멈추고, 점수 자리에 <b>‘결석’</b> 같은 글자가 있어도 멈춥니다. 실제 데이터 파일은 늘 이렇습니다. 다음 세 가지를 만족하는 `read_scores_safe(filename)` 을 만드세요.<br>① 파일이 없으면 안내문을 출력하고 <b>빈 딕셔너리</b>를 돌려준다(멈추지 않는다).<br>② 점수가 숫자가 아니거나 칸 수가 맞지 않는 줄은 <b>몇 번째 줄이 왜 문제인지 알리고 건너뛴다.</b><br>③ 나머지 줄은 정상 처리한다. 열 줄 중 두 줄이 이상하면 여덟 명의 딕셔너리를 돌려준다."), part=BOTH)

md('''
이상한 줄이 섞인 데이터 파일을 만듭니다.
''', part=BOTH)

code('''
messy = """김민준,88
이서연,95
박지호,결석
최수아,91
정예준
강하은,85
조시우,79
윤지아,97
장도윤,58
임하린,83
"""
with open("scores_messy.txt", "w", encoding="utf-8") as f:
    f.write(messy)
print(messy)
''', part=BOTH)

md('''
''' + ponder("생각해 보기 — `try` 를 어디에 둘까", "① `try` 로 `open` 부터 끝까지 전부 감싸면 어떻게 될까요? 세 번째 줄에서 오류가 나면 네 번째 줄부터는 읽힐까요?<br>② 그러면 `try` 는 <b>두 군데</b> 있어야 할지도 모릅니다. 어디와 어디인가요? 각각 어떤 오류 종류를 잡아야 하나요?<br>③ `\"정예준\"` 처럼 쉼표가 없는 줄은 `name, score = line.split(\",\")` 에서 어떤 오류가 날까요? 직접 한 줄 실행해 보세요. `\"박지호,결석\"` 은요?<br>④ ‘몇 번째 줄’은 어떻게 셀까요? 1-3 에 힌트가 있습니다.<br>⑤ 이상한 줄을 <b>건너뛸지 멈출지</b>는 누가 정하나요? 프로그래머? 데이터 주인? 둘 다 맞는 답일 때 코드에 무엇을 남겨야 할까요?") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요.
''')
blank()

# ── 문제 2 풀이 ──
md('''
''' + think("오류의 범위를 작게 — 두 겹의 try", "오류가 날 수 있는 곳이 <b>둘</b>입니다. 파일을 <b>여는</b> 순간(파일이 없다)과, 한 <b>줄을 처리</b>하는 순간(글자, 칸 수). 둘의 대처가 다릅니다. 파일이 없으면 <b>전부 포기</b>하고 빈 딕셔너리, 줄 하나가 이상하면 <b>그 줄만 건너뛰고 계속</b>.<br>그래서 `try` 가 두 겹입니다. 바깥 `try` 는 `open` 만 감싸고 `FileNotFoundError` 를 잡습니다. 안쪽 `try` 는 `for` 안에서 <b>한 줄의 처리</b>만 감싸고 `ValueError` 를 잡습니다. `int(\"결석\")` 도, 조각이 하나뿐인 줄을 `name, score` 둘로 받는 것도 모두 `ValueError` 입니다.<br>안쪽 `try` 가 `for` <b>안에</b> 있어야 한 줄에서 오류가 나도 다음 줄로 넘어갑니다. `for` 전체를 감싸면 첫 오류에서 반복이 끝납니다.<br>줄 번호는 `enumerate(f, start=1)`. 건너뛴 줄은 <b>반드시 출력</b>합니다. 조용히 건너뛰면 여덟 명만 남은 이유를 아무도 모릅니다."), part=S)

code('''
def read_scores_safe(filename):
    """이름,점수 파일을 읽어 {이름: 점수} 로. 파일이 없으면 빈 딕셔너리, 이상한 줄은 알리고 건너뛴다."""
    scores = {}
    try:
        f = open(filename, encoding="utf-8")              # 바깥 try — 여는 순간만 감쌉니다
    except FileNotFoundError:
        print(f"⚠️ 파일이 없습니다: {filename}")
        return scores                                     # 빈 딕셔너리 — 멈추지 않습니다

    with f:                                               # 이미 연 파일도 with 로 감싸 자동으로 닫게 합니다
        for lineno, line in enumerate(f, start=1):
            try:                                          # 안쪽 try — 한 줄의 처리만 감쌉니다
                name, score = line.strip().split(",")
                scores[name] = int(score)
            except ValueError as e:
                print(f"  {lineno}번째 줄 건너뜀 {line.strip()!r} — {e}")
    return scores

scores = read_scores_safe("scores_messy.txt")
print(len(scores), "명:", scores)
''', part=S)

code('''
print(read_scores_safe("없는파일.txt"))        # 멈추지 않고 빈 딕셔너리
print(read_scores_safe("scores.txt"))          # 정상 파일은 1교시와 같은 결과
''', part=S)

md('''
세 번째 줄과 다섯 번째 줄이 **왜** 건너뛰어졌는지 안내문이 알려 줍니다. `int("결석")` 은 “invalid literal”, 쉼표 없는 줄은 “not enough values to unpack”. 둘 다 `ValueError` 라 한 `except` 로 잡혔습니다.

건너뛸지 멈출지는 **데이터의 주인이 정할 일**입니다. 결석을 0점으로 칠지, 빼고 평균을 낼지는 프로그래머가 몰래 정하면 안 됩니다. 그래서 코드는 **건너뛰었다는 사실을 출력**으로 남깁니다. 조용한 프로그램이 가장 위험합니다.
''', part=S)

# ═════════════════════════ 함수를 값처럼 ═════════════════════════
md('''
## 2-6. 함수도 값이다 — 일급 객체

1교시 풀이에서 이런 줄이 있었습니다. `max(scores, key=scores.get)`. `scores.get` 뒤에 **괄호가 없습니다.** 함수를 **부른** 것이 아니라 함수 **자체를** 넘긴 것입니다. 5주차의 `sorted(words, key=len)` 도 같았습니다.

**예상해 보기** — `hello` 는 무엇일까요? `hello("민준")` 은요?
''')

code('''
def greet(name):
    return f"안녕, {name}"

hello = greet                 # 괄호 없이 — 함수 자체를 변수에 담았습니다 (부르지 않았습니다)

print(hello("민준"))          # 새 이름으로 부릅니다
print(greet)                  # 함수도 값입니다 — 메모리 어딘가의 객체
print(type(greet))
''')

md('''
함수는 숫자 · 문자열 · 리스트와 **똑같은 자격**을 가진 값입니다. 변수에 담고, 리스트에 넣고, 다른 함수에 **인자로 넘기고**, 함수에서 **돌려줄** 수 있습니다. 이것을 함수가 **일급 객체**(first-class citizen)라고 합니다. ‘일등 시민’, 즉 다른 값과 같은 권리를 가진다는 뜻입니다.

비유하면 함수는 **레시피 카드**입니다. 요리를 하지 않고 카드만 건넬 수 있습니다. 받은 사람이 필요할 때 그 카드대로 요리합니다. `greet` 는 카드, `greet("민준")` 은 요리입니다.
''')

code('''
def shout(text):
    return text.upper() + "!"

def whisper(text):
    return text.lower() + "..."

for style in [shout, whisper, len]:          # 함수들의 리스트 — 내장 함수 len 도 함께
    print(style.__name__, "→", style("Hello World"))
''')

code('''
def apply_twice(func, x):
    """함수를 받아 두 번 적용한다"""
    return func(func(x))

def add_three(n):
    return n + 3

print(apply_twice(add_three, 10))            # add_three(add_three(10)) = 16
print(apply_twice(shout, "hi"))              # shout(shout("hi"))
''')

md(key("일급 객체 정리", "① 함수 이름 뒤에 <b>괄호가 없으면</b> 함수 자체(레시피 카드), <b>괄호가 있으면</b> 부른 결과(요리)입니다.<br>② 함수는 변수에 담고, 리스트에 넣고, 인자로 넘기고, 돌려줄 수 있습니다 — 다른 값과 같은 자격, <b>일급 객체</b>.<br>③ 이미 쓰고 있었습니다: `sorted(..., key=len)`, `max(..., key=scores.get)`. `key=` 에 넘긴 것이 함수입니다.<br>④ ‘함수를 받는 함수’를 쓰면 <b>무엇을 할지</b>를 바꿔 끼울 수 있습니다. 다음 절의 데코레이터가 그 대표입니다."))

md('''
## 2-7. 데코레이터 — 함수를 포장하는 함수

10주차에 선택 정렬과 병합 정렬의 **실행 시간**을 쟀습니다. 함수가 열 개라면 열 함수 안에 모두 시간 재는 코드를 넣어야 할까요? 함수의 **본래 일**(정렬)과 **곁다리 일**(시간 재기)이 섞여 버립니다.

함수가 값이라면 다른 길이 있습니다. **함수를 받아서, 시간 재는 일을 덧붙인 새 함수를 돌려주는 함수**를 만듭니다. 원래 함수는 건드리지 않고 **포장**만 합니다.
''')

code('''
import time

def timed(func):
    """함수를 받아 '실행 시간을 출력하는 함수' 로 포장해서 돌려준다."""
    def wrapper(*args):                                    # *args: 인자를 몇 개든 받아 그대로 넘깁니다
        start = time.perf_counter()
        result = func(*args)                               # 원래 함수를 부르고
        elapsed = time.perf_counter() - start
        print(f"  ⏱ {func.__name__}: {elapsed * 1000:.2f} ms")
        return result                                      # 원래 결과를 그대로 돌려줍니다
    return wrapper                                         # 포장된 함수를 돌려줍니다 — 부르지 않고!

def slow_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

slow_sum = timed(slow_sum)             # 포장한 함수로 바꿔치기 — 이름은 그대로
print(slow_sum(1_000_000))
''')

md('''
`timed(slow_sum)` 은 `slow_sum` 을 **부르지 않습니다.** 받아서 `wrapper` 라는 새 함수 안에 넣고, 그 `wrapper` 를 돌려줍니다. 그 뒤로 `slow_sum(...)` 을 부르면 사실은 `wrapper` 가 실행되고, `wrapper` 가 시간을 재며 원래 함수를 부릅니다. 선물을 포장지로 싸듯, **원래 함수 둘레에 한 겹을 덧댄** 것입니다.

마지막 줄 `slow_sum = timed(slow_sum)` 은 너무 자주 쓰여서 Python 이 줄임 표기를 만들었습니다. 함수 정의 **바로 위에** `@timed` 를 적는 것입니다. 이 표기가 **데코레이터**(decorator)이고, `timed` 처럼 함수를 포장해 돌려주는 함수를 데코레이터 함수라고 합니다.
''')

code('''
@timed                                  # == 아래 함수를 정의한 뒤 slow_max = timed(slow_max)
def slow_max(items):
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best

import random
data = [random.randint(1, 1000) for _ in range(300_000)]
print(slow_max(data))
print(max(data))                        # 내장 max 와 답이 같은지 — 시간은 재지 않았습니다
''')

md('''
`slow_max` 의 본문에는 시간 재는 코드가 **한 줄도 없습니다.** 포장지(`@timed`)를 떼면 평범한 함수로 돌아갑니다. 함수 열 개에 시간을 재려면 열 줄의 `@timed` 면 됩니다.

''' + fold("데코레이터는 어디서 다시 만나나 — 읽을 줄만 알면 됩니다", "앞으로 외부 라이브러리에서 `@` 가 붙은 함수를 자주 봅니다. 모두 ‘이 함수를 라이브러리가 포장한다’는 뜻입니다.<br>· 웹 앱: `@app.route(\"/\")` — 이 함수를 주소 `/` 에 연결해 둔다 (14주차 챗봇 UI 에서 비슷한 모양을 봅니다)<br>· 클래스: `@property`, `@staticmethod` — 메서드의 동작 방식을 바꾼다<br>· 테스트: `@pytest.fixture` — 테스트 준비 함수로 등록한다<br>직접 데코레이터를 쓰는 일은 드뭅니다. `@이름` 이 보이면 ‘아래 함수를 `이름` 이 포장했구나’ 라고 읽으면 됩니다.<br><br>포장된 함수의 `__name__` 을 찍으면 `wrapper` 가 나옵니다. 원래 이름을 유지하려면 `wrapper` 위에 `@functools.wraps(func)` 를 붙입니다. 이것도 데코레이터입니다."))

md(key("데코레이터 정리", "① 데코레이터 함수는 <b>함수를 받아 포장한 새 함수를 돌려주는</b> 함수입니다. 원래 함수는 바뀌지 않습니다.<br>② `@timed` 는 `함수 = timed(함수)` 의 줄임 표기. 정의 <b>바로 위</b>에 적습니다.<br>③ 포장지(`wrapper`)는 <b>원래 함수를 부르고</b>, 그 앞뒤에 곁다리 일(시간 재기, 기록, 검사)을 하고, <b>원래 결과를 돌려줍니다.</b><br>④ 본래 일과 곁다리 일을 분리하는 도구입니다. 함수 열 개에 같은 곁다리를 붙일 때 열 줄로 끝납니다."))

md('''
## 2-8. 타입 힌트 — 읽는 사람을 위한 메모

함수를 쓰려면 **무엇을 넣고 무엇이 나오는지** 알아야 합니다. 1교시의 `read_scores(filename)` — `filename` 은 문자열이겠지요. 돌려주는 것은? 코드를 끝까지 읽어야 딕셔너리임을 압니다. 이것을 함수 머리에 **적어 둘** 수 있습니다.
''')

code('''
def read_scores(filename: str) -> dict:                 # filename 은 str, 돌려주는 것은 dict
    """이름,점수 파일을 읽어 {이름: 점수} 딕셔너리로 돌려준다."""
    scores = {}
    with open(filename, encoding="utf-8") as f:
        for line in f:
            name, score = line.strip().split(",")
            scores[name] = int(score)
    return scores

def average(scores: dict) -> float:
    return sum(scores.values()) / len(scores)

print(average(read_scores("scores.txt")))
''')

md('''
매개변수 뒤의 `: str` 과 괄호 뒤의 `-> dict` 가 **타입 힌트**(type hint)입니다. 힌트라는 이름 그대로, **Python 은 이것을 검사하지 않습니다.**

**예상해 보기** — 힌트와 다른 종류를 넣으면 어떻게 될까요?
''')

code('''
def double(n: int) -> int:
    return n * 2

print(double(21))
print(double("ab"))          # 힌트는 int 인데 문자열을 넣었습니다 — 오류가 날까요?
''')

md('''
오류가 나지 않습니다. 힌트는 **사람이 읽는 메모**이지 검사기가 아닙니다. 그래도 적는 이유는 셋입니다.

1. **6개월 뒤의 나**와 동료가 함수 머리만 보고 쓸 수 있습니다. 본문을 읽지 않아도 됩니다.
2. **편집기와 AI 도구**가 힌트를 읽습니다. 잘못된 종류를 넣으면 실행 전에 밑줄을 그어 주고, 자동완성이 정확해집니다. 12주차 이후 AI 와 함께 코딩할 때 힌트가 있는 코드가 훨씬 잘 통합니다.
3. 요즘 라이브러리의 **문서가 전부 이 모양**입니다. `open(file: str, mode: str = "r", encoding: str | None = None)`. 읽을 줄 알아야 합니다.

| 쓰고 싶은 것 | 힌트 |
|:---|:---|
| 정수 · 실수 · 문자열 · 참/거짓 | `int` `float` `str` `bool` |
| 정수의 리스트 | `list[int]` |
| 문자열 → 정수 딕셔너리 | `dict[str, int]` |
| 돌려주는 것이 없음 | `-> None` |
| 정수 또는 없음(`None`) | `int | None` |

''' + fold("type comment — 옛 방식", "타입 힌트 문법은 Python 3.5(2015년)에 들어왔습니다. 그 전에는 주석으로 적었습니다: `x = 3  # type: int`. 이것을 <b>타입 코멘트</b>(type comment)라고 하며 오래된 코드에서 가끔 보입니다. 새 코드에서는 쓰지 않습니다."))

md(key("타입 힌트 정리", "① `def f(x: int) -> str:` — 매개변수 뒤 `: 종류`, 괄호 뒤 `-> 돌려주는 종류`.<br>② Python 은 <b>검사하지 않습니다.</b> 읽는 사람 · 편집기 · AI 도구를 위한 메모입니다.<br>③ 라이브러리 문서를 읽을 때 필요합니다. `str | None` 은 ‘문자열 또는 None’.<br>④ 이번 학기에는 <b>읽을 줄 알고</b>, 함수 하나에 달아 볼 수 있으면 충분합니다."))

# ── 문제 3 ──
md("## 2-9. " + problem(3, "함수 실행 시간 재기 — 10주차 정렬 두 가지 비교", "10주차의 <b>선택 정렬</b>과 Python 내장 `sorted` 의 실행 시간을 비교하려 합니다. 두 함수의 <b>본문은 손대지 않고</b>, 숫자 2,000개짜리 리스트로 각각 몇 ms 가 걸리는지 출력하세요. 함수가 열 개로 늘어도 같은 방법이 통해야 합니다. 함수 머리에는 타입 힌트를 답니다."), part=BOTH)

md('''
10주차의 선택 정렬을 가져옵니다. 본문은 그대로입니다.
''', part=BOTH)

code('''
def selection_sort(items):
    """가장 작은 것을 찾아 앞으로 — 10주차 2-4"""
    result = list(items)
    n = len(result)
    for i in range(n):
        smallest = i
        for j in range(i + 1, n):
            if result[j] < result[smallest]:
                smallest = j
        result[i], result[smallest] = result[smallest], result[i]
    return result

import random
data = [random.randint(1, 100_000) for _ in range(2_000)]
''', part=BOTH)

md('''
''' + ponder("생각해 보기 — 포장지 한 장으로", "① 데코레이터 없이 재려면 `selection_sort` 본문 어디에 무엇을 넣어야 하나요? `sorted` 는 내장 함수라 본문이 없습니다. 어떻게 하죠?<br>② 2-7 의 `timed` 가 <b>돌려주는 것</b>은 숫자인가요, 함수인가요? `timed(selection_sort)` 를 변수에 담으면 그 변수는 무엇이 되나요?<br>③ 내장 `sorted` 에 `@` 를 붙일 수는 없습니다(정의한 곳이 우리 코드가 아니니까요). 그래도 `timed` 로 포장할 방법이 있을까요? 2-7 의 <b>첫 번째</b> 방법을 떠올려 보세요.<br>④ 포장된 함수가 돌려주는 정렬 결과는 원래와 같을까요? 어떻게 확인할까요?<br>⑤ `timed` 의 매개변수 `func` 와 돌려주는 값에 타입 힌트를 단다면 무엇이라고 적을까요? (힌트: `from typing import Callable` — ‘부를 수 있는 것’)") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요.
''')
blank()

# ── 문제 3 풀이 ──
md('''
''' + think("함수를 값으로 다루면 본문을 열지 않아도 된다", "본문에 손대지 않고 곁다리 일을 붙이는 도구가 데코레이터였습니다. `timed` 는 함수를 받아 <b>함수를 돌려주므로</b>, 돌려받은 것을 변수에 담으면 그 변수가 곧 ‘시간을 재는 정렬 함수’입니다.<br>우리가 정의한 함수는 `@timed` 로, 남이 만든 `sorted` 는 `timed(sorted)` 로 — <b>같은 일</b>입니다. `@` 는 줄임 표기일 뿐이니까요.<br>결과가 같은지는 `==` 로 비교합니다. 포장지는 원래 결과를 그대로 돌려주므로 같아야 합니다.<br>타입 힌트: 함수를 받아 함수를 돌려주니 `Callable -> Callable`. `typing` 모듈의 `Callable` 이 ‘부를 수 있는 것’이라는 뜻입니다."), part=S)

code('''
import time
from typing import Callable

def timed(func: Callable) -> Callable:
    """함수를 받아 '실행 시간을 출력하는 함수' 로 포장해서 돌려준다."""
    def wrapper(*args):
        start = time.perf_counter()
        result = func(*args)
        elapsed = time.perf_counter() - start
        print(f"  ⏱ {func.__name__}: {elapsed * 1000:.2f} ms")
        return result
    return wrapper

@timed                                             # 우리가 정의한 함수 — @ 로 포장
def selection_sort(items: list[int]) -> list[int]:
    """가장 작은 것을 찾아 앞으로 — 10주차 2-4"""
    result = list(items)
    n = len(result)
    for i in range(n):
        smallest = i
        for j in range(i + 1, n):
            if result[j] < result[smallest]:
                smallest = j
        result[i], result[smallest] = result[smallest], result[i]
    return result

timed_sorted = timed(sorted)                       # 남이 만든 함수 — 직접 포장

a = selection_sort(data)
b = timed_sorted(data)
print("결과가 같은가?", a == b)
''', part=S)

md('''
선택 정렬은 수십 ~ 수백 ms, 내장 `sorted` 는 1 ms 안팎입니다. 10주차에서 본 $n^2$ 과 $n \\log n$ 의 차이이고, 거기에 `sorted` 는 C 언어로 짜여 있다는 차이가 더해졌습니다. 두 함수의 본문에는 시간 재는 코드가 없습니다. 함수가 열 개여도 `@timed` 열 줄, 또는 `timed(함수)` 열 번입니다.
''', part=S)

md(key("2교시 정리", "① <b>예외</b>는 실행 도중 밖의 사정이 코드의 가정과 다를 때 납니다. `try` · `except` 로 받아 프로그램이 <b>멈추지 않게</b> 하고, 종류별로 다르게 대처합니다. 범위는 작게, 건너뛴 사실은 출력으로 남깁니다.<br>② `raise` 로 잘못된 값을 들어오는 순간 막습니다. 조용한 논리 오류보다 시끄러운 예외가 낫습니다.<br>③ 함수는 <b>값</b>입니다(일급 객체). 괄호 없이 쓰면 함수 자체, 괄호를 붙이면 결과. `key=len` 이 그것이었습니다.<br>④ <b>데코레이터</b>는 함수를 받아 포장한 함수를 돌려줍니다. `@timed` 는 `f = timed(f)`. 본래 일과 곁다리 일을 분리합니다.<br>⑤ <b>타입 힌트</b> `def f(x: int) -> str` 는 검사하지 않는 메모입니다. 읽는 사람 · 편집기 · AI 도구를 위한 것입니다."), part=S)

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "안전한 변환", "약 3분",
         "문자열을 <b>실수</b>로 바꿔 돌려주는 `to_number(text)` 를 쓰세요. 바꿀 수 없으면 오류 대신 `None` 을 돌려줍니다.<br>`to_number(\"3.5\")` → `3.5`, `to_number(\"42\")` → `42.0`, `to_number(\"abc\")` → `None`",
         '''
# 여기에 함수를 정의하세요


for text in ["3.5", "42", "abc", "", " 7 "]:
    print(repr(text), "→", to_number(text))
''',
         'to_number("3.5") == 3.5 and to_number("42") == 42.0 and to_number("abc") is None and to_number("") is None and to_number(" 7 ") == 7.0',
         '''
def to_number(text):
    try:
        return float(text)
    except ValueError:
        return None

for text in ["3.5", "42", "abc", "", " 7 "]:
    print(repr(text), "→", to_number(text))
''', raises=True, heading="## 2교시 실습")

practice("✏️ 실습 2-2", "숫자 파일 읽기 — 파일과 예외를 함께", "약 6분",
         "한 줄에 숫자 하나씩 적힌 파일을 읽어 <b>실수 리스트</b>를 돌려주는 `read_numbers(filename)` 을 쓰세요.<br>· 숫자로 바꿀 수 없는 줄(글자, 빈 줄)은 <b>건너뜁니다.</b><br>· 파일이 없으면 <b>빈 리스트</b>를 돌려줍니다(멈추지 않습니다).<br>아래 셀이 먼저 `numbers.txt` 를 만들어 둡니다. 문제 2 의 ‘두 겹의 try’ 모양 그대로입니다. 실습 2-1 의 `to_number` 를 써도 됩니다.<br>`read_numbers(\"numbers.txt\")` → `[1.0, 2.5, 4.0]`, `read_numbers(\"없음.txt\")` → `[]`",
         '''
with open("numbers.txt", "w", encoding="utf-8") as f:
    f.write("1\\n2.5\\nx\\n\\n4\\n")

# 여기에 함수를 정의하세요


print(read_numbers("numbers.txt"))
print(read_numbers("없음.txt"))
''',
         'read_numbers("numbers.txt") == [1.0, 2.5, 4.0] and read_numbers("없음_점검용.txt") == [] and (lambda fn: (open(fn, "w", encoding="utf-8").write("10\\n -3 \\nabc\\n0.5\\n"), read_numbers(fn) == [10.0, -3.0, 0.5])[-1])("_check_numbers.txt")',
         '''
def read_numbers(filename):
    numbers = []
    try:
        f = open(filename, encoding="utf-8")
    except FileNotFoundError:
        return numbers                        # 빈 리스트
    with f:
        for line in f:
            try:
                numbers.append(float(line))   # float 도 앞뒤 공백과 \\n 은 봐줍니다
            except ValueError:
                pass                          # 숫자가 아닌 줄은 건너뜁니다
    return numbers

print(read_numbers("numbers.txt"))            # [1.0, 2.5, 4.0]
print(read_numbers("없음.txt"))               # []
''', raises=True)

practice("✏️ 실습 2-3", "데코레이터 — 느낌표 붙이기", "약 5분",
         "문자열을 돌려주는 <b>인자 하나짜리</b> 함수를 받아, 결과 끝에 `\"!\"` 를 붙여 돌려주는 함수로 포장하는 데코레이터 `exclaim(func)` 을 쓰세요. 2-7 의 `timed` 와 같은 모양입니다. 포장지(`wrapper`)는 원래 함수를 부르고, 그 결과에 `\"!\"` 를 붙여 돌려줍니다.<br>`@exclaim` 을 붙인 `greet(\"민준\")` → `\"안녕, 민준!\"`",
         '''
# 여기에 데코레이터를 정의하세요


@exclaim
def greet(name):
    return f"안녕, {name}"

print(greet("민준"))
print(exclaim(str.upper)("python"))       # 내장 메서드도 포장됩니다
''',
         'exclaim(str.upper)("python") == "PYTHON!" and greet("민준") == "안녕, 민준!" and exclaim(lambda s: s * 2)("ab") == "abab!"',
         '''
def exclaim(func):
    def wrapper(x):
        return func(x) + "!"             # 원래 함수를 부르고, 결과에 덧붙여 돌려줍니다
    return wrapper                       # 포장된 함수를 돌려줍니다

@exclaim
def greet(name):
    return f"안녕, {name}"

print(greet("민준"))                     # 안녕, 민준!
print(exclaim(str.upper)("python"))      # PYTHON!
''', raises=True)

practice("✏️ 실습 2-4", "타입 힌트 달기", "약 2분",
         "직사각형의 넓이를 돌려주는 `area(width, height)` 를 쓰고, 두 매개변수와 돌려주는 값에 모두 `float` 힌트를 다세요.<br>점검 셀은 함수의 `__annotations__` (힌트를 모아 둔 딕셔너리)를 봅니다. 힌트가 동작에 영향을 주지 않는다는 것도 확인해 보세요 — `area(2, 3)` 은 정수를 넣어도 됩니다.",
         '''
# 여기에 함수를 정의하세요


print(area(2.5, 4))
print(area.__annotations__)
''',
         'area.__annotations__ == {"width": float, "height": float, "return": float} and area(2.5, 4) == 10.0 and area(2, 3) == 6',
         '''
def area(width: float, height: float) -> float:
    return width * height

print(area(2.5, 4))                      # 10.0
print(area.__annotations__)              # {'width': <class 'float'>, 'height': <class 'float'>, 'return': <class 'float'>}
''', raises=True)

# ═════════════════════════ 주차 정리 ═════════════════════════
NEXT_WEEK = f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 12주차 외부 라이브러리와 가상환경</b><br>
남이 만든 코드를 설치해 쓰는 법(오픈소스 라이브러리)과, 프로젝트마다 라이브러리를 따로 두는 <b>가상환경</b>을 배웁니다. 오늘 배운 데코레이터와 타입 힌트가 라이브러리 문서 곳곳에 나옵니다.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 노트북을 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
'''

md('''
# 11주차 마무리

오늘 프로그램은 처음으로 **코드 밖**의 데이터를 읽고 썼고, 밖의 사정(파일 없음, 이상한 줄)에 **멈추지 않고 대처**했습니다. 그리고 함수가 값이라는 사실에서 데코레이터와 타입 힌트까지 왔습니다.

칠판의 풀이와 개념 정리, 세 문제의 완성된 코드가 들어 있는 **풀이판** 노트북은 수업이 끝난 뒤 수업 사이트에 올립니다. 오늘 빈 셀에 직접 쓴 코드와 풀이판의 코드를 **비교**해 보세요.

''' + key("오늘의 한 문장", "프로그램은 코드 안의 세상에서는 전능하지만, 코드 밖의 세상은 뜻대로 되지 않습니다. 파일은 없을 수 있고 데이터는 더러울 수 있습니다. <b>그래도 멈추지 않고, 무엇을 건너뛰었는지 말하는 프로그램</b>이 좋은 프로그램입니다.") + "\n\n" + NEXT_WEEK)

md('''
# 11주차 정리

| 개념 | 한 줄 요약 | 기본형 |
|:---|:---|:---|
| **파일** | 프로그램이 끝나도 남는, 이름 붙은 바이트의 줄 | 텍스트 파일 = 인코딩된 문자열 |
| **열기 · 닫기** | `with` 가 블록 끝에서 자동으로 닫는다 | `with open(이름, 모드, encoding="utf-8") as f:` |
| **쓰기** | `"w"` 지우고 새로 · `"a"` 덧붙여. 문자열만, 줄바꿈은 직접 | `f.write(f"{x}\\n")` |
| **읽기** | 전체 · 한 줄씩 · 줄 리스트 | `f.read()` · `for line in f` · `f.read().splitlines()` |
| **한 줄 처리** | `\\n` 떼고, 쪼개고, 숫자로 | `name, score = line.strip().split(",")` |
| **인코딩** | 안 적으면 운영체제 기본값. Windows 는 cp949 일 수 있다 | 항상 `encoding="utf-8"` |
| **예외** | 실행 도중 가정과 다른 상황. 프로그램이 대처할 수 있는 유일한 오류 | `try:` … `except 종류 as e:` |
| **여러 except** | 종류별로 다르게. 마지막 그물은 `Exception`, 빈 `except:` 는 금지 | 범위는 작게, 건너뛴 것은 출력 |
| **raise** | 잘못된 값을 들어오는 순간 막는다 | `raise ValueError("안내문")` |
| **일급 객체** | 함수도 값. 괄호 없으면 함수 자체, 있으면 결과 | `key=len`, `apply_twice(func, x)` |
| **데코레이터** | 함수를 받아 포장한 함수를 돌려준다 | `@timed` == `f = timed(f)` |
| **타입 힌트** | 검사하지 않는 메모. 읽는 사람 · 편집기 · AI 를 위해 | `def f(x: int) -> str:` |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| `FileNotFoundError` | 그 파일이 없다 | 이름 오타 · 다른 폴더 |
| `ValueError` | 값이 이상하다 | `int("결석")` · 조각 수가 안 맞는 `name, score = ...` · 닫힌 파일에 쓰기 |
| `TypeError` | 종류가 안 맞는다 | `f.write(42)` · `"10" / 2` |
| `UnicodeDecodeError` | 그 인코딩으로 못 읽는다 | UTF-8 파일을 cp949 로 |
| 줄 사이가 비어 보임 | 오류는 아니지만 신호 | `\\n` 을 안 뗀 `line` 을 `print` |
| 두 번째 `read()` 가 빈 문자열 | 오류는 아니지만 신호 | 읽는 위치가 끝에 가 있다 — 다시 연다 |
| 조용히 틀린 평균 | 가장 무서운 신호 | 150점을 검사 없이 받음 — `raise` 로 막는다 |

''' + key("오늘의 한 문장", "프로그램은 코드 안의 세상에서는 전능하지만, 코드 밖의 세상은 뜻대로 되지 않습니다. 파일은 없을 수 있고 데이터는 더러울 수 있습니다. <b>그래도 멈추지 않고, 무엇을 건너뛰었는지 말하는 프로그램</b>이 좋은 프로그램입니다.") + "\n\n" + NEXT_WEEK, part=S)

# ═════════════════════════ 과제 ═════════════════════════ (생각하기 판에만. 정답은 교수용 파일)
FIRST_HW_CELL = len(CELLS)

md(f'''
# 11주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">파일 · 예외 · 함수를 값처럼</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>4 ~ 10주차의 문법과 오늘 배운 것만으로 풀 수 있습니다</li><li>파일을 만드는 과제는 셀을 다시 실행해도 결과가 같아야 합니다 (<code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">"w"</code> 와 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">"a"</code> 를 구별하세요)</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 함수 이름과 매개변수 순서를 바꾸지 마세요. 점검 셀이 그 이름으로 부릅니다.<br>③ 점검 셀은 예시와 <b>다른 파일 · 다른 값</b>으로도 함수를 부릅니다. 파일 이름을 코드 안에 고정하지 말고 매개변수로 받으세요.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다."))

practice("📝 과제 1", "구구단 파일 쓰기", "",
         "`write_table(filename, n)` — `n` 단을 `filename` 파일에 <b>새로</b> 씁니다(셀을 다시 실행해도 9줄). 한 줄의 모양은 `7 x 3 = 21` 이고 1 부터 9 까지 아홉 줄입니다. 돌려주는 값은 없습니다.<br>`write_table(\"table7.txt\", 7)` 뒤 파일의 셋째 줄 → `7 x 3 = 21`",
         '''
# 여기에 함수를 정의하세요


write_table("table7.txt", 7)
with open("table7.txt", encoding="utf-8") as f:
    print(f.read())
''',
         '(lambda fn: (write_table(fn, 7), write_table(fn, 7), open(fn, encoding="utf-8").read().splitlines())[-1])("_check_table.txt") == [f"7 x {i} = {7 * i}" for i in range(1, 10)] and (lambda fn: (write_table(fn, 12), open(fn, encoding="utf-8").read().splitlines()[-1])[-1])("_check_table12.txt") == "12 x 9 = 108"',
         '''
def write_table(filename, n):
    with open(filename, "w", encoding="utf-8") as f:      # "w" — 다시 실행해도 9줄
        for i in range(1, 10):
            f.write(f"{n} x {i} = {n * i}\\n")

write_table("table7.txt", 7)
with open("table7.txt", encoding="utf-8") as f:
    print(f.read())
''', raises=True, show_answer=False)

practice("📝 과제 2", "가장 긴 줄", "",
         "`longest_line(filename)` — 파일에서 <b>가장 긴 줄</b>을 돌려줍니다(줄 끝의 `\\n` 은 뗀 상태로). 길이가 같은 줄이 여럿이면 먼저 나온 것. 파일이 비어 있으면 빈 문자열 `\"\"`.<br>힌트: 줄 리스트를 만든 뒤 `max(lines, key=len)` — 오늘 배운 ‘함수를 값으로 넘기기’입니다. 빈 리스트에 `max` 를 쓰면 `ValueError` 가 나니 미리 확인하거나 예외로 받으세요.<br>`longest_line(\"poem.txt\")` → `\"죽는 날까지 하늘을 우러러\"`",
         '''
# 여기에 함수를 정의하세요


print(longest_line("poem.txt"))
''',
         'longest_line("poem.txt") == "죽는 날까지 하늘을 우러러" and (lambda fn: (open(fn, "w", encoding="utf-8").write("ab\\nabcd\\nabc\\nabcd\\n"), longest_line(fn) == "abcd")[-1])("_check_longest.txt") and (lambda fn: (open(fn, "w", encoding="utf-8").close(), longest_line(fn) == "")[-1])("_check_empty.txt")',
         '''
def longest_line(filename):
    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines:                              # 빈 파일 — max 를 부르면 ValueError 이므로 미리 거릅니다
        return ""
    return max(lines, key=len)                 # 길이가 가장 긴 줄 (같으면 먼저 나온 것)

print(longest_line("poem.txt"))                # 죽는 날까지 하늘을 우러러
''', raises=True, show_answer=False)

practice("📝 과제 3", "날짜 문자열 읽기 — 예외로 거르기", "",
         "`parse_date(text)` — `\"2026-11-10\"` 모양의 문자열을 받아 정수 튜플 `(2026, 11, 10)` 을 돌려줍니다. 모양이 다르면(조각이 셋이 아니다, 숫자가 아니다) 오류 대신 `None`.<br>힌트: `\"-\"` 로 쪼개 `year, month, day = ...` 로 받고 각각 `int()`. 조각 수가 안 맞아도, 숫자가 아니어도 모두 `ValueError` 입니다 — 문제 2 와 같습니다.<br>`parse_date(\"2026-11-10\")` → `(2026, 11, 10)`, `parse_date(\"2026-11\")` → `None`, `parse_date(\"2026-1a-10\")` → `None`",
         '''
# 여기에 함수를 정의하세요


for text in ["2026-11-10", "2026-11", "2026-1a-10", "11/10/2026", "1999-1-1"]:
    print(repr(text), "→", parse_date(text))
''',
         'parse_date("2026-11-10") == (2026, 11, 10) and parse_date("1999-1-1") == (1999, 1, 1) and parse_date("2026-11") is None and parse_date("2026-1a-10") is None and parse_date("11/10/2026") is None and parse_date("") is None and parse_date("a-b-c-d") is None',
         '''
def parse_date(text):
    try:
        year, month, day = text.split("-")       # 조각이 셋이 아니면 ValueError
        return (int(year), int(month), int(day)) # 숫자가 아니면 ValueError
    except ValueError:
        return None

for text in ["2026-11-10", "2026-11", "2026-1a-10", "11/10/2026", "1999-1-1"]:
    print(repr(text), "→", parse_date(text))
''', raises=True, show_answer=False)

practice("📝 과제 4", "데코레이터 — 오류를 None 으로", "",
         "데코레이터 `safe(func)` 를 쓰세요. 포장된 함수는 원래 함수가 <b>어떤 예외든</b> 내면 멈추는 대신 `None` 을 돌려주고, 오류가 없으면 원래 결과를 돌려줍니다. 인자 수는 몇 개든 됩니다(`*args`).<br>힌트: 2-7 의 `timed` 모양에서 시간 재는 자리에 `try` · `except Exception` 을 둡니다. 예외 처리와 데코레이터를 한 번에 쓰는 문제입니다.<br>`safe(int)(\"x\")` → `None`, `@safe` 를 붙인 `divide(1, 0)` → `None`, `divide(6, 3)` → `2.0`",
         '''
# 여기에 데코레이터를 정의하세요


@safe
def divide(a, b):
    return a / b

print(divide(6, 3), divide(1, 0))
print(safe(int)("42"), safe(int)("x"))
''',
         'divide(6, 3) == 2.0 and divide(1, 0) is None and safe(int)("42") == 42 and safe(int)("x") is None and safe(lambda items: items[5])([1, 2]) is None and safe(len)("abc") == 3',
         '''
def safe(func):
    def wrapper(*args):
        try:
            return func(*args)
        except Exception:                  # 어떤 예외든 — None 으로
            return None
    return wrapper

@safe
def divide(a, b):
    return a / b

print(divide(6, 3), divide(1, 0))          # 2.0 None
print(safe(int)("42"), safe(int)("x"))     # 42 None
''', raises=True, show_answer=False)

practice("📝 과제 5", "단어 빈도 (도전)", "",
         "`word_freq(filename)` — 텍스트 파일을 읽어 `{단어: 횟수}` 딕셔너리를 돌려줍니다. 단어는 공백으로 나뉜 조각이고, <b>소문자로 바꿔</b> 셉니다(`Python` 과 `python` 은 같은 단어). 파일이 없으면 빈 딕셔너리.<br>🧠 6주차 딕셔너리 세기 패턴: `counts[word] = counts.get(word, 0) + 1`. 파일 읽기는 문제 2 의 바깥 `try`.<br>`word_freq` 로 `poem.txt` 를 세면 `\"바람에도\"` 는 1 번입니다.",
         '''
# 여기에 함수를 정의하세요


freq = word_freq("poem.txt")
print(len(freq), "종류")
print(sorted(freq.items(), key=lambda item: item[1], reverse=True)[:5])    # 많이 나온 순 5개
''',
         '(lambda fn: (open(fn, "w", encoding="utf-8").write("a B a\\nc A b\\n"), word_freq(fn) == {"a": 3, "b": 2, "c": 1})[-1])("_check_freq.txt") and word_freq("없음_점검용.txt") == {} and word_freq("poem.txt").get("바람에도") == 1 and len(word_freq("poem.txt")) == 16',
         '''
def word_freq(filename):
    counts = {}
    try:
        f = open(filename, encoding="utf-8")
    except FileNotFoundError:
        return counts
    with f:
        for word in f.read().split():
            word = word.lower()
            counts[word] = counts.get(word, 0) + 1
    return counts

freq = word_freq("poem.txt")
print(len(freq), "종류")                   # 16 종류
print(sorted(freq.items(), key=lambda item: item[1], reverse=True)[:5])
''', raises=True, show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다. (과제 2 · 5는 실습 1-2 의 `poem.txt` 셀이 먼저 실행되어 있어야 합니다.)<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
def pick(part):
    """해당 판에 들어갈 셀만 (type, source, meta) 로 돌려준다"""
    return [(t, s, m) for t, s, m, p in CELLS if p == part or p == BOTH]


THINK_CELLS = pick(T)
SOLVE_CELLS = pick(S)


def to_nb(cells, prefix):
    out, seen = [], set()
    for i, (ctype, src, meta) in enumerate(cells):
        cid = hashlib.md5(f"{prefix}-{i}-{src}".encode("utf-8")).hexdigest()[:8]
        assert cid not in seen
        seen.add(cid)
        lines = src.split("\n")
        source = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]
        cell = {"cell_type": ctype, "id": cid, "metadata": meta, "source": source}
        if ctype == "code":
            cell = {"cell_type": ctype, "execution_count": None, "id": cid, "metadata": meta, "outputs": [], "source": source}
        out.append(cell)
    return {
        "cells": out,
        "metadata": {"colab": {"provenance": [], "toc_visible": True},
                     "kernelspec": {"display_name": "Python 3", "name": "python"},
                     "language_info": {"name": "python"}},
        "nbformat": 4, "nbformat_minor": 5,
    }


def save(nb, path):
    assert not os.path.exists(path), f"이미 있는 파일입니다: {path}"
    text = json.dumps(nb, ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n"))


def hw_solution_cells():
    cells = [("markdown", "# 컴퓨팅사고 11주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 수업용 노트북 `" + THINK_NB + "` 맨 끝 ‘11주차 과제’의 정답 예시입니다. 과제 2 · 5는 실습 1-2 의 `poem.txt` 가 있어야 합니다(아래 첫 코드 셀에 복사해 둠).", {})]
    cells.append(("code", '''
with open("poem.txt", "w", encoding="utf-8") as f:
    f.write("죽는 날까지 하늘을 우러러\\n한 점 부끄럼이 없기를,\\n잎새에 이는 바람에도\\n나는 괴로워했다.\\n별을 노래하는 마음으로\\n")
'''.strip("\n"), {}))
    for name, sol, chk in PRACTICES:
        if not name.startswith("과제"):
            continue
        expected = chk.split("lambda: ", 1)[1][:-1]
        cells.append(("markdown", f"## {name}\n\n자가 점검 기준: `{expected}`", {}))
        cells.append(("code", sol, {}))
    return cells


if __name__ == "__main__":
    for label, cells in [("생각하기", THINK_CELLS), ("풀이", SOLVE_CELLS)]:
        n_code = sum(1 for c in cells if c[0] == "code")
        print(f"{label}: cells={len(cells)} code={n_code}")
    # 생각하기 판에 🧠 풀이 상자 · 정답이 없고, 풀이판에 🤔 · 빈 셀 · 실습 상자가 없는지 확인
    assert not [s for t, s, m in THINK_CELLS if '">🧠' in s or "💡" in s], "생각하기 판에 풀이가 섞임"
    assert not [s for t, s, m in SOLVE_CELLS if "🤔" in s or s.startswith("# 칠판의 풀이") or ("✏️ 실습 " in s and "정답" not in s)], "풀이판에 수업용 셀이 섞임"
    print(f"practices={len(PRACTICES)} first_hw_cell={FIRST_HW_CELL}")
    if "--write" in sys.argv:
        save(to_nb(THINK_CELLS, "w11t"), os.path.join(DEST, THINK_NB))
        save(to_nb(SOLVE_CELLS, "w11s"), os.path.join(DEST, SOLVE_NB))
        save(to_nb(hw_solution_cells(), "w11h"), os.path.join(DEST, HW_SOL))
        print("saved:", THINK_NB, "/", SOLVE_NB, "/", HW_SOL)

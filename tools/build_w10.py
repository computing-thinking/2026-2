import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 10주차 노트북(강의용 + 과제 정답) 생성 스크립트 — build_w9.py 를 복제해 작성
# 주제: 고급 알고리듬 — 어려운 문제를 컴퓨팅 사고로 푸는 법 (재귀 · 동적 프로그래밍 · 그래프 모델링)
# 예제 문제 5개: 하노이 탑 · 계단 오르기(피보나치) · 거스름돈 · 쾨니히스베르크 다리 · 미로 최단 경로
# 사용: python build_w10.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w10.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
LECTURE = "컴퓨팅사고_10주차_알고리듬.ipynb"
HW_SOL = "컴퓨팅사고_10주차_과제정답.ipynb"

# ───────────────────────── HTML 상자 (9주차 노트북과 같은 값) ─────────────────────────
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


def warn(title, body):
    return (f'<div style="background:#FFF0EE;color:#1F2937;border-left:6px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#FF6B5A;">⚠️ {fmt(title)}</b><br>{fmt(body)}</div>')


def think(title, body):
    """🧠 컴퓨팅 사고 상자 — 문제를 푸는 '생각의 단계'를 정리할 때"""
    return (f'<div style="background:#FFF7E6;color:#1F2937;border-left:6px solid #F59E0B;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#B45309;">🧠 {fmt(title)}</b><br>{fmt(body)}</div>')


def task_box(label, title, minutes, body):
    m = f' <span style="color:#6B7280;font-weight:normal;">({minutes})</span>' if minutes else ""
    return (f'<div style="background:#FFFFFF;color:#1F2937;border:2px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:12px;margin:8px 0;line-height:1.7;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;'
            f'padding:2px 12px;border-radius:999px;font-weight:bold;">{label}</span>&nbsp; <b>{title}</b>{m}<br>{fmt(body)}</div>')


def boom(text):
    return ('<span style="background:#FFF0EE;color:#FF6B5A;border:1px solid #FF6B5A;padding:2px 10px;'
            f'border-radius:999px;font-weight:bold;">💥 일부러 오류를 내는 셀 — {text}</span>')


def answer(code):
    return ('<details><summary><b>💡 정답 예시 보기 — 먼저 스스로 풀어 본 뒤에 열어 보세요</b></summary>'
            '<pre style="background:#1F2937;color:#F9FAFB;padding:14px 16px;border-radius:10px;font-family:Consolas,monospace;'
            f'line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;box-sizing:border-box;max-width:100%;">{html.escape(code.strip())}</pre></details>')


def period(n, title, goals):
    lis = "".join(f"<li>{g}</li>" for g in goals)
    return (f'<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}">'
            f'<span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">{n}교시</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">{title}</span>'
            f'<span style="float:right;opacity:0.9;">⏱ 약 50분</span>'
            f'<ul style="margin:10px 0 0 0;line-height:1.7;">{lis}</ul></div>')


def problem(n, title, question):
    """문제 N 표지 — 다섯 문제의 시작을 알리는 띠"""
    return (f'<div style="background:#1F2937;color:#F9FAFB;padding:14px 22px;border-radius:12px;margin:12px 0;{BOX}">'
            f'<span style="background:#F59E0B;color:#1F2937;padding:3px 14px;border-radius:999px;font-weight:bold;">문제 {n}</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.3em;font-weight:bold;">{title}</span>'
            f'<div style="margin-top:8px;opacity:0.92;line-height:1.7;">{fmt(question)}</div></div>')


BREAK = '<div style="text-align:center;color:#6B7280;">☕ 쉬는 시간 — 10분</div>'
CHECK_HEAD = "# 🔍 자가 점검 — 수정하지 말고 실행만 하세요\n"

# ───────────────────────── 셀 모으기 ─────────────────────────
CELLS = []          # (type, source, metadata)
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w10.py 가 사용


def md(src):
    CELLS.append(("markdown", src.strip("\n"), {}))


def code(src, raises=False, form=False):
    meta = {}
    if raises:
        meta["tags"] = ["raises-exception"]
    if form:
        meta["cellView"] = "form"
        meta["jupyter"] = {"source_hidden": True}
    CELLS.append(("code", src.strip("\n"), meta))


def practice(label, title, minutes, body, skeleton, test, solution, raises=False, heading=None, show_answer=True,
             extra=None, extra_raises=False):
    """✏️ 상자 → 작성용 셀 → (추가 셀) → 🔍 점검 셀 → 💡 정답(접힘)"""
    box = task_box(label, title, minutes, body)
    md((heading + "\n\n" if heading else "") + box)
    code(skeleton, raises=raises)
    if extra:
        code(extra, raises=extra_raises)
    name = label.split(" ", 1)[1]
    chk = CHECK_HEAD + f'check("{name}", lambda: {test})'
    code(chk)
    if show_answer:
        md(answer(solution))
    PRACTICES.append((name, solution.strip("\n"), chk))


# ═════════════════════════ 표지 · 안내 ═════════════════════════
md(f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:34px 36px;border-radius:18px;{BOX}">
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 10주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">고급 알고리듬 — 어려운 문제를 컴퓨팅 사고로 풀다</div>
<div style="font-size:1.25em;margin-top:6px;">재귀 &nbsp;·&nbsp; 동적 프로그래밍 &nbsp;·&nbsp; 그래프 모델링 &nbsp;·&nbsp; 다섯 개의 고전 문제</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>
</div>
''')

md('''
# 10주차 학습 안내

4주차부터 9주차까지 Python 의 **문법**을 배웠습니다. 변수 · 조건 · 반복 · 함수 · 클래스. 이제 도구는 갖추어졌습니다.
이번 주에는 문법을 새로 배우지 않습니다. 대신 **문법만으로는 풀리지 않는 문제**를 다섯 개 가져와, 3주차에 배운 **컴퓨팅 사고**의 네 요소로 어떻게 풀어 가는지 봅니다.

| 교시 | 생각의 도구 | 문제 |
|:---:|:---|:---|
| **1교시** | **재귀** — 문제를 같은 모양의 더 작은 문제로 쪼갠다 | ① 하노이 탑 |
| **2교시** | **동적 프로그래밍** — 작은 답을 기억해 큰 답을 만든다 | ② 계단 오르기 &nbsp; ③ 거스름돈 |
| **3교시** | **그래프 모델링** — 문제를 점과 선으로 추상화한다 | ④ 쾨니히스베르크의 다리 &nbsp; ⑤ 미로 최단 경로 |

다섯 문제 모두 수백 년 된 고전이거나 모든 컴퓨터과학 교과서에 나오는 문제입니다. 문제 자체보다 **푸는 방법의 모양**이 중요합니다. 오늘 배운 모양은 여러분 전공의 문제에서 다시 나타납니다.

**오늘 수업을 마치면**

1. 재귀 함수의 두 조건(멈추는 경우, 작아지는 문제)을 알고, 하노이 탑처럼 ‘같은 모양의 작은 문제’로 쪼개는 문제를 재귀로 풀 수 있습니다.
2. 같은 계산을 되풀이하는 재귀가 왜 느려지는지 설명하고, 메모이제이션과 표 채우기(동적 프로그래밍)로 고칠 수 있습니다.
3. 쉬워 보이는 방법(탐욕법)이 틀리는 경우를 반례로 보이고, 동적 프로그래밍으로 올바른 답을 구할 수 있습니다.
4. 현실 문제를 그래프(점과 선)로 추상화하고, 큐를 이용한 너비 우선 탐색으로 최단 경로를 찾을 수 있습니다.

''' + key("이 노트북을 읽는 법", "회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요.<br>🧠 <b>컴퓨팅 사고</b> 상자는 코드가 아니라 <b>생각의 순서</b>를 적은 곳입니다. 오늘은 이 상자가 가장 중요합니다. 코드는 생각이 정리된 뒤에 따라 나옵니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다."))

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · 재귀 — 문제를 같은 모양의 작은 문제로 쪼개다\n\n" + period(1, "재귀와 하노이 탑", [
    "자기 자신을 부르는 함수(재귀)가 어떻게 끝나는지 호출 스택으로 설명한다",
    "재귀의 두 조건 — 멈추는 경우와 작아지는 문제 — 를 안다",
    "하노이 탑을 ‘n−1 개 옮기기’라는 같은 모양의 작은 문제로 분해해 푼다",
    "재귀와 반복 중 무엇을 쓸지 고르는 기준을 세운다",
]))

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
    @staticmethod
    def find_spec(name, path=None, target=None):
        _il.invalidate_caches()
        return None

if not any(type(f).__name__ == "_RefreshFinder" for f in _sys.meta_path):
    _sys.meta_path.insert(0, _RefreshFinder())

print("준비 완료! 이제 수업을 시작합니다.")
''', form=True)

md('''
## 1-1. 어려운 문제란 무엇인가 — 3주차를 다시 꺼내며

3주차에 컴퓨팅 사고의 네 요소를 배웠습니다. 그때는 말로만 했고, 이제는 코드로 할 수 있습니다.

| 요소 | 한 줄 뜻 | 오늘 코드에서 나타나는 모양 |
|:---|:---|:---|
| **분해**(decomposition) | 큰 문제를 작은 문제로 나눈다 | 재귀 — “n 개 문제는 n−1 개 문제 + 한 걸음” |
| **패턴 인식**(pattern recognition) | 작은 경우들에서 규칙을 찾는다 | 점화식 — “f(n) = f(n−1) + f(n−2)” |
| **추상화**(abstraction) | 중요하지 않은 것을 지운다 | 그래프 — 땅과 다리를 점과 선으로 |
| **알고리듬**(algorithm) | 단계의 순서로 적는다 | 함수 — 입력을 받아 출력을 돌려주는 절차 |

지금까지의 실습은 대부분 “무엇을 할지 알고 있고, 그것을 Python 으로 **옮기는**” 일이었습니다. 오늘의 다섯 문제는 다릅니다. **무엇을 할지가 보이지 않습니다.** 하노이 탑을 처음 보면 어디서 시작해야 할지 모릅니다. 그 ‘모르는 상태’에서 ‘아는 상태’로 가는 길이 오늘의 내용입니다.

## 1-2. 재귀 — 함수가 자기 자신을 부른다

7주차 2-6에서 함수가 다른 함수를 부르면 **호출 스택**에 돌아갈 곳이 쌓인다고 했습니다. 그때 “10주차에는 함수가 **자기 자신**을 부른다”고 예고했습니다. 그것이 **재귀(recursion)** 입니다.

**예상해 보기** — 아래 셀은 무엇을 출력할까요? 출력 순서에 주의하세요.
''')

code('''
def countdown(n):
    if n == 0:                  # 멈추는 경우
        print("발사!")
        return
    print(n)
    countdown(n - 1)            # 자기 자신을 — 더 작은 값으로 — 부릅니다

countdown(3)
''')

md('''
`countdown(3)` 은 3을 출력하고 `countdown(2)` 를 부릅니다. `countdown(2)` 는 2를 출력하고 `countdown(1)` 을, … `countdown(0)` 은 “발사!”를 출력하고 **돌아갑니다.** 그러면 기다리던 `countdown(1)` 이 끝나고, `countdown(2)` 가 끝나고, `countdown(3)` 이 끝납니다.

7주차의 호출 스택 그림이 네 층으로 쌓였다가 위에서부터 걷힙니다.

```
 ┌──────────────┐
 │ countdown(0) │  ← "발사!" 출력 후 return — 가장 나중에 쌓이고 가장 먼저 걷힘
 ├──────────────┤
 │ countdown(1) │
 ├──────────────┤
 │ countdown(2) │
 ├──────────────┤
 │ countdown(3) │  ← 맨 처음 호출. 가장 나중에 끝남
 └──────────────┘
```

이번에는 **돌아온 뒤에** 일을 하는 재귀입니다. 결과를 돌려받아 **쌓아 올립니다.**
''')

code('''
def factorial(n):
    """n! = n × (n-1) × … × 1"""
    if n <= 1:                         # 멈추는 경우: 1! = 1
        return 1
    return n * factorial(n - 1)        # n! = n × (n-1)!  — 작은 문제의 답에 한 단계를 더합니다

print(factorial(5))
print(factorial(20))
''')

md('''
`factorial(5)` 는 “5 × `factorial(4)`”인데 `factorial(4)` 의 값을 아직 모릅니다. 그래서 **기다리며** `factorial(4)` 를 부릅니다. `factorial(4)` 도 `factorial(3)` 을 기다리고 … `factorial(1)` 이 1을 돌려주면 그제야 2 × 1, 3 × 2, 4 × 6, 5 × 24 가 **차례로 계산되며 돌아옵니다.**

수학에서 $n! = n \\times (n-1)!$ 이라고 정의하는 것과 정확히 같은 모양입니다. **정의가 곧 코드**입니다. 이것이 재귀의 매력입니다.

## 1-3. 재귀의 두 조건 — 멈추는 경우, 작아지는 문제

재귀 함수에는 반드시 두 부분이 있어야 합니다.

| 조건 | 뜻 | `factorial` 에서 |
|:---|:---|:---|
| **멈추는 경우**(base case) | 더 쪼개지 않고 **바로 답하는** 경우 | `if n <= 1: return 1` |
| **작아지는 문제**(recursive case) | 자기 자신을 **더 작은 입력**으로 부르고, 그 답에 한 단계를 더한다 | `n * factorial(n - 1)` |

둘 중 하나라도 빠지면 어떻게 될까요?
''')

md(boom("멈추는 경우가 없으면?"))

code('''
def forever(n):
    return forever(n - 1)       # 멈추는 경우가 없습니다 — n 이 음수가 되어도 계속 부릅니다

forever(10)
''', raises=True)

md('''
`RecursionError: maximum recursion depth exceeded` — “재귀가 너무 깊어졌다”는 안내입니다. 호출 스택이 **끝없이 쌓이다** Python 이 정해 둔 한계(약 1,000층)에서 멈춘 것입니다. 6주차의 무한 반복과 같은 실수입니다. 무한 반복은 영원히 돌지만, 무한 재귀는 메모리가 쌓이므로 Python 이 먼저 끊어 줍니다.

재귀 함수를 쓸 때는 두 가지를 **먼저** 적으세요. ① 가장 작은 입력에서 답은 무엇인가? ② 호출할 때마다 입력이 **정말 작아지는가?** 둘이 확인되면 재귀는 반드시 끝납니다.
''')

md(key("재귀 정리", "① 재귀는 함수가 <b>같은 모양의 더 작은 문제</b>를 자기 자신에게 맡기는 것입니다.<br>② <b>멈추는 경우</b>와 <b>작아지는 문제</b> — 둘 다 있어야 합니다. 없으면 `RecursionError`.<br>③ 호출은 호출 스택에 쌓였다가 가장 나중 것부터 돌아옵니다. 7주차 2-6의 그림 그대로입니다.<br>④ 수학의 재귀적 정의($n! = n \\times (n-1)!$)는 코드로 거의 그대로 옮겨집니다."))

# ── 문제 1 ──
md("## 1-4. " + problem(1, "하노이 탑 (Tower of Hanoi)", "기둥 세 개 A · B · C 가 있고, A 에 크기가 다른 원판 n 개가 <b>큰 것이 아래</b>에 오도록 쌓여 있습니다. 모든 원판을 C 로 옮기세요. 규칙은 둘뿐입니다. ① 한 번에 원판 <b>하나</b>만 옮깁니다. ② <b>작은 원판 위에 큰 원판</b>을 올릴 수 없습니다. 원판이 64개일 때 몇 번 옮겨야 할까요?") + '''

1883년 프랑스 수학자 뤼카(Lucas)가 낸 퍼즐입니다. 원판 3개는 손으로 해 볼 만합니다. 7번이면 됩니다. 4개는 15번. 그런데 **방법을 말로 설명**하려면 막힙니다. “먼저 작은 걸 C 로, 그다음 중간 걸 B 로, 다시 작은 걸 B 로 …” 원판이 10개면 이 설명은 1,023 줄이 됩니다.

''' + think("분해 — 가장 큰 원판 하나만 생각한다", "원판 n 개를 A 에서 C 로 옮기는 일을 보지 말고, <b>맨 아래 가장 큰 원판 하나</b>만 봅니다. 이 원판이 C 로 가려면, 그 위에 있던 n−1 개가 <b>모두 B 에</b> 비켜 있어야 합니다. 그러면 일은 세 단계가 됩니다.<br>① 위의 n−1 개를 A 에서 B 로 옮긴다 (C 를 경유)<br>② 가장 큰 원판 하나를 A 에서 C 로 옮긴다<br>③ B 에 있던 n−1 개를 C 로 옮긴다 (A 를 경유)<br>①과 ③은 <b>원판 n−1 개를 옮기는 같은 문제</b>입니다. 기둥 이름만 다릅니다. “n−1 개를 어떻게 옮기는가”는 묻지 않습니다. 그것은 <b>같은 함수가 알아서</b> 합니다. 원판이 1개이면 그냥 옮깁니다 — 멈추는 경우.") + '''

세 단계를 코드로 옮기면 끝입니다. 함수 이름은 `hanoi(n, start, end, via)` — 원판 `n` 개를 `start` 에서 `end` 로, `via` 를 경유해 옮깁니다.
''')

code('''
def hanoi(n, start, end, via):
    """원판 n 개를 start 기둥에서 end 기둥으로 옮긴다. via 는 경유 기둥."""
    if n == 1:                               # 멈추는 경우: 원판 하나는 그냥 옮긴다
        print(f"원판 1 을 {start} → {end}")
        return
    hanoi(n - 1, start, via, end)            # ① 위의 n-1 개를 경유 기둥으로 비켜 둔다
    print(f"원판 {n} 을 {start} → {end}")    # ② 가장 큰 원판을 목적지로
    hanoi(n - 1, via, end, start)            # ③ 비켜 둔 n-1 개를 목적지로

hanoi(3, "A", "C", "B")
''')

md('''
출력된 7줄을 종이에 그려 가며 따라가 보세요. 규칙을 한 번도 어기지 않습니다. 코드 어디에도 “작은 원판 위에 큰 원판을 올리지 말라”는 검사가 **없는데도** 그렇습니다. 분해가 옳으면 규칙은 저절로 지켜집니다.

`n = 4` 로 바꾸면 15줄이 나옵니다. **코드는 한 글자도 바뀌지 않습니다.** 1,023 줄짜리 설명을 쓰지 않아도 되는 이유입니다.

### 몇 번 옮기나 — 패턴 인식

이동 횟수만 세는 함수로 바꿔 봅니다. 출력 대신 **횟수를 돌려줍니다.**
''')

code('''
def hanoi_count(n):
    if n == 1:
        return 1
    return hanoi_count(n - 1) + 1 + hanoi_count(n - 1)     # ① + ② + ③

for n in range(1, 11):
    print(n, hanoi_count(n))
''')

md('''
1, 3, 7, 15, 31, 63, … 보이나요? **다음 수 = 앞의 수 × 2 + 1**, 즉 $2^n - 1$ 입니다. 작은 경우를 나열해 규칙을 찾는 것이 **패턴 인식**입니다. 규칙을 찾으면 재귀 없이 바로 계산할 수 있습니다.
''')

code('''
moves = 2 ** 64 - 1
print(f"원판 64개: {moves:,} 번")
seconds = moves                           # 1초에 한 번 옮긴다면
years = seconds / (60 * 60 * 24 * 365)
print(f"1초에 한 번씩 옮기면 약 {years:,.0f} 년")
''')

md(note("전설", "인도 베나레스의 사원에서 승려들이 황금 원판 64개를 옮기고 있으며, 다 옮기면 세상이 끝난다는 이야기가 퍼즐과 함께 전해집니다. 위 계산대로라면 약 5,850억 년이 걸리니 걱정하지 않아도 됩니다. 우주의 나이(약 138억 년)의 40배가 넘습니다. 이것이 <b>지수적 증가</b>($2^n$)의 크기입니다. 2교시에서 이 크기가 우리 코드 안에서 생기는 것을 보게 됩니다."))

md('''
## 1-5. 재귀와 반복 — 무엇을 쓸까

`factorial` 은 6주차의 `for` 문으로도 쓸 수 있습니다. 둘 다 맞습니다.
''')

code('''
def factorial_loop(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

print(factorial(10), factorial_loop(10))
''')

md('''
그러면 `hanoi` 를 `for` 문으로 쓸 수 있을까요? 쓸 수는 있지만 **훨씬 어렵습니다.** 하노이 탑의 분해는 “n−1 개 문제 **두 번** + 한 걸음”이라 **가지를 칩니다.** 반복문은 한 줄로 쭉 가는 문제에 맞고, 가지를 치는 문제는 재귀가 자연스럽습니다.

| | 반복문 | 재귀 |
|:---|:---|:---|
| 어울리는 문제 | 한 줄로 쭉 가는 일 — 합계, 최댓값, 목록 훑기 | 가지를 치는 일 — 하노이 탑, 폴더 안의 폴더, 나무 모양 자료 |
| 생각의 방향 | “처음부터 끝까지 하나씩” | “가장 큰 한 조각만 생각하고 나머지는 자기 자신에게” |
| 비용 | 메모리가 거의 들지 않는다 | 호출마다 스택에 쌓인다. 너무 깊으면 `RecursionError` |
| 함정 | 무한 반복 | 멈추는 경우 누락 · 같은 계산 반복(2교시) |

선택 기준은 하나입니다. **문제의 정의가 재귀적이면 재귀, 아니면 반복.** 하노이 탑은 정의 자체가 “n−1 개 문제”를 품고 있으니 재귀입니다.
''')

md(key("1-4 ~ 1-5 정리", "① 하노이 탑의 열쇠는 <b>가장 큰 원판 하나만 보는 것</b>입니다. 나머지 n−1 개는 같은 문제이므로 함수 자신에게 맡깁니다.<br>② 분해가 옳으면 규칙 검사 없이도 규칙이 지켜집니다. 코드는 짧고, n 이 커져도 바뀌지 않습니다.<br>③ 작은 경우를 나열해 규칙($2^n - 1$)을 찾는 것이 패턴 인식입니다.<br>④ 가지를 치는 문제는 재귀, 한 줄로 가는 문제는 반복."))

# ── 1교시 실습 ──
practice("✏️ 실습 1-1", "자릿수의 합 — 재귀로", "약 4분",
         "정수 `n`(0 이상)의 각 자릿수를 더한 값을 돌려주는 `sum_digits(n)` 을 <b>재귀로</b> 쓰세요. `for` 문과 문자열 변환은 쓰지 않습니다.<br>힌트: `1234` 의 자릿수 합 = `4` + (`123` 의 자릿수 합). 마지막 자리는 `n % 10`, 나머지는 `n // 10`. 멈추는 경우는 `n < 10`.<br>`sum_digits(1234)` → `10`, `sum_digits(0)` → `0`",
         '''
# 여기에 함수를 정의하세요


print(sum_digits(1234))
print(sum_digits(2 ** 50))
''',
         "sum_digits(1234) == 10 and sum_digits(0) == 0 and sum_digits(9) == 9 and sum_digits(1000000) == 1 and sum_digits(2 ** 50) == 76",
         '''
def sum_digits(n):
    if n < 10:                              # 멈추는 경우: 한 자리면 그 수 자체
        return n
    return n % 10 + sum_digits(n // 10)     # 마지막 자리 + (나머지 자리들의 합)

print(sum_digits(1234))        # 10
print(sum_digits(2 ** 50))     # 76
''', raises=True, heading="## 1교시 실습")

practice("✏️ 실습 1-2", "거듭제곱 — 재귀로", "약 5분",
         "`power(x, n)` — `x` 의 `n` 제곱(`n` 은 0 이상 정수)을 <b>재귀로</b> 돌려주세요. `**` 연산자는 쓰지 않습니다.<br>힌트: $x^n = x \\times x^{n-1}$, 멈추는 경우 $x^0 = 1$.<br><b>도전</b>: $x^{10} = (x^5)^2$ 처럼 `n` 이 짝수이면 절반만 계산해 제곱하면 호출 횟수가 크게 줄어듭니다. `n` 이 홀수이면 $x \\times x^{n-1}$. 두 방식 모두 점검을 통과합니다.",
         '''
# 여기에 함수를 정의하세요


print(power(2, 10))
print(power(1.5, 3))
''',
         "power(2, 10) == 1024 and power(3, 0) == 1 and abs(power(1.5, 3) - 3.375) < 1e-9 and power(2, 100) == 2 ** 100 and power(7, 1) == 7",
         '''
def power(x, n):
    if n == 0:
        return 1
    return x * power(x, n - 1)

# 도전 — 절반으로 쪼개기 (호출 횟수가 n 번에서 약 log n 번으로)
def power_fast(x, n):
    if n == 0:
        return 1
    if n % 2 == 0:
        half = power_fast(x, n // 2)
        return half * half
    return x * power_fast(x, n - 1)

print(power(2, 10))        # 1024
print(power(1.5, 3))       # 3.375
''', raises=True)

practice("✏️ 실습 1-3", "하노이 탑 — 이동 목록 돌려주기", "약 6분",
         "1-4의 `hanoi` 는 `print` 를 했습니다. 이번에는 이동을 <b>리스트로 모아 돌려주는</b> `hanoi_moves(n, start, end, via)` 를 쓰세요. 각 이동은 `(출발, 도착)` 튜플입니다.<br>힌트: 멈추는 경우는 `[(start, end)]` 하나짜리 리스트. 작아지는 경우는 ① 의 리스트 + `[(start, end)]` + ③ 의 리스트 — 리스트 덧셈(5주차)으로 이어 붙입니다.<br>`hanoi_moves(2, \"A\", \"C\", \"B\")` → `[(\"A\", \"B\"), (\"A\", \"C\"), (\"B\", \"C\")]`",
         '''
# 여기에 함수를 정의하세요


moves = hanoi_moves(3, "A", "C", "B")
print(len(moves), "번")
print(moves)
''',
         'hanoi_moves(1, "A", "C", "B") == [("A", "C")] and hanoi_moves(2, "A", "C", "B") == [("A", "B"), ("A", "C"), ("B", "C")] and len(hanoi_moves(3, "A", "C", "B")) == 7 and hanoi_moves(3, "A", "C", "B")[3] == ("A", "C") and len(hanoi_moves(10, "A", "C", "B")) == 1023',
         '''
def hanoi_moves(n, start, end, via):
    if n == 1:
        return [(start, end)]
    return (hanoi_moves(n - 1, start, via, end)      # ① 위의 n-1 개를 경유 기둥으로
            + [(start, end)]                         # ② 가장 큰 원판
            + hanoi_moves(n - 1, via, end, start))   # ③ 비켜 둔 n-1 개를 목적지로

moves = hanoi_moves(3, "A", "C", "B")
print(len(moves), "번")                 # 7 번
print(moves)
''', raises=True)

md(key("1교시 정리", "① 재귀 = 같은 모양의 더 작은 문제를 자기 자신에게 맡기기. <b>멈추는 경우</b>와 <b>작아지는 문제</b>가 필요합니다.<br>② 하노이 탑은 ‘가장 큰 원판 하나’만 보면 세 줄로 풀립니다. 이것이 <b>분해</b>입니다.<br>③ 작은 경우를 나열해 $2^n - 1$ 을 찾는 것이 <b>패턴 인식</b>입니다. 64개면 우주 나이의 40배.<br>④ 가지를 치는 문제는 재귀, 한 줄로 가는 문제는 반복.") + "\n\n" + BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · 동적 프로그래밍 — 작은 답을 기억해 큰 답을 만들다\n\n" + period(2, "계단 오르기와 거스름돈", [
    "작은 경우를 나열해 점화식을 찾는다",
    "같은 계산을 되풀이하는 재귀가 왜 느려지는지 호출 횟수로 확인한다",
    "메모이제이션(기억하기)과 표 채우기(동적 프로그래밍)로 고친다",
    "탐욕법이 틀리는 반례를 찾고, 동적 프로그래밍으로 올바른 답을 구한다",
]))

md("## 2-1. " + problem(2, "계단 오르기", "계단이 n 칸 있습니다. 한 번에 <b>1칸 또는 2칸</b>씩 오를 수 있습니다. 꼭대기까지 오르는 <b>서로 다른 방법</b>은 몇 가지일까요? 예를 들어 3칸이면 (1,1,1), (1,2), (2,1) 세 가지입니다. 50칸이면?") + '''

손으로 50칸을 세는 것은 불가능합니다. 하노이 탑처럼 **작은 경우부터** 나열합니다.

| 칸 수 n | 방법 | 가짓수 |
|:---:|:---|:---:|
| 1 | (1) | 1 |
| 2 | (1,1), (2) | 2 |
| 3 | (1,1,1), (1,2), (2,1) | 3 |
| 4 | (1,1,1,1), (1,1,2), (1,2,1), (2,1,1), (2,2) | 5 |
| 5 | … | 8 |

1, 2, 3, 5, 8 … **앞의 두 수를 더하면 다음 수**입니다. 왜 그럴까요?

''' + think("분해 — 마지막 한 걸음만 생각한다", "n 칸 꼭대기에 도착하는 <b>마지막 걸음</b>은 둘 중 하나입니다. 1칸을 올라 도착했거나, 2칸을 올라 도착했거나.<br>· 마지막이 1칸이면, 그 전에 <b>n−1 칸</b> 꼭대기에 있었습니다. 거기까지 가는 방법의 수 = f(n−1)<br>· 마지막이 2칸이면, 그 전에 <b>n−2 칸</b> 꼭대기에 있었습니다. 거기까지 가는 방법의 수 = f(n−2)<br>두 경우는 겹치지 않으므로 <b>f(n) = f(n−1) + f(n−2)</b>. 멈추는 경우는 f(1) = 1, f(2) = 2.<br>하노이 탑과 같은 틀입니다. “전체”를 보지 않고 <b>마지막 한 조각</b>만 보고, 나머지는 같은 문제에 맡깁니다. 이렇게 f(n) 을 더 작은 f 로 나타낸 식을 <b>점화식</b>(recurrence relation)이라고 합니다.") + '''

점화식이 나왔으니 1교시처럼 재귀로 옮깁니다.
''')

code('''
def climb(n):
    if n <= 2:                               # 멈추는 경우: f(1) = 1, f(2) = 2
        return n
    return climb(n - 1) + climb(n - 2)       # 점화식 그대로

for n in range(1, 11):
    print(n, climb(n), end="  |  ")
''')

md(note("피보나치 수열", "1, 1, 2, 3, 5, 8, 13, … 앞의 두 수를 더해 가는 이 수열은 1202년 피보나치(Fibonacci)가 토끼의 번식을 설명하며 소개했습니다. 계단 오르기의 답은 피보나치 수열을 한 칸 민 것입니다. 해바라기 씨의 배열, 나선 조개 껍데기, 주가 분석 도구에도 나타납니다. 오늘은 수열 자체보다 <b>이 점화식을 계산하는 방법</b>이 주제입니다."))

md('''
## 2-2. 재귀가 느려지는 이유 — 같은 계산을 또 하고 또 한다

`climb(50)` 을 구해 봅시다. 그 전에 작은 값으로 **시간**을 재 봅니다. 7주차에서 쓴 `time` 모듈입니다.

**예상해 보기** — `climb(25)` 와 `climb(30)` 의 시간은 몇 배 차이 날까요? 입력은 1.2배인데.
''')

code('''
import time

for n in [20, 25, 30]:
    start = time.time()
    result = climb(n)
    elapsed = time.time() - start
    print(f"climb({n}) = {result:>8}   {elapsed:.3f} 초")
''')

md('''
입력이 5 늘 때마다 시간이 **약 11배** 늘어납니다. `climb(50)` 은 이 비율로 하면 **몇 시간**, `climb(100)` 은 우주의 나이보다 깁니다. 하노이 탑의 $2^n$ 이 우리 코드 안에서 일어나고 있습니다.

왜일까요? `climb(5)` 가 무엇을 부르는지 그려 봅니다.

```
climb(5)
├─ climb(4)
│  ├─ climb(3)
│  │  ├─ climb(2)
│  │  └─ climb(1)
│  └─ climb(2)
└─ climb(3)              ← climb(3) 을 또 계산합니다. 위에서 이미 했는데.
   ├─ climb(2)
   └─ climb(1)
```

`climb(3)` 이 두 번, `climb(2)` 가 세 번 계산됩니다. `climb(30)` 에서는 `climb(10)` 이 **수천 번** 계산됩니다. 매번 같은 답이 나오는데도요. 호출 횟수를 직접 세어 봅니다.
''')

code('''
calls = 0

def climb_counted(n):
    global calls                             # 호출 횟수만 세는 용도 — 7주차에서 피하라고 한 global 을 여기서만 씁니다
    calls += 1
    if n <= 2:
        return n
    return climb_counted(n - 1) + climb_counted(n - 2)

for n in [10, 20, 25]:
    calls = 0
    climb_counted(n)
    print(f"climb({n}): 함수 호출 {calls:,} 번")
''')

md('''
`climb(25)` 의 답은 121,393 인데 함수는 **15만 번** 불립니다. 서로 다른 입력은 25개뿐입니다. 나머지는 **전부 중복**입니다.

문제의 원인이 보이니 해결책도 보입니다. **한 번 구한 답을 적어 두고, 다시 물으면 적어 둔 것을 돌려준다.**

## 2-3. 메모이제이션 — 한 번 구한 답은 적어 둔다

5주차의 **딕셔너리**가 ‘메모장’이 됩니다. 함수 첫머리에서 메모장을 보고, 있으면 바로 돌려주고, 없으면 계산한 뒤 **적어 두고** 돌려줍니다. 이것을 **메모이제이션(memoization)** 이라고 합니다. ‘memo(메모)’에서 온 말입니다.
''')

code('''
memo = {}                                    # {n: climb(n)} — 구한 답을 적어 두는 메모장

def climb_memo(n):
    if n in memo:                            # 이미 구한 적이 있으면
        return memo[n]                       #   적어 둔 답을 바로 돌려준다
    if n <= 2:
        return n
    result = climb_memo(n - 1) + climb_memo(n - 2)
    memo[n] = result                         # 구한 답을 적어 둔다
    return result

start = time.time()
print(climb_memo(50))
print(climb_memo(90))
print(f"{time.time() - start:.4f} 초")
print(len(memo), "개를 적어 두었습니다")
''')

md('''
몇 시간이 **0.001초**가 되었습니다. 점화식도, 재귀도 그대로입니다. 달라진 것은 딕셔너리 세 줄뿐입니다. `climb(90)` 을 구하는 데 메모장에 적힌 항목은 88개 — 서로 다른 입력의 수만큼만 계산했습니다.

<details><summary><b>📎 더 알아보기 — <code>functools.lru_cache</code>: 메모이제이션을 한 줄로</b></summary>

Python 표준 라이브러리에 이 일을 대신해 주는 도구가 있습니다. 함수 정의 위에 한 줄을 얹으면(이런 것을 데코레이터라고 합니다. 11주차) 인자별로 결과를 자동으로 기억합니다.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def climb(n):
    if n <= 2:
        return n
    return climb(n - 1) + climb(n - 2)

climb(90)      # 빠릅니다. memo 딕셔너리를 직접 쓰지 않아도 됩니다
```

원리를 아는 것이 먼저이고, 그다음에 도구를 씁니다.

</details>

## 2-4. 거꾸로 가기 — 표를 아래에서부터 채운다 (동적 프로그래밍)

메모이제이션은 **큰 문제에서 출발해** 필요한 작은 답을 구하며 내려갑니다(하향식). 반대로 **작은 답부터 차례로** 표에 채워 올라갈 수도 있습니다(상향식). f(1), f(2) 를 알면 f(3) 이 나오고, f(3) 을 알면 f(4) 가 나옵니다. 재귀가 필요 없습니다. 6주차의 `for` 문과 리스트면 됩니다.
''')

code('''
def climb_table(n):
    table = [0] * (n + 1)                    # table[i] = i 칸을 오르는 방법의 수
    table[1] = 1
    if n >= 2:
        table[2] = 2
    for i in range(3, n + 1):
        table[i] = table[i - 1] + table[i - 2]    # 점화식 — 이미 채운 두 칸을 읽어 다음 칸을 채운다
    return table[n]

print(climb_table(50))
print(climb_table(90))
''')

md('''
표를 채우는 이 방식을 **동적 프로그래밍(dynamic programming, DP)** 이라고 합니다. 이름은 1950년대에 벨먼(Bellman)이 붙였는데, ‘동적’이라는 말에 특별한 뜻은 없습니다. 당시 상사가 수학 연구를 싫어해 그럴듯한 이름을 지었다고 벨먼 자신이 회고했습니다. 뜻은 간단합니다. **작은 문제의 답을 표에 적어 두고, 그것으로 큰 문제의 답을 만든다.**

동적 프로그래밍이 통하는 문제는 두 가지 성질이 있습니다.

| 성질 | 뜻 | 계단 오르기에서 |
|:---|:---|:---|
| **겹치는 부분 문제** | 같은 작은 문제가 여러 번 나온다 | `climb(3)` 이 `climb(4)` 와 `climb(5)` 양쪽에서 필요 |
| **최적 부분 구조** | 큰 문제의 답이 작은 문제의 답으로 만들어진다 | f(n) = f(n−1) + f(n−2) |

하노이 탑은 두 번째는 있지만 첫 번째가 없습니다. `hanoi(n-1, A, B)` 와 `hanoi(n-1, B, C)` 는 기둥이 달라 **다른 문제**라 적어 둘 것이 없습니다. 그래서 하노이 탑은 $2^n - 1$ 번보다 빨라질 수 없고, 계단 오르기는 n 번이면 됩니다. **같은 재귀라도 겹치는 부분이 있는지**가 운명을 가릅니다.
''')

md(key("세 가지 풀이 비교", "<table style='border-collapse:collapse;'><tr><th style='text-align:left;padding:2px 10px;'>방법</th><th style='text-align:left;padding:2px 10px;'>생각의 방향</th><th style='text-align:left;padding:2px 10px;'>climb(30) 의 일</th><th style='text-align:left;padding:2px 10px;'>장단점</th></tr><tr><td style='padding:2px 10px;'>단순 재귀</td><td style='padding:2px 10px;'>점화식 그대로</td><td style='padding:2px 10px;'>약 270만 번 호출</td><td style='padding:2px 10px;'>가장 읽기 쉬움 · 지수적으로 느림</td></tr><tr><td style='padding:2px 10px;'>메모이제이션</td><td style='padding:2px 10px;'>위에서 아래로, 적어 두며</td><td style='padding:2px 10px;'>약 60 번 호출</td><td style='padding:2px 10px;'>재귀 코드에 세 줄만 추가 · 깊은 재귀는 스택 한계</td></tr><tr><td style='padding:2px 10px;'>표 채우기(DP)</td><td style='padding:2px 10px;'>아래에서 위로</td><td style='padding:2px 10px;'>반복 28 번</td><td style='padding:2px 10px;'>재귀 없음 · 가장 빠름 · 채우는 순서를 정해야 함</td></tr></table>셋 다 <b>같은 점화식</b>에서 나옵니다. 점화식을 찾는 것이 일의 90% 입니다."))

# ── 문제 3 ──
md("## 2-5. " + problem(3, "거스름돈 — 가장 적은 동전으로", "동전의 종류가 주어졌을 때, 금액을 거슬러 주는 데 필요한 <b>가장 적은 동전 개수</b>는? 예: 동전이 500 · 100 · 50 · 10원일 때 1,260원 → 500 + 500 + 100 + 100 + 50 + 10 = 6개.") + '''

누구나 아는 방법이 있습니다. **큰 동전부터 되는 만큼** 씁니다. 500원을 2개 쓰고, 남은 260원에 100원을 2개, 50원 1개, 10원 1개. 이렇게 매 순간 가장 좋아 보이는 선택을 하는 것을 **탐욕법(greedy algorithm)** 이라고 합니다.
''')

code('''
def change_greedy(coins, amount):
    """큰 동전부터 되는 만큼 쓴다. coins 는 큰 것부터 정렬되어 있어야 한다."""
    count = 0
    for coin in coins:
        count += amount // coin              # 이 동전을 몇 개 쓸 수 있나
        amount = amount % coin               # 남은 금액
    return count

print(change_greedy([500, 100, 50, 10], 1260))
''')

md('''
6개, 맞습니다. 한국 동전으로는 탐욕법이 **항상** 최적입니다. 그러면 탐욕법이 거스름돈 문제의 답일까요?

**예상해 보기** — 동전이 1 · 3 · 4원이고 6원을 거슬러 줍니다. 탐욕법은 몇 개를 쓸까요? 가장 적은 개수는 몇 개일까요?
''')

code('''
print(change_greedy([4, 3, 1], 6))
''')

md('''
탐욕법은 4 + 1 + 1 = **3개**입니다. 그런데 3 + 3 = **2개**면 됩니다. 탐욕법이 **틀렸습니다.** 4원을 집는 순간이 가장 좋아 보였지만, 그 선택이 뒤를 망쳤습니다.

이것이 오늘 두 번째로 중요한 교훈입니다. **쉬워 보이는 방법이 맞는지는 반례를 찾아 확인해야 합니다.** 반례 하나면 방법 전체가 무너집니다. 한국 동전에서 통했다고 모든 동전에서 통하는 것이 아닙니다.

''' + think("분해 — 마지막에 쓴 동전 하나만 생각한다", "계단 오르기의 ‘마지막 한 걸음’과 똑같습니다. 금액 m 을 만드는 <b>마지막 동전</b>은 1원 · 3원 · 4원 중 하나입니다.<br>· 마지막이 1원이면, 그 전에 <b>m−1 원</b>을 만들어 두었어야 합니다. 그 최소 개수 = f(m−1)<br>· 마지막이 3원이면 f(m−3), 4원이면 f(m−4)<br>셋 중 <b>가장 작은 것 + 1</b>이 f(m) 입니다. 멈추는 경우는 f(0) = 0 (0원은 동전 0개).<br><b>f(m) = min(f(m−1), f(m−3), f(m−4)) + 1</b>. 같은 f(m−3) 이 여러 곳에서 필요하니(겹치는 부분 문제) 표로 채웁니다.") + '''

0원부터 차례로 표를 채웁니다. 만들 수 없는 금액(예: 동전이 2원뿐일 때 3원)은 ‘무한대’로 두어 선택되지 않게 합니다.
''')

code('''
def min_coins(coins, amount):
    INF = float("inf")                       # 무한대 — '만들 수 없음' 표시
    table = [INF] * (amount + 1)             # table[m] = m 원을 만드는 최소 동전 수
    table[0] = 0                             # 0 원은 동전 0 개
    for m in range(1, amount + 1):
        for coin in coins:                   # 마지막 동전이 coin 이라면
            if coin <= m and table[m - coin] + 1 < table[m]:
                table[m] = table[m - coin] + 1
    return table[amount] if table[amount] != INF else -1     # 만들 수 없으면 -1

print(min_coins([1, 3, 4], 6))               # 2  (3 + 3)
print(min_coins([500, 100, 50, 10], 1260))   # 6
print(min_coins([2], 3))                     # -1
''')

md('''
표 `table` 을 직접 출력해 보면 `[0, 1, 2, 1, 1, 2, 2]` — 0원 0개, 1원 1개, 2원 2개, 3원 1개, 4원 1개, 5원 2개(1+4), 6원 2개(3+3). **모든 금액**의 답이 한꺼번에 나옵니다. 그 금액 하나만 묻는 탐욕법과 다른 점입니다.

`min_coins` 는 `change_greedy` 보다 느립니다. 금액 × 동전 종류만큼 일합니다. 그러나 **항상 맞습니다.** “빠르지만 가끔 틀리는 방법”과 “조금 느리지만 항상 맞는 방법” 중 무엇을 쓸지는 문제에 따라 정합니다. 그리고 그 판단은 반례를 찾아본 사람만 할 수 있습니다.
''')

md(key("2-5 정리 — 탐욕법과 동적 프로그래밍", "① <b>탐욕법</b>: 매 순간 가장 좋아 보이는 것을 고른다. 빠르고 단순하지만, 맞는지는 <b>증명하거나 반례를 찾아야</b> 안다.<br>② 거스름돈은 동전 종류에 따라 탐욕법이 틀린다. 반례: 동전 1 · 3 · 4 로 6원.<br>③ <b>동적 프로그래밍</b>: 마지막 한 조각만 생각해 점화식을 세우고, 0부터 표를 채운다. 느리지만 항상 맞다.<br>④ 계단 오르기(경우의 수)와 거스름돈(최솟값)은 다른 문제이지만 <b>생각의 틀은 하나</b>입니다. 이 틀을 익히는 것이 오늘의 목표입니다."))

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "계단 오르기 — 한 번에 1 · 2 · 3칸", "약 5분",
         "한 번에 1칸, 2칸, <b>3칸</b>까지 오를 수 있을 때 `n` 칸을 오르는 방법의 수 `climb3(n)` 을 <b>표 채우기</b>로 쓰세요.<br>먼저 점화식을 세웁니다. 마지막 걸음이 1 · 2 · 3칸 중 하나이므로 f(n) = f(n−1) + f(n−2) + f(n−3). 멈추는 경우 f(1) = 1, f(2) = 2, f(3) = 4 (또는 f(0) = 1 로 두고 세 칸을 모두 식으로 구해도 됩니다).<br>`climb3(4)` → `7`, `climb3(10)` → `274`",
         '''
# 여기에 함수를 정의하세요


for n in [1, 2, 3, 4, 5, 10, 30]:
    print(n, climb3(n))
''',
         "[climb3(n) for n in [1, 2, 3, 4, 5, 10]] == [1, 2, 4, 7, 13, 274] and climb3(30) == 53798080",
         '''
def climb3(n):
    table = [0] * (n + 4)                    # 작은 n 에서도 인덱스가 넘치지 않게 넉넉히
    table[0] = 1                             # 0 칸: 아무것도 안 하는 방법 1 가지 — 식을 단순하게 해 줍니다
    for i in range(1, n + 1):
        table[i] = table[i - 1] + table[i - 2] + table[i - 3]     # 음수 인덱스는 뒤쪽의 0 을 읽으니 괜찮습니다
    return table[n]

for n in [1, 2, 3, 4, 5, 10, 30]:
    print(n, climb3(n))        # 1 2 4 7 13 274 53798080
''', raises=True, heading="## 2교시 실습")

practice("✏️ 실습 2-2", "격자 길 찾기 — 경로의 수", "약 6분",
         "`rows` × `cols` 격자의 왼쪽 위에서 오른쪽 아래까지, <b>오른쪽 또는 아래로만</b> 움직여 가는 경로의 수 `grid_paths(rows, cols)` 를 구하세요.<br>🧠 마지막 한 걸음을 생각합니다. 어떤 칸에 도착하는 마지막 걸음은 <b>위에서 내려왔거나 왼쪽에서 왔거나</b> 둘 중 하나입니다. 그러니 (그 칸까지의 경로 수) = (위 칸까지) + (왼쪽 칸까지). 첫 행과 첫 열은 한 방향으로만 올 수 있으니 1 입니다.<br>2차원 표는 6주차의 리스트의 리스트 `[[0] * cols for _ in range(rows)]` 로 만듭니다.<br>`grid_paths(2, 2)` → `2`, `grid_paths(3, 3)` → `6`, `grid_paths(3, 7)` → `28`",
         '''
# 여기에 함수를 정의하세요


print(grid_paths(3, 3))
print(grid_paths(10, 10))
''',
         "grid_paths(1, 1) == 1 and grid_paths(2, 2) == 2 and grid_paths(3, 3) == 6 and grid_paths(3, 7) == 28 and grid_paths(10, 10) == 48620 and grid_paths(1, 5) == 1",
         '''
def grid_paths(rows, cols):
    table = [[0] * cols for _ in range(rows)]      # table[r][c] = (r, c) 칸까지 가는 경로의 수
    for r in range(rows):
        for c in range(cols):
            if r == 0 or c == 0:
                table[r][c] = 1                    # 첫 행 · 첫 열: 한 길뿐
            else:
                table[r][c] = table[r - 1][c] + table[r][c - 1]     # 위에서 + 왼쪽에서
    return table[rows - 1][cols - 1]

print(grid_paths(3, 3))        # 6
print(grid_paths(10, 10))      # 48620
''', raises=True)

practice("✏️ 실습 2-3", "메모이제이션으로 격자 길 찾기 (도전)", "",
         "실습 2-2를 <b>재귀 + 메모이제이션</b>으로 다시 쓰세요: `grid_paths_memo(rows, cols)`. 안에 딕셔너리 `memo` 를 두고, 키는 `(rows, cols)` 튜플입니다. 점화식: g(r, c) = g(r−1, c) + g(r, c−1), 멈추는 경우 r == 1 또는 c == 1 이면 1.<br>메모 없이 `grid_paths_memo(16, 16)` 을 부르면 수십억 번 호출되어 끝나지 않습니다. 메모가 있으면 256번이면 됩니다. (시간이 남는 사람만)",
         '''
memo = {}

# 여기에 함수를 정의하세요


print(grid_paths_memo(3, 3))
print(grid_paths_memo(16, 16))
''',
         "grid_paths_memo(3, 3) == 6 and grid_paths_memo(3, 7) == 28 and grid_paths_memo(16, 16) == 155117520 and grid_paths_memo(1, 1) == 1",
         '''
memo = {}

def grid_paths_memo(rows, cols):
    if rows == 1 or cols == 1:
        return 1
    if (rows, cols) in memo:
        return memo[(rows, cols)]
    result = grid_paths_memo(rows - 1, cols) + grid_paths_memo(rows, cols - 1)
    memo[(rows, cols)] = result
    return result

print(grid_paths_memo(3, 3))        # 6
print(grid_paths_memo(16, 16))      # 155117520
''', raises=True)

md(key("2교시 정리", "① 작은 경우를 나열해 <b>점화식</b>을 찾습니다. 열쇠는 ‘마지막 한 조각만 생각하기’.<br>② 점화식을 그대로 재귀로 옮기면 맞지만, 겹치는 부분 문제 때문에 지수적으로 느려집니다. 호출 횟수를 세어 보면 보입니다.<br>③ <b>메모이제이션</b> — 딕셔너리에 적어 두기. <b>동적 프로그래밍</b> — 0부터 표 채우기. 둘 다 같은 점화식.<br>④ 탐욕법은 빠르지만 <b>반례</b>가 있을 수 있습니다. 거스름돈 1 · 3 · 4 로 6원. 동적 프로그래밍은 느리지만 항상 맞습니다.") + "\n\n" + BREAK)

# ═════════════════════════ 3교시 ═════════════════════════
md("# 3교시 · 그래프 모델링 — 문제를 점과 선으로 추상화하다\n\n" + period(3, "쾨니히스베르크의 다리와 미로 최단 경로", [
    "현실의 문제에서 중요하지 않은 것을 지워 점과 선(그래프)으로 바꾼다",
    "그래프를 딕셔너리로 표현하고, 차수를 세어 오일러의 정리로 답한다",
    "미로를 그래프로 보고, 큐를 이용한 너비 우선 탐색으로 최단 경로를 찾는다",
    "오늘 배운 네 가지 생각의 틀을 한 표로 정리한다",
]))

md("## 3-1. " + problem(4, "쾨니히스베르크의 일곱 다리", "18세기 프로이센의 도시 쾨니히스베르크(지금의 칼리닌그라드)는 강이 도시를 네 구역으로 나누고, 일곱 개의 다리가 구역들을 잇고 있었습니다. 시민들의 오랜 궁금증: <b>일곱 다리를 모두 정확히 한 번씩만 건너는 산책길</b>이 있을까? 출발점과 도착점은 달라도 됩니다.") + '''

```
            ┌─────────────────┐
            │     북쪽 땅 (N)    │
            └──┬─────┬─────┬──┘
               │     │     │          다리 7개:
   ┌───────────┴──┐  │  ┌──┴────────┐   N–W 2개, N–E 1개
   │  서쪽 섬 (W)   ├──┼──┤  동쪽 땅 (E) │   W–E 1개
   └───────────┬──┘  │  └──┬────────┘   S–W 2개, S–E 1개
               │     │     │
            ┌──┴─────┴─────┴──┐
            │     남쪽 땅 (S)    │
            └─────────────────┘
```

1736년 오일러(Euler)가 이 문제를 풀었습니다. 다리를 하나하나 건너 보는 대신, 문제를 **다시 그렸습니다.**

''' + think("추상화 — 중요하지 않은 것을 지운다", "산책에서 중요한 것은 무엇일까요? 땅의 <b>모양</b>은 상관없습니다. 다리의 <b>길이</b>도, 강의 <b>폭</b>도 상관없습니다. 중요한 것은 두 가지뿐입니다. <b>어떤 땅들이 있고, 어떤 다리가 어느 땅을 잇는가.</b><br>그래서 땅을 <b>점</b>으로, 다리를 <b>선</b>으로 바꿉니다. 지도가 아니라 점 4개와 선 7개짜리 그림이 됩니다. 이것이 <b>그래프</b>(graph)입니다 — 통계 그래프가 아니라 ‘점과 선의 구조’라는 뜻의 수학 용어입니다. 점은 <b>정점</b>(vertex), 선은 <b>변</b>(edge)이라고 부릅니다.<br>오일러는 그다음 질문을 바꾸었습니다. “어떤 순서로 건너야 하나?”가 아니라 “<b>각 땅에 다리가 몇 개씩 붙어 있나?</b>”") + '''

Python 에서 그래프는 5주차의 **딕셔너리**로 표현합니다. 키는 정점, 값은 그 정점에서 선으로 이어진 정점들의 리스트입니다. 다리가 두 개면 이름이 두 번 들어갑니다.
''')

code('''
# 쾨니히스베르크: 땅 4 곳, 다리 7 개. 각 다리는 양쪽 땅의 목록에 한 번씩 들어갑니다
bridges = {
    "N": ["W", "W", "E"],          # 북쪽 땅: 서쪽 섬으로 다리 2 개, 동쪽 땅으로 1 개
    "W": ["N", "N", "S", "S", "E"],
    "E": ["N", "W", "S"],
    "S": ["W", "W", "E"],
}

for land, neighbors in bridges.items():
    print(f"{land}: 다리 {len(neighbors)} 개 → {neighbors}")
''')

md('''
한 정점에 붙은 선의 수를 그 정점의 **차수(degree)** 라고 합니다. N 은 3, W 는 5, E 는 3, S 는 3. **모두 홀수**입니다.

''' + think("패턴 인식 — 왜 차수가 답을 결정하나", "산책 중간에 지나가는 땅을 생각합니다. 그 땅에 <b>들어오는</b> 다리 하나, <b>나가는</b> 다리 하나를 씁니다. 다시 들르면 또 둘. 모든 다리를 한 번씩만 쓰므로, 중간에 지나가는 땅의 다리 수는 <b>반드시 짝수</b>여야 합니다.<br>홀수 다리를 가진 땅은 <b>출발점이나 도착점</b>일 수밖에 없습니다. 출발점과 도착점은 많아야 둘. 그러므로 <b>홀수 차수의 정점이 0개 또는 2개</b>일 때만 산책길이 있습니다.<br>쾨니히스베르크는 홀수 차수 정점이 <b>4개</b>. 산책길은 <b>없습니다.</b> 다리를 하나도 건너 보지 않고 답했습니다.") + '''

이 판단을 함수로 씁니다. 그래프 하나를 받아 “모든 선을 한 번씩 지나는 길이 있는가”를 돌려줍니다. 이런 길을 **오일러 경로(Euler path)** 라고 합니다.
''')

code('''
def odd_degree_vertices(graph):
    """차수가 홀수인 정점의 목록"""
    return [v for v, neighbors in graph.items() if len(neighbors) % 2 == 1]

def has_euler_path(graph):
    """모든 변을 정확히 한 번씩 지나는 길이 있으면 True (홀수 차수 정점이 0 개 또는 2 개)"""
    return len(odd_degree_vertices(graph)) in (0, 2)

print(odd_degree_vertices(bridges))
print(has_euler_path(bridges))
''')

md('''
**예상해 보기** — 다리를 하나 더 놓으면 어떻게 될까요? 북쪽 땅과 남쪽 땅 사이에 여덟 번째 다리를 놓습니다. (실제로 1875년에 비슷한 다리가 놓였습니다.)
''')

code('''
import copy
bridges8 = copy.deepcopy(bridges)        # 원본을 건드리지 않도록 복사 (5주차: 리스트 · 딕셔너리는 참조)
bridges8["N"].append("S")
bridges8["S"].append("N")

print(odd_degree_vertices(bridges8))
print(has_euler_path(bridges8))
''')

md('''
홀수 차수 정점이 W 와 E 둘만 남습니다. 이제 산책길이 **있습니다.** W 에서 출발해 E 에서 끝나면 됩니다.

''' + note("그래프 이론의 시작, 그리고 지금", "오일러의 이 풀이가 <b>그래프 이론</b>의 출발점입니다. 290년 뒤, 같은 생각이 곳곳에 있습니다. 지하철 노선도(역 = 정점, 선로 = 변), SNS 친구 관계(사람 = 정점, 친구 = 변), 인터넷(컴퓨터 = 정점, 회선 = 변), 분자 구조(원자 = 정점, 결합 = 변). 내비게이션이 길을 찾는 것도, 검색 엔진이 중요한 페이지를 고르는 것도 그래프 위의 계산입니다. <b>복잡한 현실에서 점과 선만 남기는 추상화</b>가 이 모든 것의 첫걸음입니다.") + '''

## 3-2. 그래프를 걷기 — 이웃을 따라가며 모두 방문하기

차수만으로 답이 나오는 문제는 드뭅니다. 보통은 그래프를 **직접 걸어야** 합니다. 걷는 방법에는 두 가지가 있는데, 6주차의 **스택과 큐**가 그 둘을 나눕니다.

가장 기본적인 질문부터: “A 에서 출발해 **갈 수 있는 곳**이 어디까지인가?” 이웃을 따라가되, **이미 가 본 곳은 다시 가지 않습니다.**
''')

code('''
friends = {                                  # 작은 친구 관계 그래프
    "지민": ["민수", "하늘"],
    "민수": ["지민", "바다"],
    "하늘": ["지민", "바다"],
    "바다": ["민수", "하늘", "솔"],
    "솔":   ["바다"],
    "유리": ["준"],                          # 유리 - 준 은 따로 떨어진 그룹
    "준":   ["유리"],
}

def reachable(graph, start):
    """start 에서 선을 따라 갈 수 있는 모든 정점의 집합"""
    visited = {start}                        # 가 본 곳 — 5주차의 집합(set)
    queue = [start]                          # 앞으로 둘러볼 곳 — 6주차의 큐
    while queue:
        current = queue.pop(0)               # 큐의 맨 앞을 꺼낸다
        for neighbor in graph[current]:
            if neighbor not in visited:      # 처음 보는 곳이면
                visited.add(neighbor)        #   가 본 곳으로 표시하고
                queue.append(neighbor)       #   큐의 맨 뒤에 넣어 나중에 둘러본다
    return visited

print(reachable(friends, "지민"))
print(reachable(friends, "유리"))
''')

md('''
`visited` 가 없으면 지민 → 민수 → 지민 → 민수 … 를 영원히 돕니다. “가 본 곳 표시”는 그래프를 걸을 때 **빠뜨리면 안 되는 것**입니다. 재귀의 ‘멈추는 경우’와 같은 역할입니다.

큐를 썼으므로 **가까운 곳부터** 둘러봅니다. 지민의 친구(민수, 하늘)를 먼저, 그다음 친구의 친구(바다), 그다음 친구의 친구의 친구(솔). 이렇게 **가까운 순서로 넓혀 가는** 탐색을 **너비 우선 탐색(BFS, breadth-first search)** 이라고 합니다. 큐 대신 스택을 쓰면 한 방향으로 **깊이 파고드는** 깊이 우선 탐색(DFS)이 됩니다. 1교시의 재귀가 바로 스택이므로, 재귀로 쓴 탐색은 DFS 입니다.

가까운 순서로 둘러본다는 성질이 다음 문제의 열쇠입니다.
''')

md("## 3-3. " + problem(5, "미로 최단 경로", "격자 미로가 있습니다. `#` 은 벽, `.` 은 길, `S` 는 출발, `G` 는 목표입니다. 상하좌우 한 칸씩 움직일 때, S 에서 G 까지 <b>가장 짧은 길은 몇 걸음</b>일까요? 갈 수 없으면 −1 입니다.") + '''

```
S . . # . .
. # . # . .
. # . . . #
. . # # . .
# . . . . G
```

''' + think("추상화 — 미로도 그래프다", "미로의 <b>길 칸 하나</b>를 정점으로, <b>이웃한 길 칸 사이</b>를 변으로 보면 미로는 그래프입니다. 쾨니히스베르크에서 땅과 다리가 하던 역할을 칸과 이웃 관계가 합니다. 그래프가 되었으니 3-2의 `reachable` 을 쓸 수 있습니다.<br>그런데 ‘갈 수 있나’가 아니라 ‘<b>몇 걸음</b>인가’를 물었습니다. BFS 는 <b>가까운 곳부터</b> 둘러보므로, 어떤 칸에 <b>처음 도착한 순간</b>의 걸음 수가 곧 <b>최단 거리</b>입니다. 더 짧은 길이 있었다면 그 길로 먼저 도착했을 것이기 때문입니다. 그러니 `visited` 집합 대신 <b>거리를 적는 딕셔너리</b>를 두면 됩니다.") + '''

미로는 문자열 리스트로 둡니다. 칸은 `(행, 열)` 튜플입니다. 이웃은 상하좌우 네 방향인데, 격자 밖이거나 벽이면 뺍니다.
''')

code('''
maze = [
    "S..#..",
    ".#.#..",
    ".#...#",
    "..##..",
    "#....G",
]

def find(maze, ch):
    """문자 ch 가 있는 칸의 (행, 열)"""
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == ch:
                return (r, c)

def neighbors(maze, cell):
    """상하좌우 이웃 중 격자 안이고 벽이 아닌 칸들"""
    r, c = cell
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:       # 위 · 아래 · 왼쪽 · 오른쪽
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] != "#":
            result.append((nr, nc))
    return result

start, goal = find(maze, "S"), find(maze, "G")
print(start, goal)
print(neighbors(maze, start))
print(neighbors(maze, (2, 2)))
''')

md('''
`neighbors` 가 그래프의 `graph[current]` 역할을 합니다. 미리 딕셔너리를 만들지 않고 **물을 때마다** 이웃을 계산할 뿐, 하는 일은 같습니다. 이제 3-2의 `reachable` 에 거리만 더합니다.
''')

code('''
def shortest_path_length(maze):
    start, goal = find(maze, "S"), find(maze, "G")
    distance = {start: 0}                    # 칸 → S 에서의 걸음 수. '가 본 곳' 표시도 겸합니다
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current == goal:                  # 목표에 처음 도착 — 이것이 최단 거리
            return distance[current]
        for nxt in neighbors(maze, current):
            if nxt not in distance:          # 처음 보는 칸이면
                distance[nxt] = distance[current] + 1      # 한 걸음 더
                queue.append(nxt)
    return -1                                # 큐가 비었는데 못 만났다 — 갈 수 없다

print(shortest_path_length(maze))
''')

md('''
9걸음입니다. 미로를 손으로 따라가 확인해 보세요. 길이 여러 개인데 BFS 는 그중 가장 짧은 것을 **자동으로** 고릅니다. “모든 길을 다 찾아 비교한다”는 코드는 어디에도 없습니다. 가까운 곳부터 둘러본다는 **순서**가 그 일을 대신합니다.

거리 표 `distance` 를 미로 위에 그려 보면 물결이 퍼지듯 숫자가 번져 가는 것이 보입니다.
''')

code('''
def show_distances(maze):
    start = find(maze, "S")
    distance = {start: 0}
    queue = [start]
    while queue:
        current = queue.pop(0)
        for nxt in neighbors(maze, current):
            if nxt not in distance:
                distance[nxt] = distance[current] + 1
                queue.append(nxt)
    for r, row in enumerate(maze):
        line = ""
        for c, cell in enumerate(row):
            if cell == "#":
                line += " ##"
            elif (r, c) in distance:
                line += f"{distance[(r, c)]:3d}"
            else:
                line += "  ."                # 벽에 막혀 갈 수 없는 칸
        print(line)

show_distances(maze)
''')

md('''
<details><summary><b>📎 더 알아보기 — 몇 걸음이 아니라 <code>어느 길</code>인지 알고 싶다면</b></summary>

각 칸에 **어디서 왔는지**(`came_from[칸] = 이전 칸`)를 함께 적어 두면, 목표에서 출발점까지 **거꾸로 따라가며** 길을 복원할 수 있습니다. 1교시의 호출 스택이 돌아갈 곳을 기억하던 것과 같은 생각입니다.

```python
came_from = {start: None}
# BFS 중: came_from[nxt] = current
# 끝난 뒤:
path = []
cell = goal
while cell is not None:
    path.append(cell)
    cell = came_from[cell]
path.reverse()          # goal → start 순서로 모았으니 뒤집습니다 (6주차 스택!)
```

과제 5 에서 직접 해 봅니다. 내비게이션이 길을 **그려 주는** 원리가 이것입니다. 실제 지도는 길마다 길이가 달라 BFS 대신 다익스트라(Dijkstra) 알고리듬을 쓰지만, ‘가까운 곳부터, 어디서 왔는지 기억하며’라는 뼈대는 같습니다.

</details>
''')

md(key("3교시 정리 — 그래프", "① <b>추상화</b>: 땅과 다리, 칸과 이웃, 사람과 친구 — 모두 점과 선으로 바꾸면 <b>같은 문제</b>가 됩니다.<br>② 그래프는 딕셔너리 `{정점: [이웃들]}` 로 표현합니다. 차수 = 이웃 목록의 길이.<br>③ 오일러: 홀수 차수 정점이 0개 또는 2개일 때만 모든 변을 한 번씩 지나는 길이 있습니다. 걸어 보지 않고 답합니다.<br>④ <b>BFS</b> = 큐 + 가 본 곳 표시. 가까운 순서로 둘러보므로 <b>처음 도착한 순간이 최단 거리</b>입니다."))

# ── 3교시 실습 ──
practice("✏️ 실습 3-1", "오일러 경로 판정", "약 5분",
         "아래 그래프 `envelope` 에 대해 3-1의 `odd_degree_vertices` 와 `has_euler_path` 를 <b>보지 않고 다시 써서</b> 판정하세요. 그런 다음 `envelope` 에 변을 <b>하나 더해</b>(양쪽 목록에 추가) 오일러 경로가 생기게 만들고, 그 그래프를 `envelope_fixed` 에 두세요.<br>`envelope` 은 ‘봉투’ 모양입니다: 정사각형 네 꼭짓점 A B C D 와 대각선 A–C, B–D. 한붓그리기가 될까요? 🧠 어느 두 정점을 이어야 홀수 차수 정점이 둘로 줄어드는지 생각하세요.",
         '''
envelope = {                       # 정사각형 A-B-C-D 와 대각선 A-C, B-D
    "A": ["B", "D", "C"],
    "B": ["A", "C", "D"],
    "C": ["B", "D", "A"],
    "D": ["A", "C", "B"],
}

# 여기에 odd_degree_vertices, has_euler_path 를 정의하세요


print(odd_degree_vertices(envelope), has_euler_path(envelope))

import copy
envelope_fixed = copy.deepcopy(envelope)
# 여기에 변을 하나 더해 envelope_fixed 에 오일러 경로가 생기게 하세요


print(odd_degree_vertices(envelope_fixed), has_euler_path(envelope_fixed))
''',
         'sorted(odd_degree_vertices(envelope)) == ["A", "B", "C", "D"] and has_euler_path(envelope) is False and has_euler_path(envelope_fixed) is True and sum(len(v) for v in envelope_fixed.values()) == sum(len(v) for v in envelope.values()) + 2 and has_euler_path({"X": ["Y", "Z"], "Y": ["X", "Z"], "Z": ["X", "Y"]}) is True',
         '''
envelope = {
    "A": ["B", "D", "C"],
    "B": ["A", "C", "D"],
    "C": ["B", "D", "A"],
    "D": ["A", "C", "B"],
}

def odd_degree_vertices(graph):
    return [v for v, neighbors in graph.items() if len(neighbors) % 2 == 1]

def has_euler_path(graph):
    return len(odd_degree_vertices(graph)) in (0, 2)

print(odd_degree_vertices(envelope), has_euler_path(envelope))     # ['A', 'B', 'C', 'D'] False

import copy
envelope_fixed = copy.deepcopy(envelope)
envelope_fixed["A"].append("B")        # 홀수 차수 정점 둘을 변으로 이으면 둘 다 짝수가 됩니다 (A-B 가 2 개가 됨)
envelope_fixed["B"].append("A")

print(odd_degree_vertices(envelope_fixed), has_euler_path(envelope_fixed))     # ['C', 'D'] True
''', raises=True, heading="## 3교시 실습")

practice("✏️ 실습 3-2", "친구 사이의 거리 — 몇 다리 건너면 아는 사람인가", "약 6분",
         "3-2의 `friends` 그래프에서, `start` 에서 각 사람까지의 <b>거리</b>(몇 명을 거쳐야 하는지)를 딕셔너리로 돌려주는 `bfs_distances(graph, start)` 를 쓰세요. 자기 자신은 0, 친구는 1, 친구의 친구는 2. 갈 수 없는 사람은 딕셔너리에 넣지 않습니다.<br>3-3의 `shortest_path_length` 와 같은 구조입니다. 목표가 없으니 큐가 빌 때까지 돌고 `distance` 전체를 돌려줍니다.<br>`bfs_distances(friends, \"지민\")` → `{\"지민\": 0, \"민수\": 1, \"하늘\": 1, \"바다\": 2, \"솔\": 3}`",
         '''
# 여기에 함수를 정의하세요


print(bfs_distances(friends, "지민"))
print(bfs_distances(friends, "솔"))
''',
         'bfs_distances(friends, "지민") == {"지민": 0, "민수": 1, "하늘": 1, "바다": 2, "솔": 3} and bfs_distances(friends, "솔") == {"솔": 0, "바다": 1, "민수": 2, "하늘": 2, "지민": 3} and bfs_distances(friends, "유리") == {"유리": 0, "준": 1}',
         '''
def bfs_distances(graph, start):
    distance = {start: 0}
    queue = [start]
    while queue:
        current = queue.pop(0)
        for neighbor in graph[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)
    return distance

print(bfs_distances(friends, "지민"))     # {'지민': 0, '민수': 1, '하늘': 1, '바다': 2, '솔': 3}
print(bfs_distances(friends, "솔"))
''', raises=True)

practice("✏️ 실습 3-3", "미로 — 갈 수 있는 칸의 수 (도전)", "",
         "3-3의 `find`, `neighbors` 를 그대로 쓰고, S 에서 <b>갈 수 있는 길 칸의 개수</b>(S 자신 포함)를 돌려주는 `count_reachable(maze)` 를 쓰세요. 3-2의 `reachable` 을 미로에 맞게 고치면 됩니다. (시간이 남는 사람만)<br>위의 `maze` 에서는 길 칸 22개가 모두 닿습니다.",
         '''
# 여기에 함수를 정의하세요


print(count_reachable(maze))
closed = ["S.#", "##.", "..G"]          # 완전히 막힌 미로
print(count_reachable(closed))
''',
         'count_reachable(maze) == 22 and count_reachable(["S.#", "##.", "..G"]) == 2 and count_reachable(["S.G"]) == 3',
         '''
def count_reachable(maze):
    start = find(maze, "S")
    visited = {start}
    queue = [start]
    while queue:
        current = queue.pop(0)
        for nxt in neighbors(maze, current):
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return len(visited)

print(count_reachable(maze))                        # 22
closed = ["S.#", "##.", "..G"]
print(count_reachable(closed))                      # 2
''', raises=True)

# ═════════════════════════ 주차 정리 ═════════════════════════
md('''
# 10주차 정리

오늘 다섯 문제를 풀며 쓴 생각의 틀은 넷입니다. 문법은 하나도 새로 배우지 않았습니다.

| 생각의 틀 | 컴퓨팅 사고 요소 | 핵심 질문 | 오늘의 문제 |
|:---|:---|:---|:---|
| **재귀** | 분해 | “가장 큰 한 조각만 보면, 나머지는 같은 문제인가?” | 하노이 탑 |
| **점화식 → DP** | 패턴 인식 | “마지막 한 걸음을 떼면, 그 앞은 더 작은 같은 문제인가?” | 계단 오르기 · 거스름돈 |
| **탐욕법 검증** | 알고리듬 | “쉬운 방법이 틀리는 반례가 있는가?” | 거스름돈 |
| **그래프 모델링** | 추상화 | “무엇을 지우면 점과 선만 남는가?” | 쾨니히스베르크 · 미로 |

| 개념 | 한 줄 요약 |
|:---|:---|
| **재귀** | 멈추는 경우 + 작아지는 문제. 호출 스택에 쌓였다 돌아온다 |
| **점화식** | f(n) 을 더 작은 f 로 나타낸 식. 작은 경우를 나열해 찾는다 |
| **겹치는 부분 문제** | 같은 작은 문제가 여러 번 — 단순 재귀가 지수적으로 느려지는 원인 |
| **메모이제이션** | 딕셔너리에 적어 두기. 재귀는 그대로, 세 줄 추가 |
| **동적 프로그래밍** | 0부터 표 채우기. 재귀 없이, 항상 맞고 빠르다 |
| **탐욕법** | 매 순간 최선 — 빠르지만 반례가 있을 수 있다 |
| **그래프** | `{정점: [이웃들]}`. 차수 = 이웃 수 |
| **BFS** | 큐 + 가 본 곳 표시. 처음 도착 = 최단 거리 |
| **지수적 증가** | $2^n$ — 64개 원판은 우주 나이의 40배. 알고리듬 선택이 컴퓨터 성능보다 중요한 이유 |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| `RecursionError` | 재귀가 너무 깊다 | 멈추는 경우가 없다 · 입력이 작아지지 않는다 |
| 끝나지 않는 셀 | 오류는 아니지만 신호 | 겹치는 부분 문제를 매번 다시 계산 (`climb(50)`) · `visited` 없는 그래프 탐색 (■ 버튼으로 중단) |
| 답은 나오는데 틀림 | 가장 무서운 신호 | 탐욕법 — 반례로 확인하지 않은 방법 |
| `KeyError` | 그 키가 없다 | 그래프에 없는 정점 · `distance` 에 없는 칸 |
| `IndexError` | 격자 밖 | `neighbors` 에서 범위 검사 누락 |

''' + key("오늘의 한 문장", "어려운 문제는 <b>통째로</b> 풀리지 않습니다. 가장 큰 조각 하나, 마지막 한 걸음, 점과 선만 남기기 — <b>문제를 다시 쓰는 것</b>이 풀이의 90%이고, 코드는 그 뒤에 따라옵니다. 이 방법들은 모두 수백 년 전 사람들이 종이와 연필로 찾아낸 것입니다. 컴퓨터는 그 생각을 빠르게 실행할 뿐입니다.") + f'''

<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 11주차 파일 입출력과 예외 처리</b><br>
프로그램이 파일을 읽고 쓰는 법, 그리고 오류가 났을 때 멈추지 않고 <b>대처하는</b> 법(`try` · `except`)을 배웁니다. 함수를 값처럼 다루는 일급 객체와 데코레이터(오늘 접은 상자의 `@lru_cache`)도 나옵니다.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 노트북을 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
''')

# ═════════════════════════ 과제 ═════════════════════════
FIRST_HW_CELL = len(CELLS)

md(f'''
# 10주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">생각의 틀 적용하기 — 재귀 · DP · 그래프</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>각 문제에 <b>어떤 생각의 틀</b>을 쓰는지 적혀 있습니다. 코드보다 먼저 🧠 상자처럼 ‘마지막 한 조각’을 한국어로 적어 보세요</li><li>4 ~ 9주차의 문법과 오늘의 네 가지 틀만으로 풀 수 있습니다</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 함수 이름과 매개변수 순서를 바꾸지 마세요. 점검 셀이 그 이름으로 부릅니다.<br>③ 점검 셀은 예시와 <b>다른 값</b>으로도 함수를 부릅니다. 점검 셀이 <b>끝나지 않으면</b> 메모이제이션이나 ‘가 본 곳 표시’가 빠진 것입니다. ■ 버튼으로 멈추고 고치세요.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다."))

practice("📝 과제 1", "회문 판별 — 재귀로", "",
         "<b>틀: 재귀.</b> 문자열이 앞뒤로 읽어도 같은 <b>회문</b>(palindrome)이면 `True` 를 돌려주는 `is_palindrome(text)` 를 <b>재귀로</b> 쓰세요. 슬라이싱 `[::-1]` 과 반복문은 쓰지 않습니다.<br>🧠 가장 바깥 글자 둘만 봅니다. 첫 글자와 끝 글자가 같고, <b>그 사이의 문자열이 회문</b>이면 회문입니다. 멈추는 경우: 길이가 0 또는 1 이면 회문. 사이의 문자열은 `text[1:-1]`.<br>`is_palindrome(\"level\")` → `True`, `is_palindrome(\"python\")` → `False`",
         '''
# 여기에 함수를 정의하세요


for word in ["level", "python", "noon", "a", "", "abca"]:
    print(repr(word), is_palindrome(word))
''',
         '[is_palindrome(w) for w in ["level", "python", "noon", "a", "", "abca", "racecar", "ab"]] == [True, False, True, True, True, False, True, False] and is_palindrome("기러기") is True',
         '''
def is_palindrome(text):
    if len(text) <= 1:                                  # 멈추는 경우
        return True
    if text[0] != text[-1]:                             # 바깥 두 글자가 다르면 끝
        return False
    return is_palindrome(text[1:-1])                    # 사이의 문자열이 회문인가 — 같은 문제, 더 짧게

for word in ["level", "python", "noon", "a", "", "abca"]:
    print(repr(word), is_palindrome(word))
''', raises=True, show_answer=False)

practice("📝 과제 2", "이진 탐색 — 반씩 버리기", "",
         "<b>틀: 분해(절반으로).</b> <b>오름차순으로 정렬된</b> 리스트 `items` 에서 `target` 의 위치(인덱스)를 찾아 돌려주는 `binary_search(items, target)` 를 쓰세요. 없으면 `-1`.<br>🧠 처음부터 하나씩 보지 않습니다. <b>가운데</b> 원소를 봅니다. 같으면 찾았고, `target` 이 더 작으면 <b>왼쪽 절반</b>만, 더 크면 <b>오른쪽 절반</b>만 남깁니다. 한 번 볼 때마다 후보가 절반으로 주니, 100만 개에서도 20번이면 끝납니다 — 하노이 탑의 $2^n$ 을 거꾸로 쓴 것입니다.<br>재귀(`low`, `high` 를 매개변수로 더한 도우미 함수)와 `while` 반복 중 편한 쪽으로 쓰세요. 단, `items.index()` 와 `in` 은 쓰지 않습니다.<br>`binary_search([1, 3, 5, 7, 9, 11], 7)` → `3`",
         '''
# 여기에 함수를 정의하세요


data = [1, 3, 5, 7, 9, 11]
print(binary_search(data, 7), binary_search(data, 1), binary_search(data, 11), binary_search(data, 4))
''',
         'binary_search([1, 3, 5, 7, 9, 11], 7) == 3 and binary_search([1, 3, 5, 7, 9, 11], 1) == 0 and binary_search([1, 3, 5, 7, 9, 11], 11) == 5 and binary_search([1, 3, 5, 7, 9, 11], 4) == -1 and binary_search([], 3) == -1 and binary_search([5], 5) == 0 and binary_search(list(range(0, 2000000, 2)), 1999998) == 999999 and binary_search(list(range(0, 2000000, 2)), 7) == -1',
         '''
def binary_search(items, target):
    low, high = 0, len(items) - 1             # 아직 후보인 구간
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif target < items[mid]:
            high = mid - 1                    # 왼쪽 절반만 남긴다
        else:
            low = mid + 1                     # 오른쪽 절반만 남긴다
    return -1

# 재귀로 쓰면:
# def binary_search(items, target):
#     def search(low, high):
#         if low > high:
#             return -1
#         mid = (low + high) // 2
#         if items[mid] == target:
#             return mid
#         if target < items[mid]:
#             return search(low, mid - 1)
#         return search(mid + 1, high)
#     return search(0, len(items) - 1)

data = [1, 3, 5, 7, 9, 11]
print(binary_search(data, 7), binary_search(data, 1), binary_search(data, 11), binary_search(data, 4))
''', raises=True, show_answer=False)

practice("📝 과제 3", "장애물이 있는 격자 길 찾기 — DP", "",
         "<b>틀: 점화식 → 표 채우기.</b> 실습 2-2의 격자에 <b>벽</b>이 생겼습니다. `grid` 는 문자열 리스트이고 `.` 은 길, `#` 은 벽입니다. 왼쪽 위에서 오른쪽 아래까지 오른쪽 · 아래로만 가는 경로의 수 `count_paths(grid)` 를 구하세요.<br>🧠 점화식은 실습 2-2와 같습니다. 단 <b>벽 칸의 경로 수는 0</b> 이고, 첫 행 · 첫 열도 벽이 나오면 그 뒤는 0 입니다. 그래서 첫 행 · 첫 열을 따로 1 로 채우지 말고, 모든 칸에서 ‘위 칸 + 왼쪽 칸’(격자 밖은 0)을 더하되 출발 칸만 1 로 두는 편이 단순합니다. 출발 칸이 벽이면 0.",
         '''
grid = [
    "....",
    ".#..",
    "...#",
    "....",
]

# 여기에 함수를 정의하세요


print(count_paths(grid))
print(count_paths(["...", "...", "..."]))      # 벽이 없으면 실습 2-2 와 같은 6
''',
         'count_paths(["...", "...", "..."]) == 6 and count_paths(["....", ".#..", "...#", "...."]) == 4 and count_paths(["..", "#."]) == 1 and count_paths([".#", "#."]) == 0 and count_paths(["."]) == 1 and count_paths(["#."]) == 0 and count_paths(["." * 10] * 10) == 48620',
         '''
def count_paths(grid):
    rows, cols = len(grid), len(grid[0])
    table = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#":
                table[r][c] = 0                              # 벽: 지나갈 수 없다
            elif r == 0 and c == 0:
                table[r][c] = 1                              # 출발 칸
            else:
                from_up = table[r - 1][c] if r > 0 else 0
                from_left = table[r][c - 1] if c > 0 else 0
                table[r][c] = from_up + from_left
    return table[rows - 1][cols - 1]

grid = [
    "....",
    ".#..",
    "...#",
    "....",
]
print(count_paths(grid))                           # 4
print(count_paths(["...", "...", "..."]))          # 6
''', raises=True, show_answer=False)

practice("📝 과제 4", "부분집합의 합 — 메모이제이션", "",
         "<b>틀: 재귀 + 메모이제이션.</b> 양의 정수 리스트 `nums` 의 원소를 <b>여러 번 써도 되게</b> 더해서 `target` 을 만들 수 있으면 `True` 를 돌려주는 `can_sum(nums, target)` 을 쓰세요.<br>🧠 마지막에 더한 수 하나만 봅니다. `target` 을 만들 수 있다 ⇔ 어떤 `n` 에 대해 `target − n` 을 만들 수 있다. 멈추는 경우: `target == 0` 이면 `True`(아무것도 안 더함), `target < 0` 이면 `False`.<br>메모 없이는 `can_sum([7, 14], 300)` 이 <b>끝나지 않습니다</b>(같은 `target` 을 수억 번 묻습니다). 딕셔너리 `memo` 에 `{target: 결과}` 를 적어 두세요. 함수 안에서 `memo = {}` 를 만들고 안쪽 도우미 함수가 쓰거나, 과제 2-3처럼 밖에 두어도 됩니다. 단, 밖에 둘 때는 `nums` 가 바뀌면 메모를 비워야 합니다 — 안쪽에 두는 편이 안전합니다.<br>`can_sum([5, 3, 4, 7], 7)` → `True`, `can_sum([2, 4], 7)` → `False`",
         '''
# 여기에 함수를 정의하세요


print(can_sum([5, 3, 4, 7], 7))
print(can_sum([2, 4], 7))
print(can_sum([7, 14], 300))
''',
         'can_sum([5, 3, 4, 7], 7) is True and can_sum([2, 4], 7) is False and can_sum([7, 14], 300) is False and can_sum([7, 14], 302) is False and can_sum([7, 14], 294) is True and can_sum([2, 3], 7) is True and can_sum([1], 0) is True and can_sum([3], 10) is False',
         '''
def can_sum(nums, target):
    memo = {}                                  # 이 호출 안에서만 쓰는 메모장 — nums 가 바뀌어도 안전합니다

    def helper(remaining):
        if remaining in memo:
            return memo[remaining]
        if remaining == 0:
            return True
        if remaining < 0:
            return False
        for n in nums:                         # 마지막에 더한 수가 n 이라면
            if helper(remaining - n):
                memo[remaining] = True
                return True
        memo[remaining] = False
        return False

    return helper(target)

print(can_sum([5, 3, 4, 7], 7))      # True
print(can_sum([2, 4], 7))            # False
print(can_sum([7, 14], 300))         # False — 메모 덕분에 바로 끝납니다
''', raises=True, show_answer=False)

practice("📝 과제 5", "미로의 최단 경로 그리기 (도전)", "",
         "<b>틀: BFS + 어디서 왔는지 기억.</b> 3-3의 `find`, `neighbors` 를 그대로 쓰고, S 에서 G 까지의 <b>최단 경로를 칸의 리스트</b>로 돌려주는 `shortest_path(maze)` 를 쓰세요. 리스트의 첫 원소는 S 의 칸, 마지막은 G 의 칸입니다. 갈 수 없으면 빈 리스트 `[]`.<br>🧠 3-3의 접은 상자대로, BFS 를 돌며 `came_from[다음 칸] = 지금 칸` 을 적어 둡니다. G 에 도착하면 `came_from` 을 따라 S 까지 <b>거꾸로</b> 올라가며 모은 뒤 뒤집습니다.<br>점검 셀은 경로가 ① S 에서 시작해 G 에서 끝나고, ② 매 걸음이 상하좌우 한 칸이며 벽이 아니고, ③ 길이가 최단 거리 + 1 인지 확인합니다. 최단 경로가 여럿이면 어느 것이든 통과합니다.",
         '''
# 여기에 함수를 정의하세요


path = shortest_path(maze)
print(len(path) - 1, "걸음")
print(path)
''',
         '(lambda p: p[0] == find(maze, "S") and p[-1] == find(maze, "G") and len(p) == 10 and all(b in neighbors(maze, a) for a, b in zip(p, p[1:])))(shortest_path(maze)) and shortest_path(["S.#", "##.", "..G"]) == [] and shortest_path(["S.G"]) == [(0, 0), (0, 1), (0, 2)]',
         '''
def shortest_path(maze):
    start, goal = find(maze, "S"), find(maze, "G")
    came_from = {start: None}                  # 칸 → 그 칸에 처음 도착했을 때의 이전 칸. '가 본 곳' 표시도 겸합니다
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current == goal:
            path = []
            cell = goal
            while cell is not None:            # G 에서 S 까지 거꾸로
                path.append(cell)
                cell = came_from[cell]
            path.reverse()
            return path
        for nxt in neighbors(maze, current):
            if nxt not in came_from:
                came_from[nxt] = current
                queue.append(nxt)
    return []

path = shortest_path(maze)
print(len(path) - 1, "걸음")          # 9 걸음
print(path)
''', raises=True, show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다. (과제 5는 3교시의 `maze` · `find` · `neighbors` 셀이 먼저 실행되어 있어야 합니다.)<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
def to_nb(cells):
    out, seen = [], set()
    for i, (ctype, src, meta) in enumerate(cells):
        cid = hashlib.md5(f"w10-{i}-{src}".encode("utf-8")).hexdigest()[:8]
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
    cells = [("markdown", "# 컴퓨팅사고 10주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 강의 노트북 `" + LECTURE + "` 맨 끝 ‘10주차 과제’의 정답 예시입니다. 과제 5는 3교시의 `maze` · `find` · `neighbors` 가 먼저 정의되어 있어야 합니다(아래 첫 코드 셀에 복사해 둠).", {})]
    cells.append(("code", '''
maze = [
    "S..#..",
    ".#.#..",
    ".#...#",
    "..##..",
    "#....G",
]

def find(maze, ch):
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            if cell == ch:
                return (r, c)

def neighbors(maze, cell):
    r, c = cell
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] != "#":
            result.append((nr, nc))
    return result
'''.strip("\n"), {}))
    for name, sol, chk in PRACTICES:
        if not name.startswith("과제"):
            continue
        expected = chk.split("lambda: ", 1)[1][:-1]
        cells.append(("markdown", f"## {name}\n\n자가 점검 기준: `{expected}`", {}))
        cells.append(("code", sol, {}))
    return cells


if __name__ == "__main__":
    n_code = sum(1 for c in CELLS if c[0] == "code")
    print(f"cells={len(CELLS)} code={n_code} practices={len(PRACTICES)} first_hw_cell={FIRST_HW_CELL}")
    if "--write" in sys.argv:
        save(to_nb(CELLS), os.path.join(DEST, LECTURE))
        save(to_nb(hw_solution_cells()), os.path.join(DEST, HW_SOL))
        print("saved:", LECTURE, "/", HW_SOL)

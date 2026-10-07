import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 6주차 노트북(강의용 + 과제 정답) 생성 스크립트
# 사용: python build_w6.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w6.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
LECTURE = "컴퓨팅사고_6주차_Python반복문.ipynb"
HW_SOL = "컴퓨팅사고_6주차_과제정답.ipynb"

# ───────────────────────── HTML 상자 (5주차 노트북과 같은 값) ─────────────────────────
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


BREAK = '<div style="text-align:center;color:#6B7280;">☕ 쉬는 시간 — 10분</div>'
CHECK_HEAD = "# 🔍 자가 점검 — 수정하지 말고 실행만 하세요\n"

# ───────────────────────── 셀 모으기 ─────────────────────────
CELLS = []          # (type, source, metadata)
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w6.py 가 사용


def md(src):
    CELLS.append(("markdown", src.strip("\n"), {}))


def code(src, raises=False, form=False):
    meta = {}
    if raises:
        meta["tags"] = ["raises-exception"]
    if form:
        meta["cellView"] = "form"                 # Colab: 코드 접기
        meta["jupyter"] = {"source_hidden": True}  # JupyterLab: 코드 접기
    CELLS.append(("code", src.strip("\n"), meta))


def practice(label, title, minutes, body, skeleton, test, solution, raises=False, heading=None, show_answer=True):
    """✏️ 상자 → 작성용 셀 → 🔍 점검 셀 → 💡 정답(접힘)"""
    box = task_box(label, title, minutes, body)
    md((heading + "\n\n" if heading else "") + box)
    code(skeleton, raises=raises)
    name = label.split(" ", 1)[1]
    chk = CHECK_HEAD + f'check("{name}", lambda: {test})'
    code(chk)
    if show_answer:
        md(answer(solution))
    PRACTICES.append((name, solution.strip("\n"), chk))


def caesar(text, shift):
    out = ""
    for ch in text:
        out += chr((ord(ch) - 97 + shift) % 26 + 97) if "a" <= ch <= "z" else ch
    return out


# ═════════════════════════ 표지 · 안내 ═════════════════════════
md(f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:34px 36px;border-radius:18px;{BOX}">
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 6주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">Python 반복문</div>
<div style="font-size:1.25em;margin-top:6px;">while 문 · for 문 &nbsp;·&nbsp; 컴프리헨션과 이터레이터 &nbsp;·&nbsp; 스택과 큐</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>
</div>
''')

md('''
# 6주차 학습 안내

지난주에는 값 **여러 개**를 리스트 · 딕셔너리에 묶어 담고, `if` 문으로 **조건에 따라** 할 일을 골랐습니다.
이번 주에는 제어문의 마지막 조각을 배웁니다. **같은 일을 여러 번** 시키는 방법입니다.

| 교시 | 주제 | 핵심 질문 |
|:---:|:---|:---|
| **1교시** | `while` 문 — 조건이 참인 동안 반복 | 1부터 10000까지 더하려면 `+` 를 만 번 써야 할까? |
| **2교시** | `for` 문 — 원소를 하나씩 꺼내며 반복 | 리스트의 원소를 처음부터 끝까지 하나씩 처리하려면? |
| **3교시** | 컴프리헨션 · 이터레이터, 스택과 큐 | 반복문을 한 줄로 줄이려면? 넣고 꺼내는 **순서**에 규칙을 두면 어떤 문제가 풀릴까? |

**오늘 수업을 마치면**

1. `while` 문과 `for` 문으로 반복을 만들고, `break` · `continue` 로 흐름을 조절할 수 있습니다.
2. `range()` 로 횟수를 정해 반복하고, 리스트 · 문자열 · 딕셔너리의 원소를 하나씩 처리할 수 있습니다.
3. 리스트 컴프리헨션으로 새 리스트를 한 줄로 만들고, 이터레이터가 무엇인지 설명할 수 있습니다.
4. 리스트로 스택과 큐를 만들어 문제를 풀 수 있습니다.

''' + key("이 노트북을 읽는 법", "회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요. 예상과 다를 때가 가장 많이 배우는 순간입니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 정답 예시는 접혀 있으니 먼저 스스로 풀어 보세요.<br>노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다. 4주차부터 오늘까지 배운 내용으로 푸는 문제입니다."))

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · while 문\n\n" + period(1, "조건이 참인 동안 되풀이하기 — while 문", [
    "반복문이 왜 필요한지 설명한다",
    "while 문으로 횟수를 세고 값을 누적한다",
    "무한 반복이 생기는 이유를 알고 멈출 수 있다",
    "break 로 반복을 중간에 끝낸다",
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

print("준비 완료! 이제 수업을 시작합니다.")
''', form=True)

md('''
## 1-1. 같은 일을 여러 번 — 왜 반복문이 필요할까?

1부터 10까지 더해 봅시다. 지금까지 배운 방법으로는 이렇게 씁니다.
''')

code('''
total = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10
print("1부터 10까지의 합:", total)
''')

md('''
1부터 **10000**까지라면 어떨까요? `+` 를 만 번 쓸 수는 없습니다.
사람은 이럴 때 “**1씩 키우면서 계속 더한다**”고 말합니다. 이 말을 코드로 옮긴 것이 **반복문(loop)** 입니다.

3주차 흐름도에서 **화살표가 위로 되돌아가는** 그림, 기억나나요? 그것이 **반복 구조**입니다.

| 구조 | 흐름도 | Python | 배우는 때 |
|:---|:---|:---|:---|
| 순차 | 네모가 한 줄로 이어짐 | 명령문을 차례로 씀 | 4주차 |
| 선택 | 마름모에서 참/거짓 두 갈래 | `if` 문 | 5주차 |
| **반복** | **화살표가 위로 되돌아감** | **`while` 문, `for` 문** | **오늘** |

Python의 반복문은 두 가지입니다.

| 반복문 | 한 줄 설명 | 일상의 예 |
|:---|:---|:---|
| `while` 문 | **조건이 참인 동안** 반복 | 버스가 올 때까지 기다린다 |
| `for` 문 | 자료의 원소를 **하나씩 꺼내며** 반복 | 출석부의 이름을 한 명씩 부른다 |

1교시에는 `while` 문을, 2교시에는 `for` 문을 다룹니다.
''')

md('''
## 1-2. `while` 문 — 조건이 참인 동안 반복

```
while 조건식:
    조건이 참인 동안 반복할 문장
    (여러 줄 가능)
```

모양은 `if` 문과 똑같습니다. 헤더는 콜론 `:` 으로 끝나고, 블록은 들여 씁니다.
다른 점은 하나입니다. 블록을 다 실행하면 **다시 조건식으로 돌아갑니다.**

- `if` 문: 조건이 참이면 블록을 **한 번** 실행합니다.
- `while` 문: 조건이 참인 **동안** 블록을 **계속** 실행합니다.

**예상해 보기** — 아래 셀은 인사를 몇 번 할까요? 마지막에 `count` 는 얼마일까요?
''')

code('''
count = 1
while count <= 3:
    print(count, "번째 인사: 안녕하세요")
    count = count + 1
print("끝. count =", count)
''')

md('''
컴퓨터가 한 일을 한 줄씩 따라가 봅시다.

| 조건 검사 | `count` | `count <= 3` | 하는 일 |
|:---:|:---:|:---:|:---|
| 1번째 | 1 | `True` | 인사하고 `count` 를 2로 |
| 2번째 | 2 | `True` | 인사하고 `count` 를 3으로 |
| 3번째 | 3 | `True` | 인사하고 `count` 를 4로 |
| 4번째 | 4 | `False` | 블록을 건너뛰고 `while` 문을 끝냄 |

조건은 **네 번** 검사하고, 블록은 **세 번** 실행했습니다. 끝났을 때 `count` 는 3이 아니라 **4**입니다.

**예상해 보기** — 조건이 처음부터 거짓이면 어떻게 될까요?
''')

code('''
count = 10
while count <= 3:
    print(count, "번째 인사: 안녕하세요")
    count = count + 1
print("끝. count =", count)
''')

md(key("while 문의 세 가지 재료", "① <b>시작값</b> — 반복 전에 변수를 준비합니다. `count = 1`<br>② <b>조건</b> — 계속할지 검사합니다. `count <= 3`<br>③ <b>변화</b> — 블록 안에서 변수를 바꿉니다. `count = count + 1`<br>셋 중 하나라도 빠지면 반복이 제대로 돌지 않습니다. 조건이 처음부터 거짓이면 블록은 <b>한 번도</b> 실행되지 않습니다."))

md('''
## 1-3. 누적 — 반복하며 값을 모으기

이제 1-1의 문제를 풉니다. 합계를 담을 변수를 **0으로 시작**해서, 반복할 때마다 더해 갑니다.
4주차에 배운 `total += n` 은 `total = total + n` 을 줄여 쓴 것입니다.
''')

code('''
total = 0              # 합계를 담을 변수. 0 에서 시작합니다
n = 1
last_num = 10
while n <= last_num:
    total += n         # 지금까지의 합계에 n 을 더합니다
    n += 1             # 다음 수로
print(f"1부터 {last_num}까지의 합계는 {total}입니다")
''')

md('''
`last_num` 을 `10000` 으로 바꾸고 다시 실행해 보세요. 고친 곳은 숫자 하나인데 일은 천 배로 늘었습니다. 이것이 반복문의 힘입니다.

**예상해 보기** — 블록 안 두 줄의 **순서를 바꾸면** 결과가 같을까요?
''')

code('''
total = 0
n = 1
while n <= 10:
    n += 1             # 먼저 키우고
    total += n         # 그다음에 더하면?
print(total)
''')

md(note("순서가 바뀌면 다른 프로그램입니다", "먼저 키우고 더하면 1은 빠지고 11이 들어갑니다. 2부터 11까지의 합이 되어 55가 아니라 65가 나옵니다. 결과가 예상과 다르면 1-2처럼 <b>표를 그려 한 줄씩 따라가 보세요.</b> 가장 확실한 방법입니다.")
   + "\n\n" + note("합계 변수의 이름을 `sum` 으로 짓지 마세요", "5주차에 쓴 `sum(scores)` 의 `sum` 은 Python이 미리 만들어 둔 함수 이름입니다. `sum = 0` 이라고 쓰면 그 이름이 숫자 0을 가리키게 되어, 그 뒤로는 `sum()` 을 쓸 수 없습니다. 그래서 이 노트북에서는 `total` 을 씁니다. `max`, `min`, `len`, `list` 도 같은 이유로 변수 이름으로 쓰지 않습니다."))

md('''
## 1-4. 무한 반복 — 끝나지 않는 `while`

**변화**를 빠뜨리면 어떻게 될까요? 아래 코드는 **실행하지 말고 눈으로만** 읽어 보세요.

```python
n = 1
while n <= 10:
    print(n)        # n += 1 을 빠뜨렸습니다
```

`n` 이 계속 1이므로 조건이 **영원히 참**입니다. 화면에 1이 끝없이 출력됩니다. 이것을 **무한 반복(infinite loop)** 이라고 합니다.
''')

md(warn("셀이 끝나지 않을 때는 ■ 버튼", "셀 왼쪽의 실행 버튼이 <b>■ (정지)</b> 모양으로 계속 돌고 있으면 무한 반복일 수 있습니다. ■ 버튼을 누르거나 메뉴에서 `Kernel → Interrupt Kernel` 을 누르세요. `KeyboardInterrupt` 라는 빨간 글씨가 나오면 잘 멈춘 것입니다. 고장이 아닙니다. 그다음 블록 안에서 <b>조건에 쓰인 변수가 바뀌는지</b> 확인하세요."))

md('''
## 1-5. `break` — 반복을 중간에 끝내기

`break` 는 **가장 가까운 반복문을 즉시 빠져나옵니다.** 보통 `if` 와 함께 써서 ‘찾던 것을 찾았으면 그만’이라고 말합니다.

**예상해 보기** — 제곱이 500을 처음으로 넘는 수는 얼마일까요?
''')

code('''
n = 1
while n <= 10000:
    if n * n > 500:        # 찾던 수를 발견하면
        break              # 반복을 즉시 끝냅니다
    n += 1
print(f"제곱이 500을 넘는 가장 작은 수는 {n}입니다")
''')

md('''
### `while True` 와 `break` — 몇 번 반복할지 모를 때

조건식 자리에 `True` 를 쓰면 **일부러 만든 무한 반복**이 됩니다. 끝낼 조건은 블록 안에서 `break` 로 정합니다.
사용자가 `q` 를 입력할 때까지 계속 입력받는 셀입니다. 몇 번 입력할지는 실행해 봐야 압니다.
''')

code('''
while True:
    word = input("단어를 입력하세요 (끝내려면 q): ")
    if word == "q":
        break
    print(f"{word} 은(는) {len(word)}글자입니다")
print("프로그램을 끝냅니다")
''')

md('''
### 예제 — 숫자 맞히기 게임

컴퓨터가 1 ~ 100 중 하나를 고르고, 맞힐 때까지 ‘크다 / 작다’를 알려 줍니다.
지금까지 배운 `input()`, `int()`, `if` - `elif` - `else`, `while`, `break` 가 모두 들어 있습니다. 실행해서 직접 맞혀 보세요.
''')

code('''
import random                        # 무작위 수를 만드는 도구를 가져옵니다

answer = random.randint(1, 100)      # 1 ~ 100 중 하나를 고릅니다
tries = 0

while True:
    guess = int(input("1 ~ 100 사이의 수를 맞혀 보세요: "))
    tries += 1
    if guess > answer:
        print("정답보다 큰 수입니다")
    elif guess < answer:
        print("정답보다 작은 수입니다")
    else:
        print(f"정답입니다! {tries}번 만에 맞혔습니다")
        break
''')

md(note("생각해 보기 — 몇 번이면 반드시 맞힐 수 있을까?", "아무 수나 부르면 운이 나쁠 때 100번이 걸립니다. 항상 <b>남은 범위의 가운데</b>를 부르면 한 번에 범위가 절반으로 줄어듭니다. 100 → 50 → 25 → 13 → 7 → 4 → 2 → 1 이므로 <b>7번 안에</b> 반드시 맞힙니다. 문제를 절반씩 줄여 가는 이 방법을 이진 탐색(binary search)이라고 합니다. 같은 문제도 <b>방법(알고리듬)</b>에 따라 걸리는 횟수가 크게 달라집니다."))

md('''
<details><summary><b>📎 더 알아보기 — <code>while</code> - <code>else</code> : break 없이 끝났을 때만 실행</b></summary>

`while` 문에도 `else:` 블록을 붙일 수 있습니다. `if` 의 `else` 와 뜻이 다릅니다.
**`break` 로 빠져나오지 않고 조건이 거짓이 되어 끝났을 때만** 실행됩니다.

```python
n = 7
i = 2
while i < n:
    if n % i == 0:
        print(f"{n}은(는) {i}로 나누어떨어집니다")
        break
    i += 1
else:
    print(f"{n}은(는) 끝까지 나누어떨어지지 않았습니다")   # break 가 없었을 때만
```

‘끝까지 찾아봤지만 없었다’를 표현할 때 씁니다. 자주 쓰지는 않으니, 이런 문법이 있다는 것만 알아 두세요.

</details>
''')

md(key("while 문 정리", "① `while 조건식:` 은 조건이 참인 <b>동안</b> 블록을 되풀이합니다.<br>② <b>시작값 · 조건 · 변화</b> 세 가지가 모두 있어야 합니다.<br>③ 합계는 `0` 에서 시작해 `total += n` 으로 누적합니다.<br>④ 변화를 빠뜨리면 무한 반복입니다. ■ 버튼으로 멈춥니다.<br>⑤ `break` 는 반복을 즉시 끝냅니다. 횟수를 모를 때는 `while True:` 와 `break` 를 함께 씁니다."))

# ── 1교시 실습 ──
practice("✏️ 실습 1-1", "짝수만 더하기", "약 4분",
         "`while` 문으로 1부터 100까지의 수 중 <b>짝수만</b> 더해 `total` 에 넣으세요. 힌트: 짝수는 `n % 2 == 0` 입니다. 블록 안에 `if` 를 넣을 수 있습니다.",
         '''
total = 0
n = 1

# 여기에 while 문을 작성하세요


print(total)
''',
         "total == 2550",
         '''
total = 0
n = 1

while n <= 100:
    if n % 2 == 0:
        total += n
    n += 1

print(total)        # 2550

# 다른 방법: n 을 2 에서 시작해 2씩 키우면 if 가 필요 없습니다
''', heading="## 1교시 실습")

practice("✏️ 실습 1-2", "내 돈이 두 배가 되려면 몇 년?", "약 5분",
         "100만 원을 연 이자율 5%인 예금에 넣었습니다. 해마다 `money` 가 1.05배가 됩니다. `money` 가 <b>200만 원 이상</b>이 될 때까지 몇 년이 걸리는지 `years` 에 구하세요. 몇 번 반복할지 미리 알 수 없으니 `while` 문이 잘 맞습니다.",
         '''
money = 1000000
years = 0

# 여기에 while 문을 작성하세요 (money 가 2000000 보다 작은 동안 반복)


print(f"{years}년 뒤: {money:,.0f}원")
''',
         "years == 15 and money >= 2000000",
         '''
money = 1000000
years = 0

while money < 2000000:
    money = money * 1.05      # money *= 1.05 로 써도 됩니다
    years += 1

print(f"{years}년 뒤: {money:,.0f}원")     # 15년 뒤: 2,078,928원
''')

practice("✏️ 실습 1-3", "소수 판별", "약 7분",
         "1과 자기 자신으로만 나누어떨어지는 2 이상의 수를 <b>소수(prime number)</b>라고 합니다. `n` 이 소수이면 `is_prime` 이 `True`, 아니면 `False` 가 되게 하세요.<br>방법: `i` 를 2부터 `n - 1` 까지 1씩 키우면서 `n % i == 0` 인지 봅니다. 나누어떨어지는 `i` 를 <b>하나라도 찾으면</b> `is_prime` 을 `False` 로 바꾸고 `break` 합니다.<br>통과한 뒤 `n` 을 `97`, `100` 으로 바꿔 다시 확인해 보세요.",
         '''
n = 91
is_prime = True      # 일단 소수라고 가정하고 시작합니다
i = 2

# 여기에 while 문을 작성하세요


print(n, is_prime)
''',
         "is_prime == all(n % k != 0 for k in range(2, n))",
         '''
n = 91
is_prime = True      # 일단 소수라고 가정하고 시작합니다
i = 2

while i < n:
    if n % i == 0:           # 나누어떨어지는 수를 찾았다
        is_prime = False     # → 소수가 아니다
        break                # 더 볼 필요가 없으니 반복을 끝낸다
    i += 1

print(n, is_prime)   # 91 False (91 = 7 x 13),  97 True,  100 False
''')

md(key("1교시 정리", "① 반복문은 같은 일을 여러 번 시킵니다. 흐름도의 ‘되돌아가는 화살표’입니다.<br>② `while 조건식:` 은 조건이 참인 동안 블록을 되풀이합니다. 시작값 · 조건 · 변화를 챙기세요.<br>③ ‘0에서 시작해 반복하며 더하기’는 가장 자주 쓰는 패턴입니다.<br>④ `break` 는 반복을 즉시 끝냅니다. ‘찾으면 그만’인 문제에 씁니다.<br>⑤ 셀이 끝나지 않으면 ■ 버튼을 누르고, 조건에 쓰인 변수가 바뀌는지 확인합니다.") + "\n\n" + BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · for 문\n\n" + period(2, "원소를 하나씩 꺼내며 되풀이하기 — for 문", [
    "for 문으로 리스트 · 문자열 · 딕셔너리의 원소를 하나씩 처리한다",
    "range() 로 횟수와 범위를 정해 반복한다",
    "while 문과 for 문 중 알맞은 것을 고른다",
    "continue 로 이번 차례만 건너뛴다",
]))

md('''
## 2-1. `for` 문 — 원소를 하나씩 꺼내기

```
for 변수 in 자료:
    원소마다 반복할 문장
```

자료의 **원소를 앞에서부터 하나씩** 꺼내 변수에 넣고, 그때마다 블록을 실행합니다. 원소가 다 떨어지면 끝납니다.
영어 문장처럼 읽으면 됩니다. “menus **안에 있는** 각 menu **에 대해**”.
''')

code('''
menus = ["americano", "latte", "frappuccino"]
for menu in menus:
    print(menu)
print("주문 끝")
''')

md('''
변수 이름은 자유롭게 지을 수 있습니다. 리스트는 **복수형**(`menus`), 꺼낸 원소는 **단수형**(`menu`)으로 지으면 읽기 쉽습니다.

5주차에는 `sum()` 으로 합계를 구했습니다. 이번에는 1교시의 **누적 패턴**으로 직접 구해 봅시다.
''')

code('''
scores = [85, 92, 78, 64, 95]
total = 0
for score in scores:
    total += score
print(total, total / len(scores))
''')

md('''
같은 일을 `while` 문으로 쓰면 이렇게 됩니다. 두 셀을 비교해 보세요.
''')

code('''
scores = [85, 92, 78, 64, 95]
total = 0
i = 0                        # 시작값
while i < len(scores):       # 조건
    total += scores[i]
    i += 1                   # 변화
print(total, total / len(scores))
''')

md(key("for 문은 번호를 관리할 필요가 없습니다", "`while` 문에서는 번호 `i` 의 시작값 · 조건 · 변화를 직접 챙겼습니다. `for` 문은 ‘다음 원소 꺼내기’를 Python이 대신 합니다. 그래서 `i += 1` 을 빠뜨려 무한 반복에 빠질 일이 없습니다. <b>자료의 원소를 모두 처리할 때는 for 문</b>을 씁니다."))

md('''
## 2-2. 문자열도 한 글자씩

5주차에 문자열은 ‘글자를 순서대로 나열한 자료’라고 했습니다. 그래서 `for` 문에 쓸 수 있습니다. 튜플도 마찬가지입니다.
''')

code('''
for ch in "abc":
    print(ch)
''')

md('''
**예상해 보기** — 아래 셀은 무엇을 세고 있을까요? 결과는?
''')

code('''
count = 0
for ch in "banana":
    if ch == "a":
        count += 1
print(count)
''')

md('''
‘0에서 시작해 조건에 맞을 때마다 1씩 더하기’는 **개수 세기** 패턴입니다. 합계 누적과 모양이 같습니다.

## 2-3. `range()` — 숫자를 차례로 만들기

‘100번 반복’처럼 **횟수**만 정하고 싶을 때는 `range()` 를 씁니다.

**예상해 보기** — `range(5)` 는 어떤 수를 만들까요? 5가 들어 있을까요?
''')

code('''
for i in range(5):
    print(i)
''')

md('''
`range(5)` 는 **0부터 4까지** 다섯 개를 만듭니다. 5주차 슬라이싱처럼 **끝 번호 바로 앞까지**입니다.

| 쓰는 법 | 만드는 수 | 설명 |
|:---|:---|:---|
| `range(5)` | 0, 1, 2, 3, 4 | 0부터 5 **앞까지** |
| `range(1, 6)` | 1, 2, 3, 4, 5 | 1부터 6 앞까지 |
| `range(1, 10, 2)` | 1, 3, 5, 7, 9 | 1부터 10 앞까지 **2씩 증가** |
| `range(10, 1, -1)` | 10, 9, 8, …, 2 | 10부터 1 앞까지 **1씩 감소** |

`list()` 로 감싸면 어떤 수가 만들어지는지 한눈에 볼 수 있습니다.
''')

code('''
print(list(range(5)))
print(list(range(1, 6)))
print(list(range(1, 10, 2)))
print(list(range(10, 1, -1)))
''')

md('''
이제 1부터 10000까지의 합을 `for` 문으로 구합니다. 1-3의 `while` 문과 비교해 보세요.
''')

code('''
total = 0
for n in range(1, 10001):      # 10000 까지 넣으려면 끝을 10001 로
    total += n
print(total)
''')

md(key("while 과 for, 언제 무엇을 쓸까", "<b>for 문</b> — 반복할 대상이나 횟수가 <b>정해져 있을 때</b>. ‘리스트의 모든 원소’, ‘1부터 100까지’, ‘10번’.<br><b>while 문</b> — 언제 끝날지 <b>미리 모를 때</b>. ‘정답을 맞힐 때까지’, ‘돈이 두 배가 될 때까지’, ‘q 를 입력할 때까지’.<br>둘 다 쓸 수 있으면 `for` 문이 짧고 안전합니다."))

md('''
## 2-4. `continue` — 이번 차례만 건너뛰기

`break` 는 반복문을 **끝냅니다.** `continue` 는 **이번 차례의 남은 문장만 건너뛰고** 다음 차례로 갑니다.

**예상해 보기** — 아래 셀에서 출력되지 않는 수는?
''')

code('''
for i in range(10):
    if i == 5:
        continue           # 5 일 때는 아래 print 를 건너뜁니다
    print(i)
print("End of Program")
''')

md('''
`continue` 를 `break` 로 바꾸고 다시 실행해 보세요.

| | 하는 일 | 비유 |
|:---|:---|:---|
| `break` | 반복문 전체를 끝냄 | 줄넘기를 그만둔다 |
| `continue` | 이번 차례만 건너뛰고 계속 | 줄에 걸린 한 번만 빼고 계속 넘는다 |

둘 다 `while` 문과 `for` 문에서 똑같이 쓸 수 있습니다.

## 2-5. 딕셔너리와 `for` 문

딕셔너리를 `for` 문에 쓰면 **키**가 하나씩 나옵니다. 값은 `딕셔너리[키]` 로 꺼냅니다.
''')

code('''
country_code = {"America": 1, "Korea": 82, "China": 86, "Japan": 81}
for country in country_code:
    print(country, country_code[country])
''')

md('''
5주차에 본 `values()` 와 `items()` 를 쓰면 값만, 또는 키와 값을 함께 꺼낼 수 있습니다.
`items()` 는 `(키, 값)` 튜플을 하나씩 줍니다. 5주차의 `x, y = t` 처럼 변수 두 개로 풀어 받습니다.
''')

code('''
for code in country_code.values():           # 값만
    print(code)

for country, code in country_code.items():   # 키와 값을 함께
    print(f"{country}: +{code}")
''')

md('''
## 2-6. `enumerate()` — 번호와 함께 꺼내기

원소와 함께 ‘몇 번째인지’도 필요할 때가 있습니다. `enumerate()` 는 `(번호, 원소)` 를 하나씩 줍니다.
''')

code('''
menus = ["americano", "latte", "frappuccino"]
for number, menu in enumerate(menus, start=1):     # start 를 빼면 0 부터 셉니다
    print(f"{number}번 메뉴: {menu}")
''')

md('''
<details><summary><b>📎 더 알아보기 — <code>zip()</code> : 두 리스트를 나란히 꺼내기</b></summary>

`zip()` 은 리스트 두 개에서 **같은 자리의 원소끼리** 짝지어 줍니다. 지퍼의 양쪽 이가 맞물리는 모습을 떠올리세요.

```python
names = ["김연세", "이미래", "박원주"]
scores = [88, 95, 72]
for name, score in zip(names, scores):
    print(f"{name}: {score}점")
```

길이가 다르면 **짧은 쪽**에 맞춰 끝납니다.

</details>

## 2-7. 반복문 안의 반복문

`if` 안에 `if` 를 넣었듯이, 반복문 안에 반복문을 넣을 수 있습니다.
바깥 반복이 **한 번** 도는 동안 안쪽 반복은 **처음부터 끝까지** 돕니다. 시계의 시침과 분침을 떠올리세요.

**예상해 보기** — 아래 셀은 곱셈식을 모두 몇 줄 출력할까요?
''')

code('''
for dan in range(2, 4):            # 2단, 3단
    for i in range(1, 4):          # 각 단마다 1, 2, 3
        print(f"{dan} x {i} = {dan * i}")
    print("-----")                 # 한 단이 끝날 때마다
''')

md(key("for 문 정리", "① `for 변수 in 자료:` 는 원소를 하나씩 꺼내며 블록을 반복합니다.<br>② 리스트 · 튜플 · 문자열은 원소를, 딕셔너리는 <b>키</b>를 줍니다. 키와 값을 함께 꺼내려면 `items()`.<br>③ `range(시작, 끝, 간격)` 은 끝 <b>바로 앞까지</b> 수를 만듭니다.<br>④ `break` 는 반복을 끝내고, `continue` 는 이번 차례만 건너뜁니다.<br>⑤ 번호가 필요하면 `enumerate()` 를 씁니다."))

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "합격자 수 세기", "약 3분",
         "`for` 문으로 `scores` 에서 <b>60점 이상</b>인 점수의 개수를 세어 `pass_count` 에 넣으세요. 2-2의 개수 세기 패턴을 씁니다.",
         '''
scores = [85, 42, 78, 64, 95, 58, 60, 33]
pass_count = 0

# 여기에 for 문을 작성하세요


print(f"합격자: {pass_count}명")
''',
         "pass_count == 5",
         '''
scores = [85, 42, 78, 64, 95, 58, 60, 33]
pass_count = 0

for score in scores:
    if score >= 60:
        pass_count += 1

print(f"합격자: {pass_count}명")     # 5명
''', heading="## 2교시 실습")

practice("✏️ 실습 2-2", "max() 없이 최고점 찾기", "약 5분",
         "`max()` 는 안에서 어떤 일을 할까요? 직접 만들어 봅시다. 사람이 시험지를 한 장씩 넘기며 최고점을 찾는 방법과 같습니다.<br>① 첫 번째 점수를 ‘지금까지의 최고점’으로 기억합니다. ② 점수를 하나씩 보면서, 기억한 값보다 크면 그 점수로 <b>바꿔 기억</b>합니다.<br>결과를 `top_score` 에 넣으세요. `max()` 는 쓰지 않습니다.",
         '''
scores = [85, 42, 78, 64, 95, 58, 60, 33]
top_score = scores[0]      # 일단 첫 번째 점수를 최고점으로 기억합니다

# 여기에 for 문을 작성하세요


print(f"최고점: {top_score}점")
''',
         "top_score == 95",
         '''
scores = [85, 42, 78, 64, 95, 58, 60, 33]
top_score = scores[0]      # 일단 첫 번째 점수를 최고점으로 기억합니다

for score in scores:
    if score > top_score:      # 더 큰 점수를 만나면
        top_score = score      # 바꿔 기억한다

print(f"최고점: {top_score}점")     # 95점
''')

practice("✏️ 실습 2-3", "단어 세기 — 작은 텍스트 마이닝", "약 7분",
         "글에 <b>어떤 단어가 몇 번</b> 나오는지 세는 것은 텍스트 분석의 첫걸음입니다. `text` 에 나오는 단어와 그 횟수를 딕셔너리 `word_count` 에 담으세요. 예: `{'the': 4, 'cat': 2, ...}`<br>① `text.split()` 으로 단어 리스트를 만듭니다. ② 단어를 하나씩 꺼냅니다. ③ 그 단어가 `word_count` 에 <b>이미 있으면</b> 값을 1 키우고, <b>없으면</b> 1로 새로 넣습니다.",
         '''
text = "the cat saw the dog and the dog saw the cat"
word_count = {}

# 여기에 코드를 작성하세요


print(word_count)
''',
         'word_count == {"the": 4, "cat": 2, "saw": 2, "dog": 2, "and": 1}',
         '''
text = "the cat saw the dog and the dog saw the cat"
word_count = {}

for word in text.split():
    if word in word_count:
        word_count[word] += 1      # 이미 있는 단어 → 1 키우기
    else:
        word_count[word] = 1       # 처음 나온 단어 → 1 로 새로 넣기

print(word_count)

# if - else 네 줄은 get() 으로 한 줄이 됩니다
#     word_count[word] = word_count.get(word, 0) + 1
''')

practice("✏️ 실습 2-4", "3 · 6 · 9 게임 (도전)", "",
         "1부터 20까지 차례로 말하되, <b>3의 배수</b>일 때는 숫자 대신 `\"짝\"` 을 말합니다. 말한 것을 순서대로 리스트 `said` 에 담으세요. 예: `[1, 2, '짝', 4, 5, '짝', ...]` (시간이 남는 사람만)",
         '''
said = []

# 여기에 코드를 작성하세요 (range 와 append 를 쓰세요)


print(said)
''',
         'said == [("짝" if k % 3 == 0 else k) for k in range(1, 21)]',
         '''
said = []

for n in range(1, 21):
    if n % 3 == 0:
        said.append("짝")
    else:
        said.append(n)

print(said)
''')

md(key("2교시 정리", "① `for 변수 in 자료:` 는 자료의 원소를 하나씩 꺼내며 반복합니다.<br>② `range()` 로 횟수와 범위를 정합니다. 끝 번호는 들어가지 않습니다.<br>③ 대상이 정해져 있으면 `for`, 언제 끝날지 모르면 `while`.<br>④ 자주 쓰는 세 패턴: <b>누적</b>(`total += x`), <b>개수 세기</b>(`count += 1`), <b>최댓값 찾기</b>(더 크면 바꿔 기억).<br>⑤ 딕셔너리로 단어 수를 셀 수 있습니다. ‘있으면 1 키우고, 없으면 1로 넣기’.") + "\n\n" + BREAK)

# ═════════════════════════ 3교시 ═════════════════════════
md("# 3교시 · 반복문 응용\n\n" + period(3, "반복문 응용 — 컴프리헨션 · 이터레이터 · 스택과 큐", [
    "리스트 컴프리헨션으로 새 리스트를 한 줄로 만든다",
    "이터레이터가 무엇인지, for 문이 어떻게 원소를 꺼내는지 설명한다",
    "스택(나중에 넣은 것 먼저)과 큐(먼저 넣은 것 먼저)를 리스트로 만든다",
    "스택과 큐로 간단한 문제를 푼다",
]))

md('''
## 3-1. 리스트 컴프리헨션 — 반복문 한 줄로 리스트 만들기

실습 2-4에서 쓴 **‘빈 리스트 만들기 → 반복 → `append()`’** 는 정말 자주 나오는 패턴입니다.
''')

code('''
numbers = [1, 2, 3, 4, 5]

squares = []
for n in numbers:
    squares.append(n * n)
print(squares)
''')

md('''
Python은 이 세 줄을 **한 줄**로 쓰는 문법을 제공합니다. **리스트 컴프리헨션(list comprehension)** 이라고 합니다.
''')

code('''
squares = [n * n for n in numbers]
print(squares)
''')

md('''
대괄호 안을 **뒤에서부터** 읽으면 쉽습니다. “`numbers` 의 각 `n` 에 대해, `n * n` 을 모은 리스트”.
수학 시간에 집합을 $\\{\\,n^2 \\mid n \\in A\\,\\}$ 처럼 쓰던 것과 같은 생각입니다.

```
[ 식  for 변수 in 자료 ]
  ↑         ↑
  모을 값    for 문의 헤더 그대로
```

**예상해 보기** — 두 줄의 결과는?
''')

code('''
print([len(word) for word in ["sun", "moon", "star"]])
print([n * 2 for n in range(5)])
''')

md('''
### 조건 붙이기 — 골라 담기

뒤에 `if 조건` 을 붙이면 **조건에 맞는 원소만** 담습니다.
''')

code('''
scores = [85, 42, 78, 64, 95, 58]

high_scores = [score for score in scores if score >= 80]
print(high_scores)

even_squares = [n * n for n in range(1, 11) if n % 2 == 0]
print(even_squares)
''')

md(key("리스트 컴프리헨션 정리", "`[식 for 변수 in 자료]` — 원소마다 식을 계산해 <b>바꿔 담기</b><br>`[식 for 변수 in 자료 if 조건]` — 조건에 맞는 것만 <b>골라 담기</b><br>결과는 항상 <b>새 리스트</b>입니다. 원래 자료는 바뀌지 않습니다.<br>한 줄이 너무 길어져 읽기 어려우면 그냥 `for` 문으로 쓰세요. 짧은 코드보다 <b>읽기 쉬운 코드</b>가 좋은 코드입니다."))

md('''
<details><summary><b>📎 더 알아보기 — 딕셔너리 · 집합 컴프리헨션</b></summary>

대괄호를 중괄호로 바꾸면 딕셔너리와 집합도 같은 방식으로 만들 수 있습니다.

```python
words = ["sun", "moon", "star"]

lengths = {word: len(word) for word in words}     # 딕셔너리: {키: 값 for ...}
print(lengths)            # {'sun': 3, 'moon': 4, 'star': 4}

kinds = {len(word) for word in words}             # 집합: {값 for ...}
print(kinds)              # {3, 4}
```

</details>
''')

practice("✏️ 실습 3-1", "컴프리헨션으로 바꿔 담기 · 골라 담기", "약 5분",
         "`celsius_list` 는 일주일의 낮 기온(섭씨)입니다. 리스트 컴프리헨션으로 아래 두 리스트를 만드세요.<br>① 모든 기온을 화씨로 바꾼 `fahrenheit_list` — 4주차의 공식 `celsius * 9 / 5 + 32`<br>② 30도 <b>이상</b>인 기온만 고른 `hot_list`",
         '''
celsius_list = [28, 31, 25, 33, 30, 22, 27]

fahrenheit_list = []      # ← [] 를 지우고 컴프리헨션을 쓰세요
hot_list = []             # ← [] 를 지우고 컴프리헨션을 쓰세요

print(fahrenheit_list)
print(hot_list)
''',
         "len(fahrenheit_list) == 7 and all(abs(f - (c * 9 / 5 + 32)) < 1e-6 for f, c in zip(fahrenheit_list, celsius_list)) and hot_list == [31, 33, 30]",
         '''
celsius_list = [28, 31, 25, 33, 30, 22, 27]

fahrenheit_list = [celsius * 9 / 5 + 32 for celsius in celsius_list]
hot_list = [celsius for celsius in celsius_list if celsius >= 30]

print(fahrenheit_list)
print(hot_list)           # [31, 33, 30]
''')

md('''
## 3-2. 이터레이터 — `for` 문은 어떻게 하나씩 꺼낼까?

지금까지 `for` 문 뒤에 리스트, 튜플, 문자열, 딕셔너리, `range()` 를 썼습니다.
이렇게 `for` 문에 쓸 수 있는 자료를 **반복 가능한 자료(iterable)** 라고 합니다.

그런데 `for` 문은 ‘지금 몇 번째까지 꺼냈는지’를 어떻게 기억할까요? 그 일을 맡은 것이 **이터레이터(iterator)** 입니다.
이터레이터는 **책갈피**와 같습니다. 책(자료)은 그대로 있고, 책갈피가 ‘다음에 읽을 곳’을 기억합니다.

- `iter(자료)` — 자료에 책갈피를 하나 꽂습니다. (이터레이터를 만듭니다)
- `next(이터레이터)` — 다음 원소를 하나 꺼내고, 책갈피를 한 칸 옮깁니다.
''')

code('''
menus = ["americano", "latte", "frappuccino"]
it = iter(menus)        # 이터레이터를 만듭니다

print(next(it))
print(next(it))
print(next(it))
''')

md(boom("원소가 다 떨어졌는데 한 번 더 꺼내면?"))

code('''
next(it)
''', raises=True)

md('''
`StopIteration` 은 ‘더 꺼낼 것이 없다’는 신호입니다. 이제 `for` 문이 하는 일을 설명할 수 있습니다.

1. `iter()` 로 이터레이터를 만든다.
2. `next()` 로 원소를 하나 꺼내 변수에 넣고 블록을 실행한다.
3. 2를 되풀이하다가 `StopIteration` 신호가 오면 **오류 없이 조용히** 끝낸다.

우리는 `for menu in menus:` 한 줄만 쓰면 됩니다. 나머지는 `for` 문이 대신 합니다.

### 이터레이터는 한 번 지나가면 끝입니다

**예상해 보기** — 같은 이터레이터를 두 번 `list()` 로 바꾸면?
''')

code('''
it = iter([1, 2, 3])
print(list(it))       # 처음부터 끝까지 꺼냅니다
print(list(it))       # 한 번 더 꺼내면?
''')

md('''
책갈피가 이미 맨 끝에 가 있으므로 두 번째는 빈 리스트입니다. 다시 쓰려면 `iter()` 로 **새로** 만들어야 합니다.
리스트 자체는 그대로이므로 `for` 문은 몇 번이든 다시 쓸 수 있습니다. `for` 문이 매번 새 이터레이터를 만들기 때문입니다.

### 필요할 때 하나씩 만든다

`range()` 는 수를 **미리 다 만들어 두지 않습니다.** 달라고 할 때마다 다음 수를 하나씩 계산해 줍니다.
그래서 10억 개짜리 `range` 도 순식간에 만들어지고 메모리도 거의 쓰지 않습니다.
''')

code('''
big = range(1000000000)      # 10억 개. 순식간에 만들어집니다
print(big)
print(len(big))
print(big[999])                 # 999번 수를 그때 계산해서 알려 줍니다
''')

md('''
2교시에 쓴 `enumerate()` 도 이터레이터를 돌려줍니다. 그대로 출력하면 내용이 보이지 않고, `list()` 로 감싸야 보입니다.
''')

code('''
print(enumerate(menus))             # 내용이 아니라 '이터레이터가 있다'는 표시만 나옵니다
print(list(enumerate(menus)))       # list() 로 끝까지 꺼내야 보입니다
''')

md(warn("`list(range(1000000000))` 은 실행하지 마세요", "`list()` 는 원소를 <b>전부 꺼내 메모리에 담습니다.</b> 10억 개를 담으려다 메모리가 모자라 브라우저 탭이 멈춥니다. 큰 범위는 `for` 문으로 <b>하나씩</b> 꺼내 쓰세요.")
   + "\n\n" + key("이터레이터 정리", "① `for` 문에 쓸 수 있는 자료가 <b>반복 가능한 자료</b>입니다: 리스트 · 튜플 · 문자열 · 딕셔너리 · 집합 · `range()`.<br>② <b>이터레이터</b>는 ‘다음 원소’를 하나씩 건네주는 책갈피입니다. `iter()` 로 만들고 `next()` 로 꺼냅니다.<br>③ 한 번 끝까지 간 이터레이터는 다시 쓸 수 없습니다.<br>④ `range()` · `enumerate()` 는 값을 미리 만들지 않고 <b>필요할 때 하나씩</b> 만듭니다. 내용을 보려면 `list()` 로 감쌉니다.<br>평소에는 `for` 문만 쓰면 됩니다. `iter()` 와 `next()` 를 직접 쓸 일은 드뭅니다."))

md('''
<details><summary><b>📎 더 알아보기 — 대괄호를 소괄호로 바꾸면: 제너레이터 식</b></summary>

리스트 컴프리헨션의 `[ ]` 를 `( )` 로 바꾸면 리스트를 만들지 않고 **하나씩 계산해 건네주는 이터레이터**가 됩니다. 이것을 제너레이터 식(generator expression)이라고 합니다.

```python
total = sum([n * n for n in range(1, 1000001)])   # 100만 개짜리 리스트를 만든 뒤 더합니다
total = sum(n * n for n in range(1, 1000001))     # 하나씩 계산하며 바로 더합니다. 리스트를 만들지 않습니다
```

결과는 같습니다. 두 번째가 메모리를 덜 씁니다. `sum()`, `max()`, `min()` 처럼 한 번만 훑으면 되는 곳에 씁니다.

</details>

## 3-3. 스택(stack) — 나중에 넣은 것을 먼저 꺼낸다

리스트는 어느 자리에든 넣고, 어느 자리에서든 꺼낼 수 있습니다. 여기에 **‘넣고 꺼내는 자리’에 규칙**을 두면 특정한 문제를 푸는 도구가 됩니다.
이렇게 자료를 담고 꺼내는 방식을 정한 것을 **자료구조(data structure)** 라고 합니다. 가장 기본이 되는 두 가지를 봅니다.

첫 번째는 **스택(stack)** 입니다. 식당에 **쌓아 둔 접시**를 떠올리세요. 새 접시는 맨 위에 올리고, 꺼낼 때도 맨 위에서 꺼냅니다.
그래서 **나중에 넣은 것이 먼저** 나옵니다. 이것을 후입선출(LIFO, Last In First Out)이라고 합니다.

| 스택이 하는 일 | 리스트로 쓰는 법 | 설명 |
|:---|:---|:---|
| 넣기 (push) | `stack.append(x)` | 맨 **뒤**에 넣기 |
| 꺼내기 (pop) | `stack.pop()` | 맨 **뒤**에서 꺼내고, 리스트에서 없앰 |
| 맨 위 보기 | `stack[-1]` | 꺼내지 않고 보기만 |
| 비었는가 | `if stack:` | 5주차 — 빈 리스트는 거짓 |

`append()` 는 5주차에 배웠습니다. 새로 나온 것은 `pop()` 하나입니다. **예상해 보기** — 아래 셀의 출력은?
''')

code('''
stack = []
stack.append("A")
stack.append("B")
stack.append("C")
print(stack)

print(stack.pop())     # 무엇이 나올까요?
print(stack.pop())
print(stack)
''')

md(boom("빈 스택에서 꺼내면?"))

code('''
empty_stack = []
empty_stack.pop()
''', raises=True)

md('''
`IndexError: pop from empty list` 는 ‘빈 리스트에서는 꺼낼 것이 없다’는 뜻입니다. 꺼내기 전에 `if stack:` 으로 비었는지 확인하면 됩니다.

### 예제 1 — 문자열 뒤집기

글자를 차례로 스택에 넣었다가 다시 꺼내면 **순서가 거꾸로** 됩니다. `while stack:` 은 ‘스택이 빌 때까지’입니다.
''')

code('''
word = "python"

stack = []
for ch in word:
    stack.append(ch)           # p, y, t, h, o, n 순서로 쌓습니다
print(stack)

reversed_word = ""
while stack:                   # 스택이 빌 때까지
    reversed_word += stack.pop()   # 맨 위(마지막 글자)부터 꺼냅니다
print(reversed_word)
''')

md('''
### 예제 2 — 괄호 짝 검사

`(3 + (4 * 5))` 처럼 괄호가 올바르게 짝지어졌는지 검사합니다. 코드 편집기가 ‘괄호가 안 닫혔다’고 알려 줄 때 하는 일입니다.

생각을 정리해 봅시다. 닫는 괄호 `)` 는 **가장 최근에 열린** `(` 와 짝이 됩니다. ‘가장 최근 것부터’이므로 스택이 딱 맞습니다.

1. `(` 를 만나면 스택에 넣는다.
2. `)` 를 만나면 스택에서 하나 꺼낸다. **꺼낼 것이 없으면** 짝이 없는 `)` 이므로 틀렸다.
3. 끝까지 본 뒤 스택에 **남은 것이 있으면** 닫지 않은 `(` 가 있으므로 틀렸다.

**예상해 보기** — 아래 식은 괄호가 맞을까요?
''')

code('''
expression = "(3 + (4 * 5)) - (2"

stack = []
is_balanced = True                 # 일단 맞다고 가정합니다
for ch in expression:
    if ch == "(":
        stack.append(ch)
    elif ch == ")":
        if stack:
            stack.pop()            # 짝이 되는 ( 를 꺼냅니다
        else:
            is_balanced = False    # 꺼낼 ( 가 없다 → 짝 없는 )
            break
if stack:                          # 끝났는데 ( 가 남아 있다
    is_balanced = False

print(expression, "→", is_balanced)
''')

md('''
`expression` 을 `"(3 + (4 * 5)) - (2)"` 와 `")3 + 4("` 로 바꿔 다시 실행해 보세요.
''' + "\n" + note("스택은 어디에 쓰일까", "<b>실행 취소(Ctrl+Z)</b> — 한 일을 차례로 쌓아 두고, 가장 최근 것부터 되돌립니다.<br><b>브라우저의 ‘뒤로 가기’</b> — 방문한 페이지를 쌓아 두고, 가장 최근 페이지부터 돌아갑니다.<br>모두 ‘<b>가장 최근 것부터</b>’ 처리하는 일입니다."))

practice("✏️ 실습 3-2", "브라우저 ‘뒤로 가기’", "약 4분",
         "`history` 는 방문한 페이지를 순서대로 쌓은 스택입니다. <b>맨 뒤</b>가 지금 보고 있는 페이지입니다. ‘뒤로 가기’를 누르면 지금 페이지가 스택에서 빠집니다.<br>‘뒤로 가기’를 <b>두 번</b> 누른 뒤, 지금 보고 있는 페이지를 `current_page` 에 넣으세요. `pop()` 과 `[-1]` 을 씁니다.",
         '''
history = ["네이버", "연세포털", "LearnUs", "유튜브"]

# 여기에 코드를 작성하세요


print(current_page, history)
''',
         'history == ["네이버", "연세포털"] and current_page == "연세포털"',
         '''
history = ["네이버", "연세포털", "LearnUs", "유튜브"]

history.pop()                  # 유튜브에서 뒤로
history.pop()                  # LearnUs에서 뒤로
current_page = history[-1]     # 맨 위를 보기만 합니다 (꺼내지 않음)

print(current_page, history)   # 연세포털 ['네이버', '연세포털']
''', raises=True)

md('''
## 3-4. 큐(queue) — 먼저 넣은 것을 먼저 꺼낸다

두 번째는 **큐(queue)** 입니다. 매표소 앞에 **줄 서기**를 떠올리세요. 새로 온 사람은 맨 뒤에 서고, 맨 앞사람부터 표를 삽니다.
그래서 **먼저 넣은 것이 먼저** 나옵니다. 이것을 선입선출(FIFO, First In First Out)이라고 합니다.

| 큐가 하는 일 | 리스트로 쓰는 법 | 설명 |
|:---|:---|:---|
| 넣기 (enqueue) | `queue.append(x)` | 맨 **뒤**에 넣기 |
| 꺼내기 (dequeue) | `queue.pop(0)` | 맨 **앞**(0번)에서 꺼내고, 리스트에서 없앰 |
| 맨 앞 보기 | `queue[0]` | 꺼내지 않고 보기만 |

스택과 다른 곳은 **꺼내는 자리** 하나입니다. `pop()` 은 맨 뒤, `pop(0)` 은 맨 앞입니다.

**예상해 보기** — 3-3의 스택 셀과 넣는 순서는 같습니다. 꺼내는 순서는?
''')

code('''
queue = []
queue.append("A")
queue.append("B")
queue.append("C")
print(queue)

print(queue.pop(0))     # 무엇이 나올까요?
print(queue.pop(0))
print(queue)
''')

md('''
| | 스택 | 큐 |
|:---|:---:|:---:|
| 비유 | 쌓아 둔 접시 | 줄 서기 |
| 넣는 곳 | 맨 뒤 `append(x)` | 맨 뒤 `append(x)` |
| 꺼내는 곳 | **맨 뒤** `pop()` | **맨 앞** `pop(0)` |
| 먼저 나오는 것 | 나중에 넣은 것 | 먼저 넣은 것 |

### 예제 1 — 은행 창구

기다리는 손님을 **온 순서대로** 처리합니다. 처리하는 중에 새 손님이 와도 순서가 지켜집니다.
''')

code('''
waiting = ["민수", "지영", "현우"]     # 맨 앞이 가장 먼저 온 손님
waiting.append("서연")                # 새 손님은 줄 맨 뒤로

order = 1
while waiting:                        # 줄이 빌 때까지
    customer = waiting.pop(0)         # 맨 앞 손님을 부릅니다
    print(f"{order}번째 손님: {customer}")
    order += 1
print("대기 손님이 없습니다")
''')

md('''
### 예제 2 — 조금씩 돌아가며 처리하기

프린터 한 대를 여러 사람이 씁니다. 한 사람의 긴 문서가 프린터를 오래 차지하지 않도록, **한 번에 2쪽씩만** 인쇄하고 남은 문서는 **줄 맨 뒤로** 다시 보냅니다.
‘앞에서 꺼내고, 덜 끝났으면 뒤에 다시 넣기’는 큐를 쓰는 대표적인 방법입니다.

**예상해 보기** — 가장 먼저 인쇄가 끝나는 문서는?
''')

code('''
jobs = [("보고서", 5), ("사진", 2), ("과제", 3)]     # (문서 이름, 남은 쪽수)

while jobs:
    name, pages = jobs.pop(0)                  # 맨 앞 문서를 꺼냅니다
    if pages > 2:
        print(f"{name}: 2쪽 인쇄, {pages - 2}쪽 남음 → 줄 맨 뒤로")
        jobs.append((name, pages - 2))         # 남은 쪽수와 함께 다시 줄을 섭니다
    else:
        print(f"{name}: {pages}쪽 인쇄, 완료!")
''')

md(note("큐는 어디에 쓰일까", "<b>프린터 인쇄 대기열</b>, <b>콜센터 대기</b>, <b>수강신청 대기 순번</b>, <b>메신저 메시지 전송</b> 등 ‘<b>온 순서대로</b>’ 처리해야 공정한 일에 씁니다. 컴퓨터가 여러 프로그램을 동시에 실행하는 것처럼 보이는 것도, 예제 2처럼 프로그램들을 조금씩 돌아가며 실행하기 때문입니다.") + '''

<details><summary><b>📎 더 알아보기 — 큐 전용 도구 <code>deque</code></b></summary>

`pop(0)` 으로 맨 앞을 꺼내면 뒤에 있던 원소가 모두 한 칸씩 앞으로 옮겨집니다. 줄 맨 앞사람이 빠지면 뒷사람이 모두 한 걸음씩 움직이는 것과 같습니다. 원소가 수십만 개가 되면 이 일이 느려집니다.

Python에는 양쪽 끝에서 빠르게 넣고 꺼낼 수 있는 `deque`(덱) 가 준비되어 있습니다.

```python
from collections import deque

queue = deque(["A", "B", "C"])
queue.append("D")          # 맨 뒤에 넣기
print(queue.popleft())     # 맨 앞에서 꺼내기 → A
print(queue)               # deque(['B', 'C', 'D'])
```

이 수업에서는 리스트의 `pop(0)` 으로 충분합니다.

</details>
''')

practice("✏️ 실습 3-3", "카페 주문 처리", "약 4분",
         "`orders` 는 카페에 들어온 주문 대기열입니다. 아래 일을 차례로 코드로 쓰세요.<br>① 새 주문 `\"스무디\"` 가 들어왔습니다. (맨 뒤에 넣기)<br>② 먼저 들어온 주문부터 <b>두 건</b>을 꺼내, 꺼낸 순서대로 `served` 리스트에 담습니다.",
         '''
orders = ["아메리카노", "라떼", "녹차"]
served = []

# 여기에 코드를 작성하세요


print("나간 주문:", served)
print("남은 주문:", orders)
''',
         'served == ["아메리카노", "라떼"] and orders == ["녹차", "스무디"]',
         '''
orders = ["아메리카노", "라떼", "녹차"]
served = []

orders.append("스무디")              # ① 새 주문은 맨 뒤로

for i in range(2):                   # ② 두 번 반복
    served.append(orders.pop(0))     #    맨 앞에서 꺼내 served 에 담기

print("나간 주문:", served)          # ['아메리카노', '라떼']
print("남은 주문:", orders)          # ['녹차', '스무디']
''')

md(key("3교시 정리", "① 리스트 컴프리헨션 `[식 for 변수 in 자료 if 조건]` 은 ‘빈 리스트 → 반복 → append’를 한 줄로 씁니다.<br>② 이터레이터는 다음 원소를 하나씩 건네주는 책갈피입니다. `for` 문이 안에서 씁니다. 한 번 지나가면 끝입니다.<br>③ <b>스택</b>은 나중에 넣은 것을 먼저 꺼냅니다. `append()` 와 `pop()`. 뒤집기 · 괄호 검사 · 되돌리기.<br>④ <b>큐</b>는 먼저 넣은 것을 먼저 꺼냅니다. `append()` 와 `pop(0)`. 대기열 · 순서대로 처리.<br>⑤ `while stack:` · `while queue:` 는 ‘빌 때까지 반복’입니다."))

# ═════════════════════════ 주차 정리 ═════════════════════════
md('''
# 6주차 정리

| 개념 | 한 줄 요약 |
|:---|:---|
| **while 문** | 조건이 참인 동안 반복. 시작값 · 조건 · 변화를 챙긴다 |
| **for 문** | 자료의 원소를 하나씩 꺼내며 반복. `for 변수 in 자료:` |
| **range()** | `range(시작, 끝, 간격)`. 끝 번호는 들어가지 않는다 |
| **break / continue** | 반복을 끝낸다 / 이번 차례만 건너뛴다 |
| **반복 패턴** | 누적 `total += x`, 개수 세기 `count += 1`, 최댓값 찾기, 단어 수 세기 |
| **리스트 컴프리헨션** | `[식 for 변수 in 자료 if 조건]` — 바꿔 담기, 골라 담기 |
| **이터레이터** | 다음 원소를 하나씩 건네주는 책갈피. `iter()`, `next()` |
| **스택** | 나중에 넣은 것 먼저. `append()` · `pop()` |
| **큐** | 먼저 넣은 것 먼저. `append()` · `pop(0)` |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| 무한 반복 | 조건이 영원히 참이라 끝나지 않는다 (오류 메시지 없음) | `n += 1` 을 빠뜨린 `while` |
| `KeyboardInterrupt` | 사람이 실행을 멈췄다 | ■ 버튼을 눌렀을 때 |
| `StopIteration` | 이터레이터에 더 꺼낼 것이 없다 | 끝난 뒤 `next(it)` |
| `IndexError` | 빈 리스트에서 꺼내려 했다 | 빈 스택에서 `pop()` |

''' + key("오늘의 한 문장", "<b>반복문</b>으로 같은 일을 되풀이하고, 넣고 꺼내는 순서에 규칙을 둔 <b>스택과 큐</b>로 문제를 푼다.") + f'''

<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 함수 (구조적 프로그래밍)</b><br>
오늘 만든 소수 판별, 괄호 검사 같은 코드에 <b>이름을 붙여</b> 필요할 때마다 불러 쓰는 방법을 배웁니다.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 내용을 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
''')

# ═════════════════════════ 과제 ═════════════════════════
FIRST_HW_CELL = len(CELLS)

md(f'''
# 6주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">4 ~ 6주차 종합 코딩 문제</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>4주차(변수 · 문자열), 5주차(리스트 · 딕셔너리 · if 문), 6주차(반복문 · 스택 · 큐)의 내용만으로 풀 수 있습니다</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 변수 이름(`average`, `encrypted` 등)을 바꾸지 마세요. 점검 셀이 그 이름을 찾습니다.<br>③ 점검 결과만 맞추려고 답을 직접 써넣지 마세요(예: `result = 14`). <b>자료가 바뀌어도 옳게 동작하는 코드</b>를 씁니다.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다.<br>⑤ 막히면 먼저 <b>한국어로 순서를 적어 보세요.</b> 3주차의 의사코드(pseudo code)입니다. 그다음에 한 줄씩 Python으로 옮깁니다."))

practice("📝 과제 1", "성적 처리", "",
         "`scores` 는 학생 이름을 키로, 점수를 값으로 담은 딕셔너리입니다. 반복문으로 아래 세 가지를 구하세요.<br>① 평균 점수 → `average`<br>② 점수가 가장 높은 학생의 <b>이름</b> → `top_student`<br>③ 학점별 인원수 → `grade_count`. 기준은 90점 이상 A, 80점 이상 B, 70점 이상 C, 60점 이상 D, 그 밖은 F입니다. 해당 학생이 없는 학점도 `0` 으로 남겨 둡니다.<br>힌트: `scores.items()`, 실습 2-2(최댓값 찾기), 5주차의 `if` - `elif` - `else`.",
         '''
scores = {"김연세": 88, "이미래": 95, "박원주": 72, "최하늘": 59, "정바다": 81, "한솔": 67}
grade_count = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

# 여기에 코드를 작성하세요


print(f"평균: {average:.1f}점")
print(f"최고점 학생: {top_student}")
print(grade_count)
''',
         'abs(average - 77.0) < 1e-6 and top_student == "이미래" and grade_count == {"A": 1, "B": 2, "C": 1, "D": 1, "F": 1}',
         '''
scores = {"김연세": 88, "이미래": 95, "박원주": 72, "최하늘": 59, "정바다": 81, "한솔": 67}
grade_count = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

total = 0
top_student = ""
top_score = -1
for name, score in scores.items():
    total += score                  # ① 누적
    if score > top_score:           # ② 최댓값 찾기 — 이름도 함께 기억
        top_score = score
        top_student = name
    if score >= 90:                 # ③ 학점 정하기
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    grade_count[grade] += 1
average = total / len(scores)

print(f"평균: {average:.1f}점")
print(f"최고점 학생: {top_student}")
print(grade_count)
''', raises=True, show_answer=False)

SECRET = caesar("computational thinking", 3)
practice("📝 과제 2", "카이사르 암호", "",
         "2주차에 암호 기계 에니그마 이야기를 했습니다. 그보다 2천 년 앞선 로마의 카이사르는 <b>글자를 알파벳 순서로 몇 칸씩 밀어</b> 편지를 썼습니다. 3칸 밀면 `a` → `d`, `b` → `e` 가 되고, 끝을 넘어가면 처음으로 돌아와 `x` → `a`, `z` → `c` 가 됩니다.<br>① `message` 의 <b>영어 소문자만</b> `shift` 칸 밀어 암호문 `encrypted` 를 만드세요. 공백 같은 다른 글자는 그대로 둡니다.<br>② 같은 방법으로 만든 암호문 `secret` 을 원래 문장으로 되돌려 `decrypted` 에 넣으세요.<br>힌트: 4주차의 `ord()` · `chr()`. `ord(ch) - ord(\"a\")` 는 `a` 가 0, `z` 가 25인 번호입니다. ‘끝을 넘으면 처음으로’는 나머지 연산 `% 26` 으로 만들 수 있습니다.",
         f'''
message = "hello world"
secret = "{SECRET}"
shift = 3

# 여기에 코드를 작성하세요


print(encrypted)
print(decrypted)
''',
         'encrypted == "khoor zruog" and decrypted == "computational thinking"',
         f'''
message = "hello world"
secret = "{SECRET}"
shift = 3

encrypted = ""
for ch in message:
    if "a" <= ch <= "z":
        number = (ord(ch) - ord("a") + shift) % 26      # 0 ~ 25 번호로 바꿔 밀고, 넘치면 처음으로
        encrypted += chr(number + ord("a"))
    else:
        encrypted += ch

decrypted = ""
for ch in secret:
    if "a" <= ch <= "z":
        number = (ord(ch) - ord("a") - shift) % 26      # 반대 방향으로 밉니다
        decrypted += chr(number + ord("a"))
    else:
        decrypted += ch

print(encrypted)
print(decrypted)
''', raises=True, show_answer=False)

practice("📝 과제 3", "스택으로 계산기 만들기 — 후위 표기식", "",
         "우리는 `(1 + 2) * 4` 처럼 연산자를 숫자 <b>사이</b>에 씁니다. 연산자를 숫자 <b>뒤</b>에 쓰는 방법도 있습니다. `1 2 + 4 *` 처럼 씁니다. 이것을 후위 표기식이라고 합니다. 괄호와 우선순위가 필요 없어서 컴퓨터가 계산하기 쉽습니다.<br>스택으로 계산하는 방법은 다음과 같습니다. 식을 공백으로 쪼개 앞에서부터 하나씩 봅니다.<br>① 숫자이면 `int()` 로 바꿔 스택에 넣는다.<br>② 연산자(`+`, `-`, `*`)이면 스택에서 <b>두 개</b>를 꺼내 계산하고, 결과를 다시 스택에 넣는다. <b>먼저 꺼낸 것이 오른쪽</b> 수입니다. 뺄셈에서 순서가 중요합니다.<br>③ 끝나면 스택에 남은 하나가 답이다.<br>`expression` 을 계산한 결과를 `result` 에 넣으세요. 이 식은 `5 + (1 + 2) * 4 - 3` 과 같습니다.",
         '''
expression = "5 1 2 + 4 * + 3 -"

# 여기에 코드를 작성하세요


print(result)
''',
         "result == 14",
         '''
expression = "5 1 2 + 4 * + 3 -"

stack = []
for token in expression.split():
    if token in ["+", "-", "*"]:
        right = stack.pop()          # 먼저 꺼낸 것이 오른쪽
        left = stack.pop()
        if token == "+":
            stack.append(left + right)
        elif token == "-":
            stack.append(left - right)
        else:
            stack.append(left * right)
    else:
        stack.append(int(token))
result = stack.pop()

print(result)
''', raises=True, show_answer=False)

practice("📝 과제 4", "큐로 푸는 수건돌리기", "",
         "1번부터 `n` 번까지 `n` 명이 번호 순서대로 둥글게 앉아 있습니다. 1번부터 시계 방향으로 세어 <b>`k` 번째 사람이 원에서 빠집니다.</b> 빠진 사람의 다음 사람부터 다시 세어 또 `k` 번째 사람이 빠집니다. 한 명이 남을 때까지 되풀이합니다.<br>빠진 사람의 번호를 순서대로 `order` 리스트에, 마지막까지 남은 사람의 번호를 `survivor` 에 넣으세요.<br>힌트: 둥글게 앉은 사람들을 큐로 생각합니다. 맨 앞사람을 꺼내 <b>맨 뒤로 다시 보내기</b>를 `k - 1` 번 하면 `k` 번째 사람이 맨 앞에 옵니다. 3-4의 프린터 예제를 참고하세요.<br>`n = 7`, `k = 3` 이면 3번이 가장 먼저 빠지고, 그다음은 6번입니다.",
         '''
n = 7
k = 3
queue = list(range(1, n + 1))     # [1, 2, 3, 4, 5, 6, 7]
order = []

# 여기에 코드를 작성하세요


print("빠진 순서:", order)
print("마지막 남은 사람:", survivor)
''',
         "order == [3, 6, 2, 7, 5, 1] and survivor == 4",
         '''
n = 7
k = 3
queue = list(range(1, n + 1))     # [1, 2, 3, 4, 5, 6, 7]
order = []

while len(queue) > 1:
    for i in range(k - 1):
        queue.append(queue.pop(0))     # 앞사람을 맨 뒤로 보내기를 k - 1 번
    order.append(queue.pop(0))         # k 번째 사람이 빠진다
survivor = queue[0]

print("빠진 순서:", order)
print("마지막 남은 사람:", survivor)
''', raises=True, show_answer=False)

practice("📝 과제 5", "100 이하의 소수 모두 찾기 (도전)", "",
         "2 이상 100 이하의 소수를 작은 것부터 모두 찾아 리스트 `primes` 에 담으세요. 방법은 자유입니다.<br>방법 1: 실습 1-3의 소수 판별을 2부터 100까지 반복합니다(반복문 안의 반복문).<br>방법 2: 고대 그리스의 에라토스테네스가 쓴 방법입니다. 2부터 100까지 적어 놓고, 2의 배수(2 제외)를 지우고, 남은 수 중 다음 수인 3의 배수(3 제외)를 지우고… 를 되풀이하면 소수만 남습니다.",
         '''
primes = []

# 여기에 코드를 작성하세요


print(primes)
print(len(primes), "개")
''',
         "primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]",
         '''
# 방법 1 — 수마다 소수인지 판별 (반복문 안의 반복문)
primes = []
for n in range(2, 101):
    is_prime = True
    for i in range(2, n):
        if n % i == 0:
            is_prime = False
            break
    if is_prime:
        primes.append(n)

print(primes)
print(len(primes), "개")

# 방법 2 — 에라토스테네스의 체
is_candidate = [True] * 101              # is_candidate[n] 이 True 면 n 은 아직 지워지지 않은 수
sieve_primes = []
for n in range(2, 101):
    if is_candidate[n]:
        sieve_primes.append(n)
        for multiple in range(n * 2, 101, n):
            is_candidate[multiple] = False
print(sieve_primes == primes)
''', show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다.<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
def to_nb(cells):
    out, seen = [], set()
    for i, (ctype, src, meta) in enumerate(cells):
        cid = hashlib.md5(f"w6-{i}-{src}".encode("utf-8")).hexdigest()[:8]
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
    cells = [("markdown", "# 컴퓨팅사고 6주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 강의 노트북 `" + LECTURE + "` 맨 끝 ‘6주차 과제’의 정답 예시입니다. 각 셀은 혼자서 실행됩니다.", {})]
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

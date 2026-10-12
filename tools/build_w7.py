import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 7주차 노트북(강의용 + 과제 정답) 생성 스크립트 — build_w6.py 를 복제해 작성
# 사용: python build_w7.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w7.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
LECTURE = "컴퓨팅사고_7주차_함수.ipynb"
HW_SOL = "컴퓨팅사고_7주차_과제정답.ipynb"

# ───────────────────────── HTML 상자 (6주차 노트북과 같은 값) ─────────────────────────
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
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w7.py 가 사용


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


def practice(label, title, minutes, body, skeleton, test, solution, raises=False, heading=None, show_answer=True,
             extra=None, extra_raises=False):
    """✏️ 상자 → 작성용 셀 → (추가 셀) → 🔍 점검 셀 → 💡 정답(접힘)
    extra: 작성용 셀 뒤에 붙는 고정 코드 셀(예: 모듈 import). 학생이 고치지 않는다."""
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
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 7주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">함수 — 코드에 이름을 붙이다</div>
<div style="font-size:1.25em;margin-top:6px;">구조적 프로그래밍 &nbsp;·&nbsp; 함수의 정의와 호출 &nbsp;·&nbsp; 변수의 범위 &nbsp;·&nbsp; 모듈과 사용자 정의 라이브러리</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>
</div>
''')

md('''
# 7주차 학습 안내

지난주까지 순차 · 선택(`if`) · 반복(`while`, `for`)으로 **절차**를 쓸 수 있게 되었습니다.
이번 주에는 그 절차에 **이름을 붙여** 필요할 때마다 부르는 방법을 배웁니다. 프로그램이 커져도 사람이 감당할 수 있게 하는 첫 번째 도구, **함수**입니다.

| 교시 | 주제 | 핵심 질문 |
|:---:|:---|:---|
| **1교시** | 함수의 정의와 호출 | 같은 코드를 세 번 써야 한다. 복사해서 붙이면 되는 것 아닌가? |
| **2교시** | 함수를 잘 쓰기 — 매개변수 · 반환 · 변수의 범위 | 함수 안에서 만든 변수는 밖에서 보일까? |
| **3교시** | 모듈과 사용자 정의 라이브러리 | 오늘 만든 함수를 다음 주 노트북에서도 쓰려면? |

**오늘 수업을 마치면**

1. `def` 로 함수를 정의하고 호출할 수 있으며, 매개변수 · 인자 · 반환값이 무엇인지 설명할 수 있습니다.
2. `print` 와 `return` 의 차이를 알고, 기본값 · 키워드 인자 · 여러 값 반환을 쓸 수 있습니다.
3. 지역 변수와 전역 변수를 구분하고, 함수가 함수를 부를 때 무슨 일이 일어나는지 설명할 수 있습니다.
4. `import` 로 표준 모듈(`math`, `random`)을 쓰고, 내 함수를 `.py` 파일에 모아 모듈로 만들 수 있습니다.

''' + key("이 노트북을 읽는 법", "회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요. 예상과 다를 때가 가장 많이 배우는 순간입니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 정답 예시는 접혀 있으니 먼저 스스로 풀어 보세요.<br>노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다. 4주차부터 오늘까지 배운 내용으로 푸는 문제입니다."))

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · 함수의 정의와 호출\n\n" + period(1, "코드에 이름을 붙이다 — 함수의 정의와 호출", [
    "같은 코드를 복사해 붙이면 무엇이 문제인지 설명한다",
    "def 로 함수를 정의하고, 이름으로 호출한다",
    "매개변수로 값을 넣고 return 으로 결과를 돌려받는다",
    "print 와 return 의 차이를 설명한다",
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
# import 때마다 캐시를 비우는 작은 장치를 끼워 둡니다. 3교시 '나만의 모듈'에서 씁니다.
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
## 1-1. 같은 코드를 세 번? — 복사해서 붙이면 생기는 일

6주차 실습 1-3에서 91이 소수인지 판별했습니다. 그 코드입니다.
''')

code('''
n = 91
is_prime = True
i = 2
while i < n:
    if n % i == 0:
        is_prime = False
        break
    i += 1
print(n, is_prime)
''')

md('''
이번에는 91, 97, 1000003 **세 수**를 모두 검사해야 한다고 합시다. 위 셀을 세 번 복사해서 `n` 만 바꾸면 될까요? 되기는 합니다. 그런데 이런 일이 생깁니다.

- 코드가 **세 배**로 길어집니다. 읽을 것은 많은데 새로운 내용은 없습니다.
- 검사 방법을 고치면 **세 군데를 모두** 고쳐야 합니다. 한 곳만 빠뜨리면 버그입니다.
- 읽는 사람은 세 덩어리가 **정말 같은 코드인지** 매번 눈으로 비교해야 합니다.
- ‘소수인지 검사한다’는 **의도**가 코드 어디에도 적혀 있지 않습니다.

3주차에 배운 **분해(decomposition)** 를 떠올리세요. 큰 문제를 작은 조각으로 나누고, 각 조각에 **이름**을 붙이면 사람도 컴퓨터도 읽기 쉬워집니다.
코드 조각에 이름을 붙인 것이 **함수(function)** 입니다. 오늘 1교시가 끝나면 위 코드는 이렇게 됩니다.

```python
print(is_prime(91), is_prime(97), is_prime(1000003))
```

### 구조적 프로그래밍 — 쪼개고, 이름 붙이고, 모아 둔다

프로그램을 작은 부분으로 쪼개어 관리하기 쉽게 만드는 방식을 **구조적 프로그래밍(structured programming)** 이라고 합니다. 재료는 네 가지입니다.

| 재료 | 하는 일 | 배우는 때 |
|:---|:---|:---|
| 순차 · 선택 · 반복 | 절차를 쓰는 세 가지 구조 (3주차 뵘-야코피니 정리) | 4 ~ 6주차 |
| **함수** | 되풀이되는 코드 덩어리에 이름을 붙여 한 줄로 부른다 | **오늘 1 · 2교시** |
| **모듈** | 관련 있는 함수들을 파일 하나에 모아 두고 가져다 쓴다 | **오늘 3교시** |
| 클래스 | 데이터와 함수를 한 묶음으로 | 9주차 |
''')

md(note("goto 와 스파게티 코드", "1960년대까지는 `goto` 로 프로그램의 아무 줄로나 점프할 수 있었습니다. 흐름이 얽히고설켜 ‘스파게티 코드’라 불렸습니다. 세 가지 제어 구조와 함수만으로 프로그램을 짜자고 한 사람이 다익스트라(Dijkstra, 1968)입니다. Python 에는 아예 `goto` 가 없습니다."))

md('''
## 1-2. 함수 — 이미 많이 써 왔습니다

4주차부터 매일 쓴 `print()`, `len()`, `input()`, `int()`, `range()`, `sum()` 이 모두 함수입니다. 이름 뒤에 **괄호**가 붙어 있으면 함수를 **부르는(호출하는)** 것입니다.

함수는 수학의 함수와 닮았습니다. $f(x) = 2x + 1$ 에 3을 **넣으면** 정해진 계산을 하고 7이 **나옵니다**. `len("Hello")` 도 같은 모양입니다. 문자열을 넣으면 5가 나옵니다.

중요한 것은 `len()` 이 **어떻게** 글자를 세는지 몰라도 쓸 수 있다는 점입니다. **무엇을 넣으면 무엇이 나오는지**만 알면 됩니다. 전문가에게 일을 맡기는 것과 같습니다. 요청하고, 결과만 받습니다. 이렇게 안을 모른 채 쓰는 것을 **블랙박스(black box)** 로 다룬다고 합니다.

지금까지는 남이 만든 함수를 **쓰기만** 했습니다. 오늘은 내가 함수를 **만듭니다.** 만든 뒤에는 `print()` 처럼 이름만 부르면 됩니다.

## 1-3. 함수 정의하기 — `def`

```
def 함수이름(매개변수1, 매개변수2):
    실행할 문장
    실행할 문장
    return 결과값
```

| 조각 | 뜻 |
|:---|:---|
| `def` | ‘정의한다(define)’는 키워드. 이 줄부터 함수가 시작됩니다 |
| `함수이름` | 변수 이름과 같은 규칙입니다. 소문자와 밑줄. 보통 **동사**로 시작합니다: `get_score`, `is_prime`, `print_menu` |
| `( 매개변수 )` | 함수가 **받을 값**을 담을 변수 이름. 없으면 빈 괄호 `()` 입니다. 괄호는 생략할 수 없습니다 |
| `:` 와 들여쓰기 | 콜론 다음 줄부터 **들여쓴 부분**이 함수의 몸통입니다. `if` · `while` 과 같은 규칙입니다 |
| `return` | 결과를 **돌려주고 함수를 끝냅니다.** 돌려줄 것이 없으면 생략해도 됩니다 |

가장 단순한 함수부터 만들어 봅니다. 받는 값도, 돌려주는 값도 없습니다.

**예상해 보기** — 아래 셀을 실행하면 화면에 무엇이 나올까요?
''')

code('''
def say_hello():
    print("안녕하세요!")
    print("컴퓨팅 사고 7주차입니다.")
''')

md('''
**아무것도 나오지 않습니다.** 오류도 아닙니다. `def` 는 “이 이름을 부르면 이렇게 하겠다”는 **약속**만 합니다. 몸통은 아직 실행되지 않았습니다.

레시피를 **적어 두는 것**(정의)과 레시피대로 **요리하는 것**(호출)은 다릅니다. 적어 두기만 하면 배가 부르지 않습니다.

실제로 실행되는 순간은 이름 뒤에 괄호를 붙여 **호출(call)** 할 때입니다. 한 번 정의하면 몇 번이든 부를 수 있습니다.
''')

code('''
say_hello()
say_hello()
''')

md(key("정의는 약속, 호출은 실행", "① `def` 는 함수를 <b>기억</b>시킬 뿐 실행하지 않습니다. 정의만 한 셀이 조용히 끝나는 것은 정상입니다.<br>② `이름()` 으로 <b>호출</b>해야 몸통이 실행됩니다.<br>③ 호출은 정의보다 <b>뒤에</b> 와야 합니다. 정의하기 전에 부르면 `NameError` 입니다."))

md('''
## 1-4. 호출하면 흐름이 ‘다녀옵니다’

**예상해 보기** — A, B, C 는 어떤 순서로 출력될까요?
''')

code('''
def middle():
    print("B")

print("A")
middle()
print("C")
''')

md('''
컴퓨터는 위에서 아래로 갑니다. `def middle():` 은 기억만 하고 지나갑니다. `print("A")` 를 실행하고, `middle()` 을 만나면 **함수의 몸통으로 갔다가**, 몸통이 끝나면 **호출한 자리로 돌아와** 그다음 줄 `print("C")` 를 이어 갑니다.

호출은 ‘잠시 다녀오기’입니다. 어디로 돌아갈지를 컴퓨터가 어떻게 기억하는지는 2교시에서 봅니다. 6주차의 **스택**이 다시 나옵니다.

## 1-5. 값을 넣어 주기 — 매개변수와 인자

같은 일을 **다른 값**으로 하고 싶을 때, 괄호 안으로 값을 넘깁니다.
''')

code('''
def greet(name):
    print(f"{name}님, 안녕하세요!")

greet("지민")
greet("민수")
''')

md('''
용어 두 개를 구분합니다. ‘자리’와 ‘값’입니다.

| 용어 | 어디에 | 무엇 | 예 |
|:---|:---|:---|:---|
| **매개변수**(parameter) | 함수 **정의** 쪽 괄호 안 | 받을 값을 담을 **변수 이름** | `name` |
| **인자**(argument) | 함수 **호출** 쪽 괄호 안 | 실제로 넘기는 **값** | `"지민"` |

호출하면 인자가 매개변수에 **순서대로** 대입됩니다. `greet("지민")` 은 몸통이 실행되기 전에 `name = "지민"` 이 먼저 일어나는 것과 같습니다.

매개변수가 둘이면 인자도 둘, 순서도 같아야 합니다.
''')

code('''
def greet(name, year):
    print(f"{year}학년 {name}님, 환영합니다")

greet("지민", 1)
''')

md(boom("인자를 하나만 주면?"))

code('''
greet("지민")
''', raises=True)

md('''
`TypeError: greet() missing 1 required positional argument: 'year'` — “꼭 필요한 인자 `year` 가 하나 빠졌다”는 안내입니다. 정의의 괄호와 호출의 괄호를 맞춰 보면 됩니다.

오류보다 무서운 것은 **조용히 틀리는 것**입니다. `greet(1, "지민")` 은 오류 없이 “지민학년 1님”이라는 엉뚱한 문장을 만듭니다. 컴퓨터는 순서만 봅니다. 인자 순서는 늘 정의와 맞춰 보세요.

## 1-6. 결과를 돌려주기 — `return`

`print` 는 화면에 보여 줄 뿐입니다. 결과를 **다른 계산에 쓰려면** 함수가 값을 **돌려주어야** 합니다. 그 일을 `return` 이 합니다.
''')

code('''
def add(a, b):
    return a + b

result = add(3, 5)
print(result)
print(add(10, 20) * 2)
''')

md('''
`return` 은 두 가지 일을 합니다.

1. **값을 돌려줍니다.** `add(3, 5)` 라는 호출식 자체가 `8` 이 됩니다. 그래서 변수에 담거나(`result = add(3, 5)`), 다른 식에 바로 쓸 수 있습니다(`add(10, 20) * 2`). 수학에서 $f(3)$ 을 7로 바꿔 읽는 것과 같습니다.
2. **함수를 끝냅니다.** `return` 을 만나면 그 아래 줄은 실행하지 않고 즉시 돌아갑니다. 반복문 안에서 만나면 반복도 함께 끝납니다.

### `print` 와 `return` 은 다릅니다 — 가장 많이 헷갈리는 곳

**예상해 보기** — 아래 셀의 두 번째 `print` 는 무엇을 출력할까요?
''')

code('''
def add_print(a, b):
    print(a + b)

result = add_print(3, 5)
print(result)
''')

md('''
`8` 다음에 **`None`** 이 나옵니다. `add_print` 는 화면에 8을 보여 주기만 했을 뿐, 아무것도 **건네주지** 않았습니다. 돌려주는 값이 없는 함수의 호출식은 `None`(‘없음’을 뜻하는 값)이 됩니다. 그래서 `result` 에 `None` 이 담겼습니다. `result + 1` 을 하면 `TypeError` 가 납니다.

| | `print` | `return` |
|:---|:---|:---|
| 비유 | 요리를 **보여 준다** | 요리를 접시에 담아 **건네준다** |
| 결과가 가는 곳 | 화면 (사람에게) | 호출한 자리 (프로그램에게) |
| 그다음 | 지나가면 끝 | 변수에 담거나 다른 계산에 쓴다 |

함수의 기본형은 `return` 쪽입니다. 출력이 `None` 으로 나오면 **`return` 을 빠뜨렸는지** 먼저 의심하세요.

### 입력과 출력의 네 가지 조합

매개변수(입력)와 `return`(출력)은 각각 있어도 되고 없어도 됩니다. 함수마다 필요한 모양이 다릅니다.
''')

code('''
def add(a, b):          # 입력 O, 출력 O — 계산해서 돌려준다
    return a + b

def greet(name):        # 입력 O, 출력 X — 받은 값으로 '일'만 한다
    print(f"{name}님, 안녕하세요!")

def ask_name():         # 입력 X, 출력 O — 밖에서 값을 얻어 와 돌려준다
    return input("이름: ")

def say_hello():        # 입력 X, 출력 X — 정해진 일을 할 뿐
    print("안녕하세요!")

print(add(2, 3))
greet("지민")
say_hello()
''')

md(key("함수를 만들기 전에 스스로 묻기", "“이 함수는 <b>무엇을 받고</b>(매개변수), <b>무엇을 하고</b>(몸통), <b>무엇을 돌려주나</b>(return)?” — 답이 정해지면 `def` 한 줄이 써집니다. 3주차 ‘좋은 알고리듬의 조건’ 중 <b>입력 · 출력</b>이 함수에서도 그대로입니다.<br>결과를 함수 밖에서 써야 한다면 `return`. `print` 는 사람에게 보여 주는 일, `return` 은 프로그램에게 건네주는 일입니다."))

md('''
## 1-7. 돌아와서 — 소수 판별에 이름 붙이기

1-1의 코드를 함수로 만듭니다. 6주차의 ‘일단 `True` 로 놓고 `break`’ 가 함수 안에서는 더 단순해집니다. `return` 이 `break` 역할까지 하기 때문입니다.
''')

code('''
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False    # 나누어떨어지면 바로 끝 — 아래 줄은 실행되지 않습니다
    return True             # 반복이 끝까지 돌았다면 나눈 수가 없었다 → 소수

print(is_prime(91), is_prime(97), is_prime(1000003))
if is_prime(2027):
    print("2027은 소수입니다")
''')

md('''
무엇이 달라졌는지 보세요.

- `is_prime = True` 깃발 변수가 **사라졌습니다.** 나누어떨어지는 순간 `return False` 로 함수째 끝납니다.
- 반복이 끝까지 돌았다면 나눈 수가 없었다는 뜻입니다. 그래서 마지막 줄이 `return True` 입니다.
- 호출하는 쪽은 `is_prime(97)` 한 줄입니다. **어떻게** 검사하는지는 몰라도 됩니다.
- 참 · 거짓을 돌려주는 함수는 `is_…` 로 이름 짓는 관습이 있습니다. `if is_prime(n):` 이 영어 문장처럼 읽힙니다.
''')

md(key("1-3 ~ 1-7 정리", "① `def 이름(매개변수):` 몸통 `return 결과` — 이 네 조각이 함수의 전부입니다.<br>② 정의는 약속, 호출은 실행. 호출하면 함수에 다녀와서 다음 줄을 이어 갑니다.<br>③ 매개변수는 정의 쪽 ‘빈 자리’, 인자는 호출 쪽 ‘채우는 값’. 순서대로 짝이 맞습니다.<br>④ `return` 은 값을 돌려주고 함수를 끝냅니다. 없으면 `None`.<br>⑤ 함수 안의 `return` 은 ‘답이 나오는 즉시 끝’ — 깃발 변수와 `break` 가 필요 없어집니다."))

# ── 1교시 실습 ──
practice("✏️ 실습 1-1", "섭씨 → 화씨 변환 함수", "약 3분",
         "섭씨 온도를 받아 화씨 온도를 <b>돌려주는</b> 함수 `celsius_to_fahrenheit(celsius)` 를 정의하세요. 공식은 4주차의 `celsius * 9 / 5 + 32` 입니다.<br>`print` 가 아니라 `return` 입니다. `celsius_to_fahrenheit(100)` 은 `212.0` 을 돌려주어야 합니다.",
         '''
# 여기에 함수를 정의하세요


print(celsius_to_fahrenheit(100))
print(celsius_to_fahrenheit(36.5))
''',
         "abs(celsius_to_fahrenheit(100) - 212) < 1e-6 and abs(celsius_to_fahrenheit(-40) + 40) < 1e-6",
         '''
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32

print(celsius_to_fahrenheit(100))      # 212.0
print(celsius_to_fahrenheit(36.5))     # 97.7
''', raises=True, heading="## 1교시 실습")

practice("✏️ 실습 1-2", "윤년 판별 함수", "약 5분",
         "연도를 받아 윤년이면 `True`, 아니면 `False` 를 돌려주는 `is_leap_year(year)` 를 정의하세요. 윤년의 규칙은 세 가지입니다.<br>① 4로 나누어떨어지면 윤년입니다. ② 그중 100으로 나누어떨어지면 윤년이 <b>아닙니다.</b> ③ 그중 400으로 나누어떨어지면 다시 윤년입니다.<br>1900 → `False`, 2000 → `True`, 2024 → `True`, 2026 → `False`. 5주차의 `if` - `elif` - `else`, 또는 `and` · `or` 로 한 줄에 쓸 수도 있습니다.",
         '''
# 여기에 함수를 정의하세요


for year in [1900, 2000, 2024, 2026]:
    print(year, is_leap_year(year))
''',
         "[is_leap_year(y) for y in [1900, 2000, 2024, 2026, 2100, 2400]] == [False, True, True, False, False, True]",
         '''
def is_leap_year(year):
    if year % 400 == 0:        # ③ 400 의 배수 → 윤년
        return True
    elif year % 100 == 0:      # ② 100 의 배수 → 윤년 아님
        return False
    elif year % 4 == 0:        # ① 4 의 배수 → 윤년
        return True
    else:
        return False

for year in [1900, 2000, 2024, 2026]:
    print(year, is_leap_year(year))

# 한 줄로 쓰면:
#     return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
''', raises=True)

practice("✏️ 실습 1-3", "2 ~ 50 의 소수 모두 모으기", "약 4분",
         "1-7의 `is_prime(n)` 을 이 셀에 그대로 정의한 뒤, `for` 문으로 2부터 50까지 돌며 <b>소수만</b> 리스트 `primes` 에 담으세요. 6주차의 ‘빈 리스트 → 반복 → `append()`’ 패턴입니다.<br>길이는 15개, 마지막 원소는 47입니다. 리스트 컴프리헨션으로 한 줄에 쓸 수도 있습니다.",
         '''
# 여기에 is_prime 을 정의하세요


primes = []
# 여기에 for 문을 작성하세요


print(primes)
print(len(primes), "개")
''',
         "primes == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47] and is_prime(1000003) and not is_prime(1000001)",
         '''
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

primes = []
for n in range(2, 51):
    if is_prime(n):
        primes.append(n)

print(primes)
print(len(primes), "개")      # 15 개

# 컴프리헨션으로:  primes = [n for n in range(2, 51) if is_prime(n)]
''')

md(key("1교시 정리", "① 같은 코드가 두 번 나오면 이름을 붙일 때입니다. 함수는 <b>이름 붙은 코드 묶음</b>입니다.<br>② `def` 로 정의하고 `이름()` 으로 호출합니다. 정의는 약속, 호출은 실행.<br>③ 매개변수로 값을 받고 `return` 으로 결과를 돌려줍니다. 호출식은 돌려준 값으로 바뀝니다.<br>④ `print` 는 보여 주기, `return` 은 건네주기. 결과를 밖에서 쓰려면 `return`.<br>⑤ 오늘의 질문에 대한 답 — 복사해서 붙이지 않습니다. <b>한 번 정의하고 여러 번 부릅니다.</b> 고칠 일이 생기면 한 곳만 고칩니다.") + "\n\n" + BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · 함수를 잘 쓰기\n\n" + period(2, "매개변수 · 반환 · 변수의 범위", [
    "기본값 매개변수와 키워드 인자로 호출을 편하게 만든다",
    "여러 값을 튜플로 돌려주고 풀어 받는다",
    "지역 변수와 전역 변수를 구분한다",
    "함수가 함수를 부를 때 무슨 일이 일어나는지 설명하고, 프로그램을 함수로 쪼갠다",
]))

md('''
## 2-1. 기본값 매개변수 — 안 주면 이 값으로

매개변수에 `=` 로 **기본값**을 적어 두면, 호출할 때 그 인자를 생략할 수 있습니다.
''')

code('''
def greet(name, greeting="안녕하세요"):
    print(f"{name}님, {greeting}!")

greet("지민")                  # greeting 을 생략 → 기본값
greet("지민", "반갑습니다")     # 직접 주면 그 값
''')

md('''
이미 써 본 것입니다. 6주차의 `print(n, end=" ")` 에서 `end` 의 기본값은 줄바꿈 `"\\n"` 입니다. 그래서 평소에는 안 적어도 줄이 바뀝니다. `range(10)` 의 시작값 기본 0, 간격 기본 1도 마찬가지입니다.

대부분의 호출이 같은 값을 쓰고 **가끔만** 바꾸고 싶을 때 씁니다. 호출은 짧아지고, 바꿀 길은 열려 있습니다.
''')

md(boom("기본값 있는 매개변수를 앞에 두면?"))

code('''
def greet(greeting="안녕하세요", name):
    print(f"{name}님, {greeting}!")
''', raises=True)

md('''
`SyntaxError: parameter without a default follows parameter with a default` — 기본값이 있는 매개변수는 **없는 것 뒤에** 두어야 합니다. `greet("지민")` 에서 `"지민"` 이 어느 자리인지 정할 수 없기 때문입니다.

## 2-2. 키워드 인자 — 순서 대신 이름으로

인자가 많아지면 순서를 외우기 어렵습니다. `이름=값` 으로 넘기면 순서와 상관없이 정확히 전달됩니다. 이것을 **키워드 인자(keyword argument)** 라고 합니다.
''')

code('''
def greet(name, greeting="안녕하세요"):
    print(f"{name}님, {greeting}!")

greet(greeting="좋은 아침", name="지민")     # 순서가 바뀌어도 이름으로 찾아갑니다
print("사과", "배", "감", sep=" / ")         # 앞의 값들은 위치 인자, sep 은 키워드 인자
print(round(3.14159, ndigits=2))             # 두 번째 인자의 이름이 ndigits 라는 것도 보입니다
''')

md('''
규칙은 하나입니다. **위치 인자를 먼저, 키워드 인자를 뒤에.** `greet(name="지민", "좋은 아침")` 은 `SyntaxError` 입니다.

효과는 **읽기 쉬움**입니다. `draw(100, 50, 3)` 보다 `draw(width=100, height=50, border=3)` 이 무슨 뜻인지 바로 보입니다. 인자가 셋을 넘으면 이름으로 넘기는 습관을 들이세요.

## 2-3. 여러 값 돌려주기 — 쉼표로 나열하면 튜플

`return` 뒤에 값을 여러 개 적으면 5주차의 **튜플**로 묶여 돌아옵니다. 받는 쪽은 변수 여러 개로 풀어 받습니다.
''')

code('''
def min_max(scores):
    return min(scores), max(scores)

low, high = min_max([72, 88, 95, 60])     # 튜플을 변수 두 개에 나누어 담기
print(low, high)
print(min_max([72, 88, 95, 60]))          # 실제로는 튜플 하나입니다
print(divmod(17, 5))                      # 몫과 나머지를 한 번에 주는 내장 함수
''')

md('''
함수는 값을 **하나** 돌려줍니다. 여러 개가 필요하면 튜플 · 리스트 · 딕셔너리로 **묶어서** 돌려줍니다. 돌려줄 값이 많고 뜻이 다르면 딕셔너리가 읽기 쉽습니다. `return {"low": 60, "high": 95}`

**예상해 보기** — `def stats(scores): return sum(scores) / len(scores), max(scores) - min(scores)` 에 `[72, 88, 95, 60]` 을 넣으면? → 평균 78.75 와 범위 35 가 튜플로: `(78.75, 35)`

## 2-4. 변수의 유효 범위 ① — 함수 안의 변수는 밖에서 보이지 않습니다

**예상해 보기** — 마지막 줄 `print(total)` 은 무엇을 출력할까요?
''')

code('''
def add(a, b):
    total = a + b
    return total

print(add(3, 5))
''')

md(boom("함수 안에서 만든 total 을 밖에서 부르면?"))

code('''
print(total)
''', raises=True)

md('''
`NameError: name 'total' is not defined` — 함수 **몸통 안에서 만든** 변수 `total` 은 함수가 실행되는 **동안만** 있습니다. 함수가 끝나 돌아오면 사라집니다. 이런 변수를 **지역 변수(local variable)** 라고 합니다. 매개변수 `a`, `b` 도 지역 변수입니다.

함수는 **문 닫힌 방**과 같습니다. 방 안에서 쓴 메모(지역 변수)는 나올 때 버리고, 결과(`return`)만 들고 나옵니다. 밖에 알려 주고 싶은 값은 `return` 으로 건네줍니다.

왜 이렇게 만들었을까요? 함수를 **블랙박스**로 쓰려면, 안에서 어떤 이름을 쓰든 밖에 영향이 없어야 합니다. 다른 함수가 같은 이름 `total` 을 써도 서로 부딪히지 않습니다. 그래서 여러 사람이 각자 함수를 만들어 합칠 수 있습니다.

## 2-5. 변수의 유효 범위 ② — 같은 이름을 쓰면 새 변수가 생깁니다

함수 **밖**에서 만든 변수는 **전역 변수(global variable)** 라고 합니다. 프로그램 전체에서 보입니다.

**예상해 보기** — 두 `print` 는 각각 무엇을 출력할까요?
''')

code('''
total = 0                 # 전역 변수

def add3(a, b, c):
    total = a + b + c     # 함수 안의 새 변수 — 밖의 total 과 이름만 같은 남남
    print(total)

add3(3, 2, 4)
print(total)
''')

md('''
`9` 그리고 `0` 입니다. 함수 안에서 `total = …` 로 **대입**하면 밖의 것을 바꾸는 것이 아니라, **같은 이름의 지역 변수를 새로** 만듭니다. 그래서 밖의 `total` 은 여전히 0입니다.

함수 안에서 전역 변수를 **읽기만** 하는 것은 됩니다. `def show(): print(total)` 은 0을 출력합니다. **대입**하는 순간 지역 변수가 됩니다. 이것이 헷갈림의 근원입니다.

밖의 변수를 바꾸고 싶다면? 함수는 **받은 것으로 계산해서 돌려주기만** 하고, 바꾸는 일은 **밖에서** 합니다. 호출문을 읽으면 무엇이 바뀌는지 **보입니다.**
''')

code('''
total = 0

def add3(a, b, c):
    return a + b + c

total = add3(3, 2, 4)     # 바꾸는 일은 밖에서 — 무엇이 바뀌는지 호출문에 보입니다
print(total)
''')

md('''
<details><summary><b>📎 더 알아보기 — <code>global</code> 키워드</b></summary>

함수 안에서 `global total` 이라고 선언하면 “이 함수의 `total` 은 밖의 것이다”라는 뜻이 되어 전역 변수를 직접 바꿀 수 있습니다.

```python
total = 0

def add3(a, b, c):
    global total
    total = a + b + c

add3(3, 2, 4)
print(total)      # 9
```

동작은 하지만, 함수가 **몰래 밖을 바꾸는** 코드가 됩니다. 호출문 `add3(3, 2, 4)` 만 봐서는 `total` 이 바뀐 줄 모릅니다. 프로그램이 커지면 ‘누가 이 값을 바꿨지?’를 찾기 어려워집니다. 이런 문법이 **있다**는 것만 알아 두고, 값은 `return` 으로 돌려주세요.

</details>
''')

md(key("변수의 유효 범위 정리", "① 함수 안에서 만든 이름(매개변수 포함)은 <b>지역 변수</b>입니다. 함수가 끝나면 사라집니다.<br>② 함수 밖의 이름은 <b>전역 변수</b>입니다. 함수 안에서 읽을 수는 있지만, 대입하면 같은 이름의 지역 변수가 새로 생깁니다.<br>③ 밖과의 대화는 <b>괄호(입력)와 return(출력)</b>으로만 합니다. 그래서 함수는 안심하고 조합할 수 있습니다."))

md('''
## 2-6. 함수가 함수를 부른다 — 그리고 호출 스택

작은 함수를 조합해 큰 일을 합니다. `print_primes` 는 소수를 **어떻게** 판별하는지 모릅니다. `is_prime` 을 부를 뿐입니다.
''')

code('''
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def print_primes(limit):
    for n in range(2, limit + 1):
        if is_prime(n):             # 다른 함수를 부릅니다
            print(n, end=" ")

print_primes(30)
''')

md('''
한 함수는 한 가지 일만 합니다. 판별은 `is_prime`, 출력은 `print_primes`. 판별 방법을 바꿔도 출력 함수는 그대로입니다.

그런데 `print_primes` 가 `is_prime(7)` 을 부른 순간, 컴퓨터는 **돌아갈 곳을 두 개** 기억해야 합니다. `is_prime` 이 끝나면 `print_primes` 의 어디로, `print_primes` 가 끝나면 메인 코드의 어디로.

6주차의 **스택**이 바로 이 일을 합니다. 함수를 호출하면 돌아갈 자리를 스택에 넣고(push), 함수가 끝나면 맨 위를 꺼내(pop) 그곳으로 돌아갑니다. 나중에 부른 함수가 먼저 끝나니 후입선출(LIFO)입니다. 이 스택을 **호출 스택(call stack)** 이라고 합니다.

```
 ┌──────────────────┐
 │ is_prime(7)      │  ← 지금 실행 중. 끝나면 pop
 ├──────────────────┤
 │ print_primes(30) │  ← n = 7 에서 기다리는 중
 ├──────────────────┤
 │ 메인 코드         │  ← print_primes(30) 줄에서 기다리는 중
 └──────────────────┘
```

오류 메시지에서 본 `Traceback (most recent call last)` 가 바로 이 스택을 위에서부터 보여 주는 것입니다. 10주차에는 함수가 **자기 자신**을 부르는 재귀 호출(recursion)을 배웁니다. 그때 이 그림이 다시 나옵니다.

## 2-7. 설명을 붙이기 — 독스트링과 `help()`

함수는 ‘남이(그리고 한 달 뒤의 내가) 쓰는 것’입니다. 몸통 **첫 줄**에 쓴 문자열은 함수의 **설명서**가 됩니다. 이것을 **독스트링(docstring)** 이라고 합니다. `help()` 가 이 글을 보여 줍니다.
''')

code('''
def is_prime(n):
    """n이 소수이면 True, 아니면 False를 돌려줍니다."""
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

help(is_prime)
help(len)          # 남이 만든 함수도 같은 방법으로 — 쓰는 법을 모를 때 물어보세요
''')

md(key("좋은 함수의 네 가지 조건", "① <b>한 가지 일만</b> 합니다. ‘판별하고 출력하고 저장’은 셋입니다. 이름에 ‘그리고’가 들어가면 쪼갭니다.<br>② 이름은 <b>동사</b>로. `get_`, `is_`, `print_`, `calc_` — 이름만 봐도 무엇을 하는지 보이게.<br>③ 입력은 괄호로, 출력은 `return` 으로. 밖의 변수를 몰래 읽거나 바꾸지 않습니다.<br>④ <b>한 화면 안에</b> 들어오게. 스크롤해야 보이면 둘로 나눕니다.<br>`#` 주석은 읽는 사람을 위해, 독스트링은 쓰는 사람(`help()`)을 위해 — 둘 다 ‘왜’를 적는 곳입니다."))

md('''
## 2-8. 예제 — 숫자 맞히기 게임을 함수로 쪼개기

6주차의 숫자 맞히기 게임은 한 덩어리의 `while` 안에 입력 · 판정 · 출력 · 횟수가 **모두** 섞여 있었습니다. 13줄이라 아직 읽히지만, 기능이 늘면 금세 100줄이 됩니다.

‘입력 받기 · 판정하기 · 진행하기’ 세 함수로 나눕니다. 먼저 판정 함수만 봅니다.
''')

code('''
def judge(guess, answer):
    """추측한 수와 정답을 비교해 안내 문장을 돌려줍니다."""
    if guess > answer:
        return "정답보다 큰 수입니다"
    elif guess < answer:
        return "정답보다 작은 수입니다"
    return "정답"

print(judge(50, 30))
print(judge(10, 30))
print(judge(30, 30))
''')

md('''
`judge` 는 입력도 화면도 모릅니다. **값을 받아 값을 돌려줄 뿐**입니다. 그래서 위처럼 **따로 시험**할 수 있습니다. 게임을 끝까지 하지 않고도 판정이 맞는지 확인했습니다.

이제 나머지 두 함수를 붙여 게임을 완성합니다. 실행해서 직접 맞혀 보세요.
''')

code('''
import random

def read_guess():
    """사용자에게서 수를 하나 입력받아 돌려줍니다."""
    return int(input("1 ~ 100 사이의 수를 맞혀 보세요: "))

def play_game():
    """게임의 줄거리 — 세부는 함수 이름 뒤에 숨었습니다."""
    answer = random.randint(1, 100)
    tries = 0
    while True:
        guess = read_guess()
        tries += 1
        message = judge(guess, answer)
        print(message)
        if message == "정답":
            print(f"{tries}번 만에 맞혔습니다")
            break

play_game()
''')

md(note("무엇이 좋아졌나", "① `play_game` 을 읽으면 게임의 <b>줄거리</b>가 보입니다. 입력 방식을 바꾸려면 `read_guess` 만, 판정 기준을 바꾸려면 `judge` 만 고칩니다.<br>② `judge` 처럼 입력과 화면에서 떨어진 함수는 <b>따로 시험</b>할 수 있습니다. 이 노트북의 자가 점검이 하는 일이 바로 그것입니다.<br>③ 3주차의 <b>분해</b>가 코드에서는 함수로 나타납니다. 9주차에는 이 셋을 클래스 하나로 묶습니다."))

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "평균 함수", "약 4분",
         "점수 리스트를 받아 평균을 <b>돌려주는</b> `average(scores)` 를 정의하세요. 빈 리스트가 오면 나누기 0 오류 대신 `0` 을 돌려줍니다.<br>`average([72, 88, 95, 60])` → `78.75`, `average([])` → `0`",
         '''
# 여기에 함수를 정의하세요


print(average([72, 88, 95, 60]))
print(average([]))
''',
         "abs(average([72, 88, 95, 60]) - 78.75) < 1e-6 and average([]) == 0 and abs(average([10]) - 10) < 1e-6",
         '''
def average(scores):
    if len(scores) == 0:         # 빈 리스트 → 0 (if not scores: 로 써도 됩니다)
        return 0
    return sum(scores) / len(scores)

print(average([72, 88, 95, 60]))     # 78.75
print(average([]))                   # 0
''', raises=True, heading="## 2교시 실습")

practice("✏️ 실습 2-2", "단어 세기 함수", "약 5분",
         "문장을 받아 `{단어: 횟수}` 딕셔너리를 돌려주는 `count_words(text)` 를 정의하세요. 소문자로 바꾼 뒤(`lower()`) `split()` 으로 나눕니다. 6주차 실습 2-3의 코드를 함수 안으로 옮기면 됩니다.<br>`count_words(\"The cat saw the dog\")` → `{'the': 2, 'cat': 1, 'saw': 1, 'dog': 1}`",
         '''
# 여기에 함수를 정의하세요


print(count_words("The cat saw the dog"))
''',
         'count_words("The cat saw the dog") == {"the": 2, "cat": 1, "saw": 1, "dog": 1} and count_words("a A a") == {"a": 3} and count_words("") == {}',
         '''
def count_words(text):
    word_count = {}
    for word in text.lower().split():
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

print(count_words("The cat saw the dog"))
''', raises=True)

practice("✏️ 실습 2-3", "기본값과 여러 값", "약 5분",
         "함수 두 개를 정의하세요.<br>① `describe(name, year=1)` — `\"지민 (1학년)\"` 처럼 이름과 학년을 합친 <b>문자열을 돌려줍니다.</b> 학년을 생략하면 1학년입니다. `describe(\"지민\", 3)` → `\"지민 (3학년)\"`<br>② `min_max(scores)` — 최솟값과 최댓값을 <b>튜플로</b> 돌려줍니다. `min()` · `max()` 를 써도 되고, 6주차 실습 2-2처럼 직접 찾아도 됩니다.",
         '''
# 여기에 함수 두 개를 정의하세요


print(describe("지민"))
print(describe("민수", 3))
low, high = min_max([72, 88, 95, 60])
print(low, high)
''',
         'describe("지민") == "지민 (1학년)" and describe("민수", 3) == "민수 (3학년)" and describe(name="하늘", year=2) == "하늘 (2학년)" and min_max([72, 88, 95, 60]) == (60, 95) and min_max([5]) == (5, 5)',
         '''
def describe(name, year=1):
    return f"{name} ({year}학년)"

def min_max(scores):
    return min(scores), max(scores)

print(describe("지민"))              # 지민 (1학년)
print(describe("민수", 3))           # 민수 (3학년)
low, high = min_max([72, 88, 95, 60])
print(low, high)                     # 60 95
''', raises=True)

practice("✏️ 실습 2-4", "스택으로 문자열 뒤집기 함수 (도전)", "",
         "6주차 3-3의 ‘스택으로 문자열 뒤집기’를 함수 `reverse_word(word)` 로 만드세요. 글자를 스택에 차례로 넣었다가 다시 꺼내 이어 붙인 문자열을 <b>돌려줍니다.</b> 슬라이싱 `[::-1]` 은 쓰지 않습니다. (시간이 남는 사람만)<br>`reverse_word(\"python\")` → `\"nohtyp\"`",
         '''
# 여기에 함수를 정의하세요


print(reverse_word("python"))
print(reverse_word("level"))
''',
         'reverse_word("python") == "nohtyp" and reverse_word("level") == "level" and reverse_word("") == ""',
         '''
def reverse_word(word):
    stack = []
    for ch in word:
        stack.append(ch)
    result = ""
    while stack:
        result += stack.pop()
    return result

print(reverse_word("python"))     # nohtyp
print(reverse_word("level"))      # level
''', raises=True)

md(key("2교시 정리", "① 기본값 `def f(x, n=2):` 은 생략하면 그 값. 기본값 있는 매개변수는 뒤에.<br>② 키워드 인자 `f(n=3, x=1)` 은 이름으로 넘기니 순서 무관. 위치 인자 먼저.<br>③ `return a, b` 는 튜플 하나. `x, y = f()` 로 풀어 받습니다.<br>④ 함수 안의 이름은 지역 변수. 밖의 같은 이름과는 남남. 밖과의 대화는 괄호와 `return` 으로만.<br>⑤ 함수가 함수를 부르면 돌아갈 곳을 <b>호출 스택</b>에 쌓습니다. 작은 함수를 조합해 큰 일을 합니다.") + "\n\n" + BREAK)

# ═════════════════════════ 3교시 ═════════════════════════
md("# 3교시 · 모듈과 사용자 정의 라이브러리\n\n" + period(3, "함수를 파일에 모으다 — 모듈과 import", [
    "모듈이 무엇인지, 세 종류가 무엇인지 설명한다",
    "import 의 여러 방법을 알고 math · random 모듈을 쓴다",
    "내 함수를 .py 파일에 저장해 모듈로 만들고 import 한다",
    "dir() 과 help() 로 모르는 모듈을 탐색한다",
]))

md('''
## 3-1. 모듈 — 함수를 모아 둔 `.py` 파일

6주차 게임에서 `import random` 을 이미 썼습니다. `random` 은 누군가 만들어 둔 **함수 묶음**입니다. 실체는 `random.py` 라는 파일 하나이고, 그 안에 `def randint(a, b): …`, `def choice(seq): …` 같은 함수 정의가 들어 있습니다.

이렇게 함수 · 변수를 모아 둔 `.py` 파일을 **모듈(module)** 이라고 합니다. 파일 이름에서 `.py` 를 뗀 것이 모듈 이름입니다. `import random` 은 “`random.py` 를 읽어 그 안의 이름들을 쓸 수 있게 하라”는 뜻입니다.

| 종류 | 설명 | 예 |
|:---|:---|:---|
| **표준 모듈** | Python 에 **기본 포함**. 설치가 필요 없습니다 | `math`, `random`, `datetime`, `json` … 200여 개 |
| **외부 모듈** | 다른 사람들이 만들어 **공개**한 것. 설치해서 씁니다 | `numpy`, `pandas`, `matplotlib` — 12주차 |
| **사용자 정의 모듈** | **내가 만든** `.py` 파일 | 오늘 만든 `is_prime` 을 `my_utils.py` 에 저장 — 3-5 |

모듈 여러 개를 묶은 큰 단위를 **라이브러리(library)** 라고 부릅니다. 표준 라이브러리 = Python 이 기본으로 주는 모듈 전체입니다. 공식 문서: [docs.python.org/ko/3/library](https://docs.python.org/ko/3/library/)

## 3-2. `import` 의 여러 방법

모두 같은 함수를 가져옵니다. 다른 것은 ‘부를 때 이름을 어떻게 쓰느냐’입니다.
''')

code('''
import math                          # ① 모듈 이름을 붙여 부릅니다 — 기본 · 권장
print(math.sqrt(16), math.pi)

import random as rd                  # ② 모듈에 별명 — 긴 이름을 줄일 때 (numpy as np)
print(rd.randint(1, 6))

from math import sqrt, pi            # ③ 필요한 것만 꺼내 와 모듈 이름 없이 부릅니다
print(sqrt(16), pi)

from math import sqrt as root        # ④ 꺼내 온 함수에 별명
print(root(16))
''')

md('''
| 방법 | 가져오기 | 부르기 | 특징 |
|:---|:---|:---|:---|
| ① | `import math` | `math.sqrt(16)` | **어느 모듈의 함수인지** 늘 보입니다. 수업의 기본 |
| ② | `import random as rd` | `rd.randint(1, 6)` | 긴 모듈 이름을 줄입니다 |
| ③ | `from math import sqrt` | `sqrt(16)` | 짧지만 출처가 안 보입니다 |
| ④ | `from math import sqrt as root` | `root(16)` | 이름이 겹칠 때 피합니다 |
| ⑤ | `from math import *` | `sqrt(16)` | **전부** 꺼내 옵니다. 내 함수와 이름이 겹치면 덮어씁니다 — 3-4 |

`math` 안의 `pi` 는 함수가 아니라 **변수**입니다. 모듈 안의 것은 함수든 변수든 `모듈.이름` 으로 똑같이 부릅니다. `import math, random` 처럼 한 줄에 여러 모듈을 가져올 수도 있습니다.

## 3-3. 표준 모듈 둘러보기 — `math` 와 `random`

자주 쓰는 함수 몇 개만 알아 둡니다. 나머지는 필요할 때 3-7의 `dir()` 과 `help()` 로 찾습니다.
''')

code('''
import math, random

print(math.sqrt(2))                   # 제곱근.  2 ** 0.5 와 같습니다
print(math.floor(3.7), math.ceil(3.2))   # 내림, 올림
print(math.gcd(12, 18))               # 최대공약수
print(random.randint(1, 6))           # 1 이상 6 이하 정수 하나 — 실행할 때마다 다릅니다
print(random.choice(["김밥", "라면", "떡볶이"]))   # 리스트에서 하나 고르기
''')

md('''
주사위를 1,000번 던지면 각 눈이 몇 번 나올까요? 6주차의 딕셔너리 세기와 `for` 문을 씁니다.
''')

code('''
import random

counts = {}
for _ in range(1000):                 # 꺼낸 값을 쓰지 않을 때는 변수 이름을 _ 로 둡니다
    face = random.randint(1, 6)
    counts[face] = counts.get(face, 0) + 1

for face in range(1, 7):
    print(face, counts[face])
''')

md(note("의사 난수(pseudo random number)", "컴퓨터는 정해진 대로만 움직이는 기계라 ‘진짜 우연’을 만들 수 없습니다. 계산으로 <b>우연처럼 보이는</b> 수를 만듭니다. 그래서 ‘의사(擬似, 흉내 낸) 난수’입니다. 게임 · 시뮬레이션 · 표본 추출에 씁니다. `random.shuffle(리스트)` 는 리스트를 제자리에서 섞고, `random.random()` 은 0 이상 1 미만의 실수를 줍니다."))

md('''
## 3-4. `from 모듈 import *` 를 피하는 이유 — 이름이 조용히 덮어씌워집니다

**예상해 보기** — 두 번째 `print(sqrt(16))` 은 무엇을 출력할까요?
''')

code('''
def sqrt(x):
    return "제곱근은 나중에"      # 내가 만든 함수

print(sqrt(16))

from math import *              # math 의 sqrt 가 내 함수를 덮어씁니다
print(sqrt(16))
''')

md('''
`from math import *` 가 `math` 의 이름 **수십 개**를 한꺼번에 가져오면서, 내가 만든 `sqrt` 를 **덮어썼습니다.** 오류 메시지가 **없습니다.** 어느 날 함수가 다르게 동작하는데 이유를 모르는 상황, 가장 찾기 어려운 버그입니다.

`math.sqrt` 처럼 모듈 이름을 붙여 부르면 이런 일이 없습니다. `math.` 은 **성(姓)** 과 같습니다. ‘김 지민’과 ‘이 지민’이 같은 교실에 있을 수 있듯, `math.sqrt` 와 내 `sqrt` 도 함께 있을 수 있습니다. `import *` 는 성을 떼어 버리는 일입니다. 이렇게 이름이 속한 울타리를 **이름 공간(namespace)** 이라고 합니다.
''')

md(key("import 정리", "① 모듈은 함수를 모아 둔 `.py` 파일입니다. `import 모듈` 뒤에 `모듈.이름` 으로 부릅니다.<br>② 수업에서는 `import math` 처럼 <b>출처가 보이는</b> 방법을 기본으로 씁니다.<br>③ `from 모듈 import *` 는 내 이름을 덮어쓸 수 있으니 쓰지 않습니다.<br>④ 함수 이름을 외우는 것이 아니라 <b>찾는 법</b>을 익힙니다 — 3-7."))

md('''
## 3-5. 나만의 모듈 만들기 — 함수를 `.py` 파일에 저장하고 `import`

오늘 만든 함수를 다음 주 노트북에서도 쓰려면 어떻게 할까요? 복사해 붙이지 않습니다. **파일에 저장**하고 `import` 합니다.

노트북에서 파일을 만드는 명령이 `%%writefile` 입니다. 셀 **맨 윗줄**에 `%%writefile 파일이름` 을 쓰면, 그 셀은 실행되지 않고 내용이 **그대로 파일로 저장**됩니다. 노트북 전용 명령이라 `%` 가 붙어 있습니다.
''')

code('''
%%writefile calc_area.py
PI = 3.14159

def circle_area(r):
    """반지름 r 인 원의 넓이"""
    return PI * r * r

def rect_area(w, h):
    """가로 w, 세로 h 인 직사각형의 넓이"""
    return w * h
''')

md('''
`Writing calc_area.py` 가 나오면 노트북과 **같은 폴더**에 파일이 생긴 것입니다. 왼쪽 파일 탐색기(📁)에서 확인해 보세요. 같은 이름으로 다시 실행하면 `Overwriting` 이라고 나오며 덮어씁니다.

이제 `random` 을 쓰듯 가져옵니다. `.py` 는 붙이지 않습니다. 함수도 변수(`PI`)도 `calc_area.` 뒤에 붙여 부릅니다.
''')

code('''
import calc_area

print(calc_area.circle_area(3))
print(calc_area.rect_area(4, 5))
print(calc_area.PI)
help(calc_area.circle_area)       # 독스트링도 함께 따라옵니다
''')

md(warn("파일을 고친 뒤 다시 import 해도 바뀌지 않습니다", "Python 은 한 번 읽은 모듈을 <b>기억해 두고</b> 다시 읽지 않습니다. `%%writefile` 셀을 고쳐 다시 실행한 뒤 `import calc_area` 를 또 실행해도 <b>옛 내용</b>이 그대로입니다.<br>다시 읽게 하려면 `importlib.reload(calc_area)` 를 실행하거나, `Kernel → Restart Kernel` 뒤 위에서부터 다시 실행하세요. 실습 3-3에서 직접 해 봅니다."))

code('''
import importlib
importlib.reload(calc_area)       # 파일을 고쳤을 때 다시 읽어 옵니다. 지금은 바뀐 것이 없어 조용히 끝납니다
print(calc_area.circle_area(1))
''')

md('''
## 3-6. 모듈 안의 문장은 `import` 할 때 실행됩니다

모듈 파일 끝에 시험용 `print` 를 넣어 두면, 남이 `import` 할 때마다 그 `print` 가 찍힙니다. `import` 는 파일을 **위에서 아래로 실행**해서 그 안의 이름들을 모으는 일이기 때문입니다.

**예상해 보기** — 아래 두 셀을 차례로 실행하면 두 번째 셀에서 무엇이 출력될까요?
''')

code('''
%%writefile noisy.py
def hello():
    return "hello"

print("noisy 모듈을 읽는 중입니다")      # 함수 정의가 아닌 문장
''')

code('''
import noisy
print(noisy.hello())
''')

md('''
<details><summary><b>📎 더 알아보기 — <code>if __name__ == "__main__":</code> 관용구</b></summary>

남의 코드에서 자주 보게 되는 한 줄입니다. `__name__` 은 Python 이 자동으로 채우는 변수로, 파일을 **직접 실행**하면 `"__main__"` 이고, 다른 파일이 **import** 하면 그 모듈 이름(`"calc_area"`)입니다.

```python
PI = 3.14159

def circle_area(r):
    return PI * r * r

if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 돌아가는 시험용 코드. import 할 때는 건너뜁니다
    print(circle_area(1))
```

같은 파일이 ‘프로그램’도 되고 ‘모듈’도 됩니다. 뜻은 ‘직접 실행할 때만’. 이 정도로 기억해 두면 충분합니다.

</details>

## 3-7. 모르는 모듈을 탐색하기 — `dir()` 과 `help()`

모듈 안에 무엇이 있는지, 각 함수를 어떻게 쓰는지는 외우지 않습니다. **물어봅니다.**

- `dir(모듈)` — 모듈이 가진 **이름 목록**을 리스트로 줍니다. `_` 로 시작하는 것은 내부용이라 걸러 봅니다.
- `help(함수)` — 함수의 **독스트링**을 보여 줍니다. 2교시에 내가 쓴 독스트링도 같은 자리에 나옵니다.
''')

code('''
import math

names = [name for name in dir(math) if not name.startswith("_")]
print(len(names), "개:", names[:12], "...")
help(math.floor)
''')

md(key("찾는 순서 — 세 단계", "① `dir()` 로 이름을 훑습니다. “소수점을 자르는 게 있을 텐데…” → `floor`, `trunc` 발견.<br>② `help()` 로 쓰는 법을 확인합니다. 받는 것과 돌려주는 것.<br>③ 공식 문서를 읽거나 AI 에게 묻습니다. <b>읽을 줄 알면</b> AI 의 답도 검증할 수 있습니다 — 3주차의 결론입니다.<br>어느 층이든 — 내 함수, 내 모듈, 표준 라이브러리, 외부 라이브러리, AI 가 쓰는 코드 — 모두 <b>이름 + 괄호 + 인자</b>로 부르고 결과를 받습니다. 오늘 그 첫 층을 만들었습니다."))

# ── 3교시 실습 ──
practice("✏️ 실습 3-1", "math 로 계산하기", "약 4분",
         "`import math` 뒤에 함수 두 개를 정의하세요.<br>① `circle_area(r)` — 반지름 `r` 인 원의 넓이. `math.pi` 를 씁니다. `circle_area(1)` → `3.141592…`<br>② `hypotenuse(a, b)` — 직각삼각형의 두 변 `a`, `b` 를 받아 빗변 길이 `math.sqrt(a*a + b*b)` 를 돌려줍니다. `hypotenuse(3, 4)` → `5.0`",
         '''
import math

# 여기에 함수 두 개를 정의하세요


print(circle_area(1))
print(hypotenuse(3, 4))
''',
         "abs(circle_area(1) - 3.141592653589793) < 1e-9 and abs(circle_area(2) - 12.566370614359172) < 1e-9 and abs(hypotenuse(3, 4) - 5) < 1e-9 and abs(hypotenuse(5, 12) - 13) < 1e-9",
         '''
import math

def circle_area(r):
    return math.pi * r ** 2

def hypotenuse(a, b):
    return math.sqrt(a * a + b * b)

print(circle_area(1))        # 3.141592653589793
print(hypotenuse(3, 4))      # 5.0
''', raises=True, heading="## 3교시 실습")

practice("✏️ 실습 3-2", "주사위 던지기 함수", "약 5분",
         "`roll_counts(times)` — `random.randint(1, 6)` 을 `times` 번 던져 `{눈: 횟수}` 딕셔너리를 <b>돌려줍니다.</b> 3-3의 주사위 셀을 함수 안으로 옮기면 됩니다.<br>여섯 눈의 횟수 합은 `times` 와 같아야 합니다. 각 눈은 대략 1/6 이지만 정확히 같지는 않습니다. 한 번도 안 나온 눈이 있으면 키가 빠질 수 있으니, 1 ~ 6 을 미리 0 으로 채워 두면 안전합니다.",
         '''
import random

# 여기에 함수를 정의하세요


print(roll_counts(1000))
''',
         "sum(roll_counts(600).values()) == 600 and set(roll_counts(600).keys()) == {1, 2, 3, 4, 5, 6} and all(50 <= v <= 150 for v in roll_counts(600).values())",
         '''
import random

def roll_counts(times):
    counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}     # 미리 0 으로 채워 둡니다
    for _ in range(times):
        face = random.randint(1, 6)
        counts[face] += 1
    return counts

print(roll_counts(1000))
''', raises=True)

practice("✏️ 실습 3-3", "my_utils.py — 나만의 라이브러리", "약 6분",
         "오늘 만든 함수 세 개 `is_prime(n)`, `average(scores)`, `celsius_to_fahrenheit(celsius)` 를 아래 `%%writefile` 셀에 넣어 `my_utils.py` 파일로 저장하세요. 정의만 넣고 `print` 는 넣지 않습니다(3-6).<br>그다음 셀은 파일을 다시 읽어 와 시험합니다. 파일을 고칠 때마다 두 셀을 <b>차례로</b> 다시 실행하세요.<br>수업 끝에 `File → Download` 로 이 파일도 내려받아 두세요. 다음 주차에 다시 씁니다.",
         '''
%%writefile my_utils.py
# 여기에 함수 세 개를 정의하세요 (is_prime, average, celsius_to_fahrenheit)

''',
         "importlib.reload(my_utils).is_prime(97) and not my_utils.is_prime(91) and abs(my_utils.average([80, 90]) - 85) < 1e-6 and my_utils.average([]) == 0 and abs(my_utils.celsius_to_fahrenheit(100) - 212) < 1e-6",
         '''
%%writefile my_utils.py
def is_prime(n):
    """n이 소수이면 True, 아니면 False"""
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True

def average(scores):
    """점수 리스트의 평균. 비어 있으면 0"""
    if len(scores) == 0:
        return 0
    return sum(scores) / len(scores)

def celsius_to_fahrenheit(celsius):
    """섭씨 → 화씨"""
    return celsius * 9 / 5 + 32
''',
         extra='''
import importlib, my_utils
importlib.reload(my_utils)       # 파일을 고쳤을 때 다시 읽어 옵니다
print(my_utils.is_prime(97), my_utils.average([80, 90]), my_utils.celsius_to_fahrenheit(100))
''', extra_raises=True)

md(key("3교시 정리", "① 모듈은 함수를 모아 둔 `.py` 파일입니다. 표준 · 외부 · 사용자 정의 세 종류가 있습니다.<br>② `import 모듈` 뒤 `모듈.이름` 으로 부릅니다. 출처가 보이는 이 방법이 기본입니다. `import *` 는 쓰지 않습니다.<br>③ `%%writefile` 로 노트북 셀을 파일로 저장하면 그것이 곧 <b>나만의 라이브러리</b>입니다. 고친 뒤에는 `importlib.reload()`.<br>④ 모듈 안의 문장은 `import` 할 때 실행됩니다. 모듈에는 정의만 둡니다.<br>⑤ `dir()` 과 `help()` 로 찾습니다. 외우지 않습니다."))

# ═════════════════════════ 주차 정리 ═════════════════════════
md('''
# 7주차 정리

| 개념 | 한 줄 요약 |
|:---|:---|
| **함수 정의** | `def 이름(매개변수):` 몸통 `return 결과`. 정의는 약속, 호출은 실행 |
| **매개변수 / 인자** | 정의 쪽 빈 자리 / 호출 쪽 실제 값. 순서대로 짝이 맞는다 |
| **return** | 값을 돌려주고 함수를 끝낸다. 호출식은 그 값으로 바뀐다. 없으면 `None` |
| **print ≠ return** | 보여 주기 ≠ 건네주기. 결과를 밖에서 쓰려면 `return` |
| **기본값 · 키워드 인자** | `def f(x, n=2)` · `f(n=3, x=1)`. 기본값 있는 것은 뒤에, 키워드 인자는 뒤에 |
| **여러 값 반환** | `return a, b` 는 튜플 하나. `x, y = f()` 로 풀어 받는다 |
| **지역 / 전역 변수** | 함수 안의 이름은 함수 안에서 끝난다. 밖과의 대화는 괄호와 `return` 으로만 |
| **호출 스택** | 돌아갈 곳을 쌓아 두는 스택. 나중에 부른 함수가 먼저 끝난다 |
| **모듈** | 함수를 모아 둔 `.py` 파일. `import 모듈` 뒤 `모듈.이름` |
| **%%writefile** | 노트북 셀을 파일로 저장 → 나만의 모듈. 고친 뒤에는 `importlib.reload()` |
| **dir() · help()** | 모듈 안의 이름 목록 · 함수 설명서(독스트링) |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| `NameError` | 그 이름을 모른다 | 정의하기 전에 호출했다 · 지역 변수를 밖에서 불렀다 |
| `TypeError: missing … argument` | 인자 개수가 매개변수와 다르다 | `greet("지민")` 에 `year` 가 빠짐 |
| `None` 이 출력됨 | 오류는 아니지만 신호 | `return` 이 없거나 `print` 만 한 함수의 결과를 담았다 |
| `SyntaxError: … follows parameter with a default` | 기본값 있는 매개변수 뒤에 없는 것을 두었다 | `def greet(greeting="…", name)` |
| `ModuleNotFoundError` | 그 이름의 `.py` 파일이 없다 | `%%writefile` 셀을 먼저 실행하지 않았다 · 이름 오타 |
| `IndentationError` | `def` 다음 몸통을 들여쓰지 않았다 | |

''' + key("오늘의 한 문장", "같은 코드가 두 번 나오면 <b>함수</b>로, 같은 함수가 두 노트북에 나오면 <b>모듈</b>로. 이름을 붙이는 순간 ‘어떻게’는 숨고 ‘무엇을’만 남는다 — 3주차의 <b>추상화</b>입니다.") + f'''

<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 8주차 중간고사</b><br>
범위는 1 ~ 7주차입니다. 닫힌 책(closed book) 지필시험으로 객관식과 주관식이 나오며, 시험 중 IT 기기는 쓸 수 없습니다. 일시와 장소는 LearnUs 공지를 따릅니다.<br>
준비는 세 가지입니다. ① 4 ~ 7주차 노트북을 <b>위에서부터 다시 실행</b>하며 출력을 먼저 예상한다. ② 실습 코드를 <b>종이에</b> 써 본다 — 시험장에는 자동완성이 없다. ③ 각 주차 ‘정리’와 ‘오류와 신호’ 표를 설명할 수 있는지 확인한다.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 노트북과 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">my_utils.py</code> 를 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
''')

# ═════════════════════════ 과제 ═════════════════════════
FIRST_HW_CELL = len(CELLS)

md(f'''
# 7주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">4 ~ 7주차 종합 — 함수로 만들기</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>모든 문제는 <b>함수를 정의</b>하는 문제입니다. 자가 점검은 여러분의 함수를 <b>여러 가지 값으로</b> 불러 봅니다</li><li>4주차(변수 · 문자열), 5주차(리스트 · 딕셔너리 · if 문), 6주차(반복문 · 스택 · 큐), 7주차(함수 · 모듈)의 내용만으로 풀 수 있습니다</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 함수 이름과 매개변수 순서(`grade_of(score)` 등)를 바꾸지 마세요. 점검 셀이 그 이름으로 함수를 부릅니다.<br>③ 점검 셀은 예시와 <b>다른 값</b>으로도 함수를 부릅니다. 예시 값 하나만 맞추는 코드는 통과하지 못합니다. <b>어떤 값이 와도 옳게 동작하는 함수</b>를 씁니다.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다.<br>⑤ 막히면 먼저 <b>“무엇을 받아서, 무엇을 하고, 무엇을 돌려주나”</b>를 한국어로 한 줄 적어 보세요. 그다음에 `def` 한 줄을 씁니다."))

practice("📝 과제 1", "학점 함수와 학점 집계 함수", "",
         "함수 두 개를 정의하세요.<br>① `grade_of(score)` — 점수 하나를 받아 학점 문자열을 돌려줍니다. 90점 이상 `\"A\"`, 80점 이상 `\"B\"`, 70점 이상 `\"C\"`, 60점 이상 `\"D\"`, 그 밖은 `\"F\"`.<br>② `grade_counts(scores)` — `{이름: 점수}` 딕셔너리를 받아 `{\"A\": 인원, \"B\": 인원, \"C\": 인원, \"D\": 인원, \"F\": 인원}` 을 돌려줍니다. 해당 학생이 없는 학점도 `0` 으로 넣습니다. <b>②는 반드시 ①을 호출해서</b> 학점을 정하세요. 2-6의 ‘함수가 함수를 부른다’입니다.",
         '''
scores = {"김연세": 88, "이미래": 95, "박원주": 72, "최하늘": 59, "정바다": 81, "한솔": 67}

# 여기에 함수 두 개를 정의하세요


print(grade_of(88), grade_of(59))
print(grade_counts(scores))
''',
         '[grade_of(s) for s in [100, 90, 89, 80, 79, 70, 69, 60, 59, 0]] == ["A", "A", "B", "B", "C", "C", "D", "D", "F", "F"] and grade_counts(scores) == {"A": 1, "B": 2, "C": 1, "D": 1, "F": 1} and grade_counts({"a": 90, "b": 90}) == {"A": 2, "B": 0, "C": 0, "D": 0, "F": 0} and grade_counts({}) == {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}',
         '''
scores = {"김연세": 88, "이미래": 95, "박원주": 72, "최하늘": 59, "정바다": 81, "한솔": 67}

def grade_of(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"

def grade_counts(scores):
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for score in scores.values():
        counts[grade_of(score)] += 1      # 함수가 함수를 부른다
    return counts

print(grade_of(88), grade_of(59))
print(grade_counts(scores))
''', raises=True, show_answer=False)

practice("📝 과제 2", "카이사르 암호 함수", "",
         "6주차 과제 2의 카이사르 암호를 함수로 만듭니다. 영어 소문자를 알파벳 순서로 `shift` 칸 밀고, 끝을 넘어가면 처음으로 돌아옵니다(`z` → `c`). 소문자가 아닌 글자(공백 등)는 그대로 둡니다.<br>① `encrypt(text, shift)` — 암호문을 돌려줍니다. `encrypt(\"hello world\", 3)` → `\"khoor zruog\"`<br>② `decrypt(text, shift)` — 원래 문장을 돌려줍니다. 새로 쓰지 말고 <b>①을 호출해서</b> 만들어 보세요. 3칸 민 것을 되돌리는 것은 23칸(= 26 − 3) 더 미는 것과 같습니다.<br>힌트: 4주차의 `ord()` · `chr()`. `ord(ch) - ord(\"a\")` 는 `a` 가 0, `z` 가 25인 번호입니다. ‘끝을 넘으면 처음으로’는 `% 26` 입니다.",
         '''
# 여기에 함수 두 개를 정의하세요


secret = encrypt("computational thinking", 5)
print(secret)
print(decrypt(secret, 5))
''',
         'encrypt("hello world", 3) == "khoor zruog" and encrypt("xyz", 3) == "abc" and encrypt("abc", 0) == "abc" and decrypt(encrypt("computational thinking", 5), 5) == "computational thinking" and decrypt("khoor zruog", 3) == "hello world" and encrypt("Hi!", 1) == "Hj!"',
         '''
def encrypt(text, shift):
    result = ""
    for ch in text:
        if "a" <= ch <= "z":
            number = (ord(ch) - ord("a") + shift) % 26      # 0 ~ 25 번호로 바꿔 밀고, 넘치면 처음으로
            result += chr(number + ord("a"))
        else:
            result += ch
    return result

def decrypt(text, shift):
    return encrypt(text, 26 - shift % 26)      # 반대 방향으로 미는 것 = 26 - shift 만큼 더 미는 것

secret = encrypt("computational thinking", 5)
print(secret)
print(decrypt(secret, 5))
''', raises=True, show_answer=False)

practice("📝 과제 3", "괄호 짝 검사 함수 — 세 종류의 괄호", "",
         "6주차 3-3의 괄호 짝 검사를 함수 `is_balanced(text)` 로 만들되, 괄호를 `()` · `[]` · `{}` <b>세 종류</b>로 넓히세요. 짝이 모두 맞으면 `True`, 아니면 `False` 를 돌려줍니다.<br>닫는 괄호를 만나면 스택에서 꺼낸 여는 괄호가 <b>같은 종류</b>여야 합니다. `\"([)]\"` 은 개수는 맞지만 종류가 엇갈려 `False` 입니다.<br>힌트: `pairs = {\")\": \"(\", \"]\": \"[\", \"}\": \"{\"}` 처럼 닫는 괄호 → 여는 괄호 딕셔너리를 만들면 `if` 가 줄어듭니다. 괄호가 아닌 글자는 무시합니다.<br>`is_balanced(\"{[(1 + 2) * 3]}\")` → `True`, `is_balanced(\"([)]\")` → `False`, `is_balanced(\"((\")` → `False`",
         '''
# 여기에 함수를 정의하세요


for text in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", ""]:
    print(repr(text), is_balanced(text))
''',
         '[is_balanced(t) for t in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", "", "(a[b]{c})", "(]", "[(])"]] == [True, False, False, False, True, True, True, False, False]',
         '''
def is_balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}      # 닫는 괄호 → 짝이 되는 여는 괄호
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:   # 꺼낼 것이 없거나 종류가 다르면
                return False
    return len(stack) == 0                       # 남은 여는 괄호가 없어야 True

for text in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", ""]:
    print(repr(text), is_balanced(text))
''', raises=True, show_answer=False)

practice("📝 과제 4", "큐로 푸는 수건돌리기 함수", "",
         "6주차 과제 4를 함수 `josephus(n, k)` 로 만드세요. 1번부터 `n` 번까지 둥글게 앉아 `k` 번째 사람이 빠지기를 한 명 남을 때까지 되풀이합니다. 빠진 번호의 리스트와 마지막 남은 사람의 번호를 <b>튜플로</b> 돌려줍니다.<br>`josephus(7, 3)` → `([3, 6, 2, 7, 5, 1], 4)`<br>힌트: 큐 `list(range(1, n + 1))` 에서 맨 앞을 꺼내 맨 뒤로 보내기를 `k - 1` 번 하면 `k` 번째 사람이 맨 앞에 옵니다. `n` 이 1이면 빠진 사람 없이 `([], 1)` 입니다.",
         '''
# 여기에 함수를 정의하세요


order, survivor = josephus(7, 3)
print("빠진 순서:", order)
print("마지막 남은 사람:", survivor)
''',
         "josephus(7, 3) == ([3, 6, 2, 7, 5, 1], 4) and josephus(5, 2) == ([2, 4, 1, 5], 3) and josephus(1, 3) == ([], 1) and josephus(6, 1) == ([1, 2, 3, 4, 5], 6)",
         '''
def josephus(n, k):
    queue = list(range(1, n + 1))
    order = []
    while len(queue) > 1:
        for i in range(k - 1):
            queue.append(queue.pop(0))     # 앞사람을 맨 뒤로 보내기를 k - 1 번
        order.append(queue.pop(0))         # k 번째 사람이 빠진다
    return order, queue[0]

order, survivor = josephus(7, 3)
print("빠진 순서:", order)
print("마지막 남은 사람:", survivor)
''', raises=True, show_answer=False)

practice("📝 과제 5", "text_tools.py — 텍스트 분석 모듈 (도전)", "",
         "실습 2-2의 `count_words(text)` 와 새 함수 `most_common(word_count)` 를 `text_tools.py` 모듈로 저장하세요.<br>`most_common(word_count)` — `{단어: 횟수}` 딕셔너리를 받아 <b>가장 많이 나온 단어</b>를 돌려줍니다. 횟수가 같으면 먼저 나온 단어입니다. 빈 딕셔너리이면 `None` 을 돌려줍니다. 6주차 실습 2-2의 ‘최댓값 찾기’를 딕셔너리에 적용합니다. `max()` 를 써도 됩니다.<br>아래 두 번째 셀은 모듈을 다시 읽어 와 시험합니다. 파일을 고칠 때마다 두 셀을 차례로 실행하세요.",
         '''
%%writefile text_tools.py
# 여기에 count_words 와 most_common 을 정의하세요

''',
         'importlib.reload(text_tools).count_words("The cat saw the dog") == {"the": 2, "cat": 1, "saw": 1, "dog": 1} and text_tools.most_common({"the": 4, "cat": 2, "saw": 2}) == "the" and text_tools.most_common({"a": 1, "b": 3, "c": 3}) == "b" and text_tools.most_common({}) is None and text_tools.most_common(text_tools.count_words("b a b a a")) == "a"',
         '''
%%writefile text_tools.py
def count_words(text):
    """문장의 단어별 등장 횟수"""
    word_count = {}
    for word in text.lower().split():
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def most_common(word_count):
    """가장 많이 나온 단어. 비어 있으면 None"""
    best_word = None
    best_count = 0
    for word, count in word_count.items():
        if count > best_count:           # 더 많이 나온 단어를 만나면 바꿔 기억 (같으면 먼저 것 유지)
            best_word = word
            best_count = count
    return best_word
''',
         extra='''
import importlib, text_tools
importlib.reload(text_tools)
word_count = text_tools.count_words("the cat saw the dog and the dog saw the cat")
print(word_count)
print(text_tools.most_common(word_count))
''', extra_raises=True, show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다.<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다. 과제 5를 했다면 `text_tools.py` 도 함께 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
def to_nb(cells):
    out, seen = [], set()
    for i, (ctype, src, meta) in enumerate(cells):
        cid = hashlib.md5(f"w7-{i}-{src}".encode("utf-8")).hexdigest()[:8]
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
    cells = [("markdown", "# 컴퓨팅사고 7주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 강의 노트북 `" + LECTURE + "` 맨 끝 ‘7주차 과제’의 정답 예시입니다. 각 셀은 혼자서 실행됩니다. (과제 5는 `%%writefile` 셀이므로 노트북에서 실행한 뒤 `import text_tools` 로 확인합니다.)", {})]
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

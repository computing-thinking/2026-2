import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 9주차 노트북(강의용 + 과제 정답) 생성 스크립트 — build_w7.py 를 복제해 작성
# 내용 출처: 동영상_ppt 8강_1(클래스와 인스턴스) · 8강_2(상속과 다형성) · 9강_1(외부 라이브러리)
# 사용: python build_w9.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w9.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
LECTURE = "컴퓨팅사고_9주차_클래스.ipynb"
HW_SOL = "컴퓨팅사고_9주차_과제정답.ipynb"

# ───────────────────────── HTML 상자 (7주차 노트북과 같은 값) ─────────────────────────
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
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w9.py 가 사용


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
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 9주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">객체지향 프로그래밍 — 데이터와 함수를 한 묶음으로</div>
<div style="font-size:1.25em;margin-top:6px;">클래스와 인스턴스 &nbsp;·&nbsp; 상속과 다형성 &nbsp;·&nbsp; 모듈과 패키지 시스템 &nbsp;·&nbsp; 외부 라이브러리</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>
</div>
''')

md('''
# 9주차 학습 안내

중간고사 전 7주차에서 코드 조각에 이름을 붙이는 **함수**를 배웠습니다. 함수는 **일(절차)** 에 이름을 붙입니다. 그런데 프로그램에는 일만 있는 것이 아니라 **데이터**도 있습니다. 학생 한 명에게는 이름 · 전공 · 학년이 있고, 그 학생이 하는 일(자기소개, 진급)도 있습니다.
이번 주에는 **데이터와 그 데이터를 다루는 함수를 한 묶음**으로 만드는 방법, **클래스**를 배웁니다. 그리고 남이 만든 클래스와 함수가 어떻게 **모듈 · 패키지 · 라이브러리**로 묶여 우리에게 오는지 봅니다.

| 교시 | 주제 | 핵심 질문 |
|:---:|:---|:---|
| **1교시** | 클래스와 인스턴스 | 학생 한 명의 이름 · 전공 · 학년이 리스트 세 개에 흩어져 있다. 한 덩어리로 다룰 수 없을까? |
| **2교시** | 상속과 다형성 | 비슷한 클래스가 둘이다. 공통 부분을 또 복사해야 하나? |
| **3교시** | 모듈과 패키지 시스템 · 외부 라이브러리 | 남이 만든 수십만 개의 코드 묶음을 어떻게 찾고, 가져오고, 이름이 겹치지 않게 쓰나? |

**오늘 수업을 마치면**

1. `class` 로 클래스를 정의하고, `__init__` 과 `self` 가 무엇인지 설명하며, 인스턴스를 여러 개 만들어 쓸 수 있습니다.
2. 속성과 메서드를 구분하고, 메서드로 객체의 상태를 바꾸며, `__str__` 로 출력 모양을 정할 수 있습니다.
3. 상속으로 공통 부분을 물려받고, 메서드를 재정의(오버라이딩)하며, 다형성이 왜 편리한지 설명할 수 있습니다.
4. 모듈 · 패키지 · 라이브러리의 관계와 `import` 가 모듈을 찾는 순서를 알고, 외부 라이브러리를 설치해 쓰는 흐름을 설명할 수 있습니다.

''' + key("이 노트북을 읽는 법", "회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요. 예상과 다를 때가 가장 많이 배우는 순간입니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 정답 예시는 접혀 있으니 먼저 스스로 풀어 보세요.<br>노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다. 4주차부터 오늘까지 배운 내용으로 푸는 문제입니다."))

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · 클래스와 인스턴스\n\n" + period(1, "데이터와 함수를 한 묶음으로 — 클래스와 인스턴스", [
    "객체가 ‘데이터 + 기능’이라는 것을 이미 써 온 예로 설명한다",
    "class 와 __init__ 으로 클래스를 정의하고 인스턴스를 만든다",
    "self 가 무엇인지 알고, 속성과 메서드를 구분한다",
    "메서드로 객체의 상태를 바꾸고, __str__ 로 출력 모양을 정한다",
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
# import 때마다 캐시를 비우는 작은 장치를 끼워 둡니다. 3교시 '모듈과 패키지'에서 씁니다.
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
## 1-1. 데이터가 흩어져 있으면 — 리스트 세 개의 문제

학생 세 명의 이름 · 전공 · 학년을 저장한다고 합시다. 5주차까지 배운 것으로는 리스트 세 개가 먼저 떠오릅니다.
''')

code('''
names = ["김연세", "이미래", "박원주"]
majors = ["컴퓨터공학", "경영학", "생명과학"]
years = [1, 2, 1]

for i in range(len(names)):
    print(f"{names[i]} ({majors[i]} {years[i]}학년)")
''')

md('''
동작은 합니다. 그런데 이런 일이 생깁니다.

- **한 학생**의 정보가 리스트 세 개에 **흩어져** 있습니다. ‘이미래’를 알려면 세 리스트의 1번을 각각 찾아야 합니다.
- 학생을 한 명 지우면 **세 리스트를 모두** 지워야 합니다. 하나만 빠뜨리면 번호가 밀려 엉뚱한 전공이 붙습니다.
- 학생이 하는 일(자기소개, 진급)은 **리스트 밖의 함수**에 따로 있습니다. 데이터와 일이 떨어져 있습니다.

5주차의 **딕셔너리**로 한 명을 한 덩어리로 묶으면 조금 낫습니다.
''')

code('''
student = {"name": "이미래", "major": "경영학", "year": 2}

def introduce(student):
    return f"{student['name']} ({student['major']} {student['year']}학년)"

print(introduce(student))
student["year"] += 1          # 진급
print(introduce(student))
''')

md('''
데이터는 묶였습니다. 그러나 `introduce` 는 여전히 **밖에** 있습니다. 학생 딕셔너리에 어떤 키가 있어야 하는지, 어떤 함수가 학생용인지는 **사람이 기억**해야 합니다. 키 이름을 `"grade"` 로 잘못 쓰면 `KeyError` 가 날 때까지 아무도 모릅니다.

오늘 배울 **클래스(class)** 는 이 두 가지를 한꺼번에 해결합니다. ① 학생 한 명이 어떤 데이터를 갖는지 **한 곳에 적어 두고**, ② 학생이 하는 일(함수)을 **그 데이터에 붙여 둡니다.** 1교시가 끝나면 위 코드는 이렇게 됩니다.

```python
student = Student("이미래", "경영학", 2)
print(student.introduce())
student.promote()
```

## 1-2. 객체 — 사실 4주차부터 계속 써 왔습니다

Python 에서 값은 모두 **객체(object)** 입니다. 객체는 **데이터**와 그 데이터를 다루는 **기능**을 함께 가진 덩어리입니다. 문자열 `"hello"` 는 글자 다섯 개(데이터)를 갖고 있고, 대문자로 바꾸는 기능 `upper()` 도 갖고 있습니다.
''')

code('''
word = "hello"
print(word.upper())          # 문자열 객체가 가진 기능 — 4주차
scores = [72, 88, 95]
scores.append(60)            # 리스트 객체가 가진 기능 — 5주차
print(scores, len(scores))
print(type(word), type(scores))
''')

md('''
`word.upper()` 처럼 **객체 이름 뒤에 점(`.`)을 찍고 부르는 함수**를 **메서드(method)** 라고 합니다. 4주차부터 `.upper()`, `.split()`, `.append()`, `.get()` 을 쓸 때마다 메서드를 부르고 있었습니다. 7주차의 함수와 다른 점은 **어느 객체의 것인지가 점 앞에 보인다**는 것뿐입니다.

`type(word)` 가 `<class 'str'>` 이라고 답합니다. `"hello"` 는 **`str` 클래스로 만든 객체**라는 뜻입니다. `[72, 88, 95]` 는 `list` 클래스로 만든 객체입니다. 즉, 지금까지 쓴 모든 값은 누군가 만들어 둔 **클래스로 찍어 낸 것**이었습니다. 오늘은 그 클래스를 **내가** 만듭니다.

| 용어 | 뜻 | 예 |
|:---|:---|:---|
| **클래스**(class) | 객체의 **설계도**. 어떤 데이터와 기능을 갖는지 적어 둔 코드 | `str`, `list`, 오늘 만들 `Student` |
| **인스턴스**(instance) | 설계도로 **실제로 만든** 객체 하나 | `"hello"`, `[72, 88]`, `Student("이미래", …)` |
| **속성**(attribute) | 객체가 가진 **데이터**. `객체.이름` 으로 읽습니다 | `student.name` |
| **메서드**(method) | 객체가 가진 **함수**. `객체.이름()` 으로 부릅니다 | `word.upper()`, `student.introduce()` |

붕어빵 **틀**이 클래스, 틀로 찍어 낸 붕어빵 하나하나가 인스턴스입니다. 틀은 하나지만 붕어빵은 몇 개든 만들 수 있고, 팥 · 슈크림처럼 속(데이터)은 저마다 다릅니다. ‘객체’와 ‘인스턴스’는 거의 같은 말입니다. 설계도를 강조할 때 “`Student` 의 인스턴스”라고 부릅니다.

## 1-3. 클래스 정의하기 — `class` 와 `__init__`

```
class 클래스이름:
    def __init__(self, 매개변수1, 매개변수2):
        self.속성1 = 매개변수1
        self.속성2 = 매개변수2

    def 메서드이름(self):
        실행할 문장
```

| 조각 | 뜻 |
|:---|:---|
| `class 이름:` | 클래스를 정의하는 키워드. 이름은 **대문자로 시작**하는 관습입니다: `Student`, `BankAccount` |
| `def __init__(self, …):` | 인스턴스를 **만들 때 자동으로 실행**되는 특별한 메서드. 앞뒤에 밑줄 두 개(`__`)입니다. ‘초기화(initialize)’의 줄임말 |
| `self` | **지금 만들어지는(또는 호출된) 그 인스턴스 자신.** 모든 메서드의 첫 매개변수입니다 |
| `self.name = name` | 인스턴스에 `name` 이라는 **속성을 만들고** 값을 넣습니다 |

가장 단순한 클래스부터 만듭니다.

**예상해 보기** — 아래 셀을 실행하면 화면에 무엇이 나올까요? (7주차의 `def` 를 떠올리세요.)
''')

code('''
class Student:
    def __init__(self, name, major, year):
        self.name = name        # 속성 name 을 만들고 값을 넣습니다
        self.major = major
        self.year = year
''')

md('''
**아무것도 나오지 않습니다.** `def` 가 함수를 기억만 하듯, `class` 도 설계도를 **기억만** 합니다. 붕어빵 틀을 만든 것이지 붕어빵을 구운 것이 아닙니다.

## 1-4. 인스턴스 만들기 — 클래스 이름을 함수처럼 부릅니다

클래스 이름 뒤에 괄호를 붙여 **호출**하면 인스턴스가 하나 만들어집니다. 괄호 안의 값은 `__init__` 의 `self` **다음** 매개변수로 들어갑니다. `self` 자리는 Python 이 **방금 만든 인스턴스를 자동으로** 넣어 줍니다.
''')

code('''
s1 = Student("김연세", "컴퓨터공학", 1)     # __init__(s1, "김연세", "컴퓨터공학", 1) 이 자동으로 실행됩니다
s2 = Student("이미래", "경영학", 2)

print(s1.name, s1.major, s1.year)         # 속성 읽기 — 객체.속성
print(s2.name, s2.major, s2.year)
print(type(s1))
''')

md('''
`s1` 과 `s2` 는 같은 틀로 만들었지만 **서로 다른 붕어빵**입니다. 속성 값이 따로 있습니다. 1-1의 리스트 세 개가 **인스턴스 하나 안에** 들어왔습니다. `s1.name` 처럼 점으로 읽으니 `names[0]` 보다 뜻도 분명합니다.

속성은 변수처럼 **바꿀 수** 있습니다.
''')

code('''
s1.year = 2                 # 속성에 대입 — 진급
s1.email = "yonsei@example.com"   # 없던 속성도 붙일 수 있습니다 (권장하지는 않습니다 — __init__ 에 모아 두세요)
print(s1.year, s1.email)
''')

md(boom("없는 속성을 읽으면?"))

code('''
print(s2.email)
''', raises=True)

md('''
`AttributeError: 'Student' object has no attribute 'email'` — “`Student` 객체에 `email` 이라는 속성이 없다”는 안내입니다. `s1` 에만 붙인 속성이라 `s2` 에는 없습니다. 모든 인스턴스가 같은 속성을 갖게 하려면 **`__init__` 안에서** 만듭니다. 그래서 `__init__` 이 ‘이 클래스의 인스턴스는 이런 데이터를 갖는다’는 **목록** 역할을 합니다.
''')

md(key("클래스는 설계도, 인스턴스는 제품", "① `class` 는 기억만 합니다. `클래스이름(인자)` 로 호출해야 인스턴스가 만들어집니다.<br>② 만들 때 `__init__` 이 자동으로 실행되어 속성을 채웁니다. 괄호의 인자는 `self` 다음 자리부터 들어갑니다.<br>③ 인스턴스마다 속성 값이 따로 있습니다. `객체.속성` 으로 읽고 씁니다.<br>④ 인스턴스가 가져야 할 속성은 모두 `__init__` 에 적어 둡니다."))

md('''
## 1-5. 메서드 — 클래스 안에 정의한 함수, 그리고 `self`

이제 학생이 **하는 일**을 클래스 안에 넣습니다. 클래스 안의 `def` 는 7주차의 함수와 같습니다. 단 하나, **첫 매개변수가 `self`** 입니다.
''')

code('''
class Student:
    def __init__(self, name, major, year):
        self.name = name
        self.major = major
        self.year = year

    def introduce(self):                      # 메서드 — 첫 매개변수는 늘 self
        return f"{self.name} ({self.major} {self.year}학년)"

s1 = Student("김연세", "컴퓨터공학", 1)
s2 = Student("이미래", "경영학", 2)
print(s1.introduce())                        # 괄호가 비어 있는데 self 는 누가 줄까요?
print(s2.introduce())
''')

md('''
`s1.introduce()` 의 괄호는 비어 있는데 `introduce(self)` 는 매개변수가 하나입니다. 어떻게 된 걸까요?

**점 앞의 객체가 `self` 로 들어갑니다.** `s1.introduce()` 는 Python 이 `Student.introduce(s1)` 으로 바꿔 실행합니다. 그래서 메서드 안에서 `self.name` 은 `s1.name`, 즉 “**이 학생의** 이름”이 됩니다. `s2.introduce()` 에서는 `self` 가 `s2` 입니다.

1-1의 `introduce(student)` 와 비교해 보세요. 함수 밖에서 딕셔너리를 **넘겨주던** 것이, 점 앞에 **붙어서** 들어가는 것으로 바뀌었을 뿐입니다. `self` 는 ‘그 딕셔너리’ 자리입니다.
''')

code('''
print(Student.introduce(s1))      # s1.introduce() 와 똑같습니다 — self 자리에 s1 을 직접 넣은 것
''')

md(boom("self 를 빠뜨리면?"))

code('''
class Student:
    def __init__(self, name):
        self.name = name

    def introduce():                 # self 가 없습니다
        return "안녕하세요"

s = Student("김연세")
s.introduce()
''', raises=True)

md('''
`TypeError: Student.introduce() takes 0 positional arguments but 1 was given` — “인자를 받지 않는 메서드인데 하나가 들어왔다”는 안내입니다. 그 하나가 Python 이 자동으로 넣은 `s` 입니다. 메서드를 정의할 때 **`self` 를 빠뜨렸다**는 뜻이니, 이 메시지를 보면 `def` 줄의 괄호를 보세요. 오늘 가장 자주 만날 오류입니다.

`self` 라는 이름 자체는 관습입니다. 다른 이름을 써도 동작하지만 **모든 Python 코드가 `self` 를 쓰므로** 우리도 그렇게 씁니다.

## 1-6. 상태를 바꾸는 메서드

메서드 안에서 `self.속성 = …` 로 대입하면 **그 인스턴스의 데이터가 바뀝니다.** 함수가 끝나도 사라지지 않습니다. 7주차의 지역 변수와 다른 점입니다. `self` 에 붙은 것은 인스턴스가 **살아 있는 동안** 남습니다.

**예상해 보기** — 두 번째 `introduce()` 는 몇 학년이라고 할까요?
''')

code('''
class Student:
    def __init__(self, name, major, year):
        self.name = name
        self.major = major
        self.year = year
        self.scores = []                       # 인자로 받지 않은 속성도 __init__ 에서 만들 수 있습니다

    def introduce(self):
        return f"{self.name} ({self.major} {self.year}학년)"

    def promote(self):                         # 상태를 바꾸는 메서드 — 돌려주는 값은 없습니다
        self.year += 1

    def add_score(self, score):
        self.scores.append(score)

    def average(self):                         # 자기 데이터로 계산해 돌려주는 메서드
        if len(self.scores) == 0:
            return 0
        return sum(self.scores) / len(self.scores)

s1 = Student("김연세", "컴퓨터공학", 1)
print(s1.introduce())
s1.promote()
print(s1.introduce())

s1.add_score(88)
s1.add_score(95)
print(s1.scores, s1.average())
''')

md('''
1-1의 딕셔너리 버전과 비교하면, 데이터(`name`, `major`, `year`, `scores`)와 그 데이터를 다루는 일(`introduce`, `promote`, `add_score`, `average`)이 **한 곳**에 모였습니다. `Student` 클래스를 읽으면 ‘학생이란 무엇이고 무엇을 할 수 있는가’가 **전부** 보입니다.

메서드도 7주차 함수의 규칙을 그대로 따릅니다. `promote` 처럼 상태만 바꾸는 메서드는 `return` 이 없고, `average` 처럼 계산하는 메서드는 `return` 합니다. `s1.average()` 가 `None` 이면 `return` 을 빠뜨린 것입니다.

## 1-7. 출력 모양 정하기 — `__str__`

**예상해 보기** — `print(s1)` 은 무엇을 출력할까요?
''')

code('''
print(s1)
''')

md('''
`<__main__.Student object at 0x…>` — “`Student` 객체가 메모리 어딘가에 있다”는, 사람에게는 쓸모없는 문장입니다. `print` 는 객체를 문자열로 바꿔 보여 주는데, 우리 클래스에는 **문자열로 바꾸는 법**이 아직 없기 때문입니다.

그 방법을 알려 주는 특별한 메서드가 `__str__` 입니다. `print(객체)` 나 `f"{객체}"` 는 이 메서드를 불러 **돌려준 문자열**을 씁니다.
''')

code('''
class Student:
    def __init__(self, name, major, year):
        self.name = name
        self.major = major
        self.year = year

    def __str__(self):                         # print() 가 이 메서드의 결과를 씁니다
        return f"{self.name} ({self.major} {self.year}학년)"

s1 = Student("김연세", "컴퓨터공학", 1)
print(s1)
print(f"학생: {s1}")
students = [Student("김연세", "컴퓨터공학", 1), Student("이미래", "경영학", 2), Student("박원주", "생명과학", 1)]
for s in students:
    print(s)
''')

md(note("밑줄 두 개로 둘러싼 이름 — 특별 메서드", "`__init__`, `__str__` 처럼 앞뒤에 밑줄 두 개가 붙은 메서드는 Python 이 <b>정해진 순간에 자동으로 부르는</b> 약속된 이름입니다. 만들 때는 `__init__`, 문자열로 바꿀 때는 `__str__`. 이 밖에도 `+` 를 만났을 때의 `__add__`, `len()` 을 만났을 때의 `__len__`, `==` 를 만났을 때의 `__eq__` 등이 있습니다. 4주차에 `\"a\" + \"b\"` 와 `1 + 2` 가 다르게 동작한 것도 `str` 과 `int` 의 `__add__` 가 다르기 때문입니다. 이름이 있다는 것만 알아 두세요. 수업에서는 `__init__` 과 `__str__` 두 개만 씁니다."))

md('''
## 1-8. 예제 — 7주차의 숫자 맞히기 게임을 클래스로

7주차 2-8에서 게임을 `read_guess` · `judge` · `play_game` 세 함수로 쪼갰습니다. 그때 정답 `answer` 와 시도 횟수 `tries` 는 `play_game` 의 **지역 변수**라 다른 함수가 볼 수 없었고, 그래서 `judge(guess, answer)` 처럼 매번 넘겨주어야 했습니다.

클래스로 만들면 **정답과 횟수가 게임 객체의 속성**이 됩니다. 메서드는 `self` 로 언제든 꺼내 볼 수 있으니 넘겨줄 필요가 없습니다.
''')

code('''
import random

class NumberGame:
    def __init__(self, answer=None):
        if answer is None:                       # 정답을 안 주면 무작위로 — 주면 그 값 (시험할 때 편합니다)
            answer = random.randint(1, 100)
        self.answer = answer
        self.tries = 0

    def guess(self, number):
        """수를 하나 받아 판정 문장을 돌려주고, 시도 횟수를 하나 올립니다."""
        self.tries += 1
        if number > self.answer:
            return "정답보다 큰 수입니다"
        elif number < self.answer:
            return "정답보다 작은 수입니다"
        return f"정답! {self.tries}번 만에 맞혔습니다"

game = NumberGame(answer=30)        # 정답을 정해 두고 시험
print(game.guess(50))
print(game.guess(10))
print(game.guess(30))
print(game.tries, "번 시도")
''')

md('''
`input()` 이 없어도 게임의 **규칙**은 전부 시험할 수 있습니다. 화면과 입력은 바깥에서 붙입니다. 실제로 해 보고 싶으면 아래 셀을 실행하세요. (실행할 때마다 정답이 달라집니다.)
''')

code('''
game = NumberGame()                 # 정답은 무작위
while True:
    message = game.guess(int(input("1 ~ 100 사이의 수를 맞혀 보세요: ")))
    print(message)
    if message.startswith("정답"):
        break
''')

md(key("1-5 ~ 1-8 정리", "① 메서드는 클래스 안의 함수입니다. 첫 매개변수 `self` 에 <b>점 앞의 객체</b>가 자동으로 들어갑니다.<br>② `self.속성 = 값` 은 그 인스턴스의 데이터를 바꿉니다. 함수가 끝나도 남습니다.<br>③ `__str__` 이 돌려주는 문자열을 `print()` 가 씁니다.<br>④ 함수끼리 값을 넘겨주던 것이 객체 안에서는 `self.속성` 으로 <b>공유</b>됩니다. 그래서 ‘게임의 상태’처럼 여러 함수가 함께 쓰는 데이터는 클래스로 묶기 좋습니다."))

# ── 1교시 실습 ──
practice("✏️ 실습 1-1", "원 클래스", "약 4분",
         "`Circle` 클래스를 정의하세요.<br>① `__init__(self, radius)` — 반지름을 속성 `radius` 에 저장합니다.<br>② `area(self)` — 넓이 `math.pi * radius ** 2` 를 돌려줍니다.<br>③ `circumference(self)` — 둘레 `2 * math.pi * radius` 를 돌려줍니다.<br>`Circle(1).area()` → `3.141592…`, `Circle(2).circumference()` → `12.566…`",
         '''
import math

# 여기에 Circle 클래스를 정의하세요


c = Circle(2)
print(c.radius, c.area(), c.circumference())
''',
         "abs(Circle(1).area() - 3.141592653589793) < 1e-9 and abs(Circle(2).area() - 12.566370614359172) < 1e-9 and abs(Circle(2).circumference() - 12.566370614359172) < 1e-9 and Circle(3).radius == 3",
         '''
import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def circumference(self):
        return 2 * math.pi * self.radius

c = Circle(2)
print(c.radius, c.area(), c.circumference())     # 2 12.566370614359172 12.566370614359172
''', raises=True, heading="## 1교시 실습")

practice("✏️ 실습 1-2", "학생 클래스 — 자기소개와 진급", "약 5분",
         "1-6의 `Student` 를 보지 않고 직접 써 보세요.<br>① `__init__(self, name, major, year)` — 세 속성을 저장합니다.<br>② `introduce(self)` — `\"이미래 (경영학 2학년)\"` 모양의 문자열을 <b>돌려줍니다.</b><br>③ `promote(self)` — `year` 를 1 올립니다. 돌려주는 값은 없습니다.<br>④ `__str__(self)` — `introduce()` 와 같은 문자열을 돌려줍니다. (② 를 그대로 호출해도 됩니다: `return self.introduce()`)",
         '''
# 여기에 Student 클래스를 정의하세요


s = Student("이미래", "경영학", 2)
print(s.introduce())
s.promote()
print(s)
''',
         '(lambda s: s.introduce() == "이미래 (경영학 2학년)" and (s.promote() or True) and s.year == 3 and str(s) == "이미래 (경영학 3학년)" and Student("김연세", "컴퓨터공학", 1).introduce() == "김연세 (컴퓨터공학 1학년)")(Student("이미래", "경영학", 2))',
         '''
class Student:
    def __init__(self, name, major, year):
        self.name = name
        self.major = major
        self.year = year

    def introduce(self):
        return f"{self.name} ({self.major} {self.year}학년)"

    def promote(self):
        self.year += 1

    def __str__(self):
        return self.introduce()

s = Student("이미래", "경영학", 2)
print(s.introduce())       # 이미래 (경영학 2학년)
s.promote()
print(s)                   # 이미래 (경영학 3학년)
''', raises=True)

practice("✏️ 실습 1-3", "계수기 클래스 — 상태를 가진 객체", "약 4분",
         "누른 횟수를 세는 `Counter` 클래스를 정의하세요.<br>① `__init__(self)` — 속성 `count` 를 0 으로 시작합니다. 인자는 없습니다.<br>② `click(self)` — `count` 를 1 올리고, 올린 뒤의 값을 <b>돌려줍니다.</b><br>③ `reset(self)` — `count` 를 0 으로 되돌립니다.<br>계수기 두 개를 만들면 서로 <b>독립</b>이어야 합니다. `a` 를 세 번 눌러도 `b.count` 는 0 입니다.",
         '''
# 여기에 Counter 클래스를 정의하세요


a = Counter()
b = Counter()
a.click(); a.click(); print(a.click())
print(a.count, b.count)
a.reset()
print(a.count)
''',
         '(lambda a, b: a.click() == 1 and a.click() == 2 and b.click() == 1 and a.count == 2 and b.count == 1 and (a.reset() or True) and a.count == 0 and b.count == 1)(Counter(), Counter())',
         '''
class Counter:
    def __init__(self):
        self.count = 0

    def click(self):
        self.count += 1
        return self.count

    def reset(self):
        self.count = 0

a = Counter()
b = Counter()
a.click(); a.click(); print(a.click())     # 3
print(a.count, b.count)                    # 3 0
a.reset()
print(a.count)                             # 0
''', raises=True)

md(key("1교시 정리", "① 객체 = 데이터(속성) + 기능(메서드). 4주차부터 쓴 문자열 · 리스트도 모두 객체입니다.<br>② 클래스는 설계도, 인스턴스는 그 설계도로 만든 제품. `클래스이름(인자)` 로 만들면 `__init__` 이 자동 실행됩니다.<br>③ 메서드의 첫 매개변수 `self` 는 점 앞의 객체 자신. `self.속성` 으로 자기 데이터를 읽고 씁니다.<br>④ `__str__` 로 `print()` 모양을 정합니다.<br>⑤ 오늘의 질문에 대한 답 — 리스트 세 개로 흩지 않습니다. <b>데이터와 그 데이터를 다루는 함수를 한 클래스에 모읍니다.</b>") + "\n\n" + BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · 상속과 다형성\n\n" + period(2, "공통 부분을 물려받다 — 상속과 다형성", [
    "상속으로 부모 클래스의 속성과 메서드를 물려받는다",
    "super() 로 부모의 __init__ 을 부르고, 자식에 속성과 메서드를 더한다",
    "메서드 오버라이딩으로 부모의 동작을 바꾼다",
    "다형성 — 같은 이름의 메서드를 여러 클래스가 각자 다르게 구현하면 무엇이 편한지 설명한다",
]))

md('''
## 2-1. 비슷한 클래스가 둘 — 또 복사해야 하나?

학생 클래스 옆에 **교수** 클래스가 필요해졌습니다. 교수도 이름이 있고 자기소개를 합니다. 다른 점은 전공 · 학년 대신 **학과**와 **연구실**이 있다는 것뿐입니다.

`Student` 를 복사해 `Professor` 를 만들면 7주차 1-1에서 본 문제가 그대로 돌아옵니다. `introduce` 의 인사말을 바꾸면 두 클래스를 모두 고쳐야 합니다. 사람 · 학생 · 교수 · 직원 … 종류가 늘수록 복사본도 늘어납니다.

**공통 부분을 한 번만 쓰고 물려받는** 방법이 **상속(inheritance)** 입니다. 먼저 공통 부분만 가진 **부모 클래스** `Person` 을 만듭니다.
''')

code('''
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"안녕하세요, {self.name}입니다"

    def __str__(self):
        return self.name
''')

md('''
자식 클래스는 `class 자식이름(부모이름):` 으로 만듭니다. 괄호 안이 **누구에게서 물려받는지**입니다.

**예상해 보기** — `Student` 안에는 아무것도 없는데(`pass`), `s.introduce()` 가 될까요?
''')

code('''
class Student(Person):          # Person 을 물려받습니다
    pass                        # 아직 아무것도 더하지 않았습니다

s = Student("김연세")
print(s.name)
print(s.introduce())
print(type(s))
''')

md('''
됩니다. `Student` 에 `__init__` 도 `introduce` 도 없지만, **부모 `Person` 의 것을 그대로 물려받았습니다.** 객체에서 속성이나 메서드를 찾을 때 Python 은 ① 그 객체 → ② 그 클래스 → ③ 부모 클래스 순서로 올라가며 찾습니다.

부모를 **상위 클래스(superclass) · 기반 클래스**, 자식을 **하위 클래스(subclass) · 파생 클래스**라고도 부릅니다. 뜻은 모두 같습니다. ‘학생**은** 사람**이다**(a Student **is a** Person)’가 성립할 때 상속을 씁니다.

## 2-2. 자식에서 더하기 — `super().__init__()`

학생에게는 전공과 학년이 **더** 있습니다. 자식 클래스에 자기만의 `__init__` 을 쓰되, 이름 저장은 **부모에게 맡깁니다.** 부모의 메서드를 부르는 이름이 `super()` 입니다.
''')

code('''
class Student(Person):
    def __init__(self, name, major, year):
        super().__init__(name)          # 부모의 __init__ 을 불러 name 을 저장하게 합니다
        self.major = major              # 학생만의 속성을 더합니다
        self.year = year

    def promote(self):                  # 학생만의 메서드
        self.year += 1

s = Student("김연세", "컴퓨터공학", 1)
print(s.name, s.major, s.year)         # name 은 부모가, major · year 는 자식이 채웠습니다
print(s.introduce())                   # introduce 는 여전히 부모의 것
s.promote()
print(s.year)
''')

md(boom("super().__init__() 을 빠뜨리면?"))

code('''
class Student(Person):
    def __init__(self, name, major, year):
        self.major = major              # name 을 저장하는 줄이 없습니다
        self.year = year

s = Student("김연세", "컴퓨터공학", 1)
print(s.introduce())
''', raises=True)

md('''
`AttributeError: 'Student' object has no attribute 'name'` — 자식이 `__init__` 을 **새로** 쓰면 부모의 `__init__` 은 **자동으로 실행되지 않습니다.** 그래서 `name` 속성이 만들어지지 않았고, 부모의 `introduce` 가 `self.name` 을 찾다 실패했습니다. 자식 `__init__` 의 첫 줄은 거의 늘 `super().__init__(…)` 입니다.

## 2-3. 부모의 동작을 바꾸기 — 오버라이딩

학생의 자기소개에는 전공도 들어가야 합니다. 자식 클래스에 **같은 이름의 메서드**를 다시 쓰면 자식의 것이 부모의 것을 **덮어씁니다.** 이것을 **오버라이딩(overriding, 재정의)** 이라고 합니다.
''')

code('''
class Professor(Person):
    def __init__(self, name, department, office):
        super().__init__(name)
        self.department = department
        self.office = office

    def introduce(self):                                   # 부모의 introduce 를 덮어씁니다
        return super().introduce() + f". {self.department} 교수이고 연구실은 {self.office}입니다"

class Student(Person):
    def __init__(self, name, major, year):
        super().__init__(name)
        self.major = major
        self.year = year

    def introduce(self):                                   # 학생도 자기 식으로
        return super().introduce() + f". {self.major} {self.year}학년입니다"

p = Person("박원주")
s = Student("김연세", "컴퓨터공학", 1)
prof = Professor("윤교수", "AI융합과학원", "컨113호")
print(p.introduce())
print(s.introduce())
print(prof.introduce())
''')

md('''
세 가지를 보세요.

- `Student.introduce` 안에서 `super().introduce()` 로 **부모의 인사말을 재사용**한 뒤 덧붙였습니다. 부모의 것을 완전히 버리고 새로 써도 됩니다.
- 인사말 “안녕하세요, …입니다”를 바꾸고 싶으면 **`Person` 한 곳만** 고치면 학생 · 교수 모두 바뀝니다. 오늘의 질문에 대한 답입니다.
- `__init__` 을 자식에서 새로 쓴 것도 사실 오버라이딩입니다. 그래서 부모의 것을 쓰려면 `super().__init__()` 을 **직접** 불러야 했습니다.

## 2-4. 다형성 — 같은 이름, 다른 동작

위 셀의 마지막 세 줄을 보세요. `p`, `s`, `prof` 는 **클래스가 다른데** 모두 `.introduce()` 한 가지로 불렀고, 각자 **자기 방식**으로 답했습니다. 호출하는 쪽은 상대가 학생인지 교수인지 **몰라도 됩니다.**

이렇게 **같은 이름의 메서드가 객체의 종류에 따라 다르게 동작하는 것**을 **다형성(polymorphism)** 이라고 합니다. ‘여러(poly) 모양(morph)’이라는 뜻입니다.

**예상해 보기** — 아래 `for` 문은 무엇을 출력할까요?
''')

code('''
class Animal:
    def __init__(self, name):
        self.name = name

    def talk(self):
        return "..."                     # 부모는 기본 동작만

class Cat(Animal):
    def talk(self):
        return "야옹"

class Dog(Animal):
    def talk(self):
        return "멍멍"

animals = [Cat("나비"), Dog("바둑이"), Cat("까망이"), Animal("정체불명")]
for animal in animals:
    print(f"{animal.name}: {animal.talk()}")      # 종류를 묻지 않습니다 — 각자 알아서 답합니다
''')

md('''
`for` 문은 `if type(animal) == Cat: … elif type(animal) == Dog: …` 같은 분기가 **없습니다.** 각 객체가 자기 `talk` 를 알고 있으니, 부르는 쪽은 한 줄이면 됩니다. 나중에 `Cow` 클래스를 더해도 **`for` 문은 고치지 않습니다.** 새 클래스에 `talk` 만 쓰면 됩니다.

사실 다형성도 이미 써 왔습니다. `len("hello")` 와 `len([1, 2, 3])` — 문자열과 리스트는 길이를 **다른 방법**으로 세지만, 부르는 쪽은 `len()` 하나입니다. `1 + 2` 와 `"a" + "b"` 도 같은 `+` 로 다른 일을 합니다.
''')

md(key("상속과 다형성 정리", "① `class 자식(부모):` — 부모의 속성과 메서드를 <b>물려받습니다.</b> ‘자식은 부모이다’가 성립할 때 씁니다.<br>② 자식 `__init__` 의 첫 줄은 `super().__init__(…)`. 부모가 자기 속성을 채우게 합니다.<br>③ 같은 이름의 메서드를 자식에 다시 쓰면 <b>오버라이딩</b>. `super().메서드()` 로 부모 것을 재사용할 수 있습니다.<br>④ <b>다형성</b> — 종류가 달라도 같은 이름으로 부르면 각자 알아서 동작합니다. 부르는 쪽의 `if` 가 사라집니다."))

md('''
## 2-5. 객체의 종류 묻기 — `isinstance()` 와 모든 클래스의 조상 `object`

종류를 꼭 확인해야 할 때는 `type()` 보다 `isinstance(객체, 클래스)` 를 씁니다. **부모 클래스에 대해서도 `True`** 를 주기 때문입니다. 학생은 학생이면서 사람입니다.
''')

code('''
s = Student("김연세", "컴퓨터공학", 1)
print(isinstance(s, Student), isinstance(s, Person), isinstance(s, Professor))
print(isinstance(s, object), isinstance("hello", object), isinstance(3, object))
print(Student.__bases__, Person.__bases__)        # 각 클래스의 부모
''')

md('''
`Person` 은 부모를 적지 않았는데 `Person.__bases__` 가 `(<class 'object'>,)` 입니다. **부모를 적지 않은 클래스는 자동으로 `object` 를 물려받습니다.** `object` 는 모든 클래스의 조상입니다. 그래서 `"hello"` 도 `3` 도 우리 `Student` 도 모두 `object` 의 인스턴스입니다. 1-7의 `<__main__.Student object at …>` 라는 기본 출력도 `object` 가 물려준 `__str__` 이 만든 것이었습니다. 우리가 `__str__` 을 쓴 것은 그것을 **오버라이딩**한 것입니다.

다른 사람의 코드에서 `class Person(object):` 라고 쓴 것을 자주 봅니다. `class Person:` 과 같은 뜻입니다.

## 2-6. 안을 감추기 — 캡슐화

7주차에서 함수는 **블랙박스**라고 했습니다. 안을 몰라도 ‘무엇을 넣으면 무엇이 나오는지’만 알면 쓸 수 있었습니다. 객체도 같습니다. 객체의 **세부 구현은 감추고 메서드만으로 쓰게 하는 것**을 **캡슐화(encapsulation)** 라고 합니다.

은행 계좌를 생각해 봅시다. 잔액은 `deposit()` · `withdraw()` 로만 바뀌어야 합니다. 밖에서 `account.balance = -1000000` 처럼 **직접 고치면** 규칙이 깨집니다.

Python 은 속성 이름을 **밑줄 두 개(`__`)로 시작**하면 밖에서 그 이름으로 **접근하지 못하게** 합니다.
''')

code('''
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance                 # 밖에서 직접 못 건드리는 속성

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:              # 규칙 — 잔액보다 많이 뺄 수 없습니다
            return False
        self.__balance -= amount
        return True

    def get_balance(self):                       # 읽는 길은 메서드로 열어 둡니다
        return self.__balance

acc = BankAccount("김연세", 1000)
acc.deposit(500)
print(acc.withdraw(2000), acc.withdraw(300))
print(acc.get_balance())
''')

md(boom("감춘 속성을 밖에서 읽으면?"))

code('''
print(acc.__balance)
''', raises=True)

md('''
`AttributeError: 'BankAccount' object has no attribute '__balance'` — 밖에서는 **없는 속성**처럼 보입니다. 잔액은 `get_balance()` 로 읽고 `deposit()` · `withdraw()` 로만 바꿀 수 있습니다. 규칙이 **클래스 안에서만** 지켜지면 되니, 쓰는 사람이 실수할 길이 줄어듭니다.

<details><summary><b>📎 더 알아보기 — 완전히 감춰지는 것은 아닙니다 · <code>@property</code></b></summary>

Python 은 `__balance` 를 `_BankAccount__balance` 라는 이름으로 **바꿔 저장**할 뿐입니다(이름 뒤섞기, name mangling). `acc._BankAccount__balance` 로는 읽힙니다. 자물쇠라기보다 ‘건드리지 마시오’ 표지판입니다. 그래서 Python 에서는 밑줄 **하나**(`_balance`)만 붙여 “내부용이니 직접 쓰지 마세요”라고 표시하는 관습도 널리 쓰입니다.

`get_balance()` 대신 속성처럼 읽게 하고 싶으면 `@property` 를 붙입니다.

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance

    @property
    def balance(self):                 # acc.balance 라고 괄호 없이 읽습니다. 대입은 안 됩니다
        return self.__balance
```

`acc.balance` → `1200`, `acc.balance = 0` → `AttributeError`. 읽기는 열고 쓰기는 막는 것입니다. 수업에서는 `get_…()` 메서드로 충분합니다.

</details>

<details><summary><b>📎 더 알아보기 — 클래스 변수: 모든 인스턴스가 함께 쓰는 값</b></summary>

`__init__` 안에서 `self.` 로 만든 속성은 인스턴스마다 **따로** 있습니다(인스턴스 변수). 클래스 몸통에 **직접** 쓴 변수는 모든 인스턴스가 **함께** 씁니다(클래스 변수). 만든 인스턴스의 수를 세거나, 모든 계좌에 같은 이자율을 둘 때 씁니다.

```python
class BankAccount:
    interest_rate = 0.02          # 클래스 변수 — 모든 계좌가 공유
    count = 0

    def __init__(self, owner, balance=0):
        self.owner = owner        # 인스턴스 변수 — 계좌마다 따로
        self.__balance = balance
        BankAccount.count += 1    # 클래스 이름으로 접근

a = BankAccount("김연세"); b = BankAccount("이미래")
print(BankAccount.count, a.interest_rate, b.interest_rate)     # 2 0.02 0.02
```

</details>
''')

md(key("2-5 ~ 2-6 정리", "① `isinstance(객체, 클래스)` 는 부모 클래스에 대해서도 `True`. 모든 클래스의 조상은 `object`.<br>② 캡슐화 — 세부는 감추고 메서드로만 쓰게 합니다. `__이름` 속성은 밖에서 보이지 않습니다.<br>③ 함수가 블랙박스였듯 객체도 블랙박스입니다. 쓰는 사람은 <b>메서드 이름과 인자</b>만 알면 됩니다."))

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "상속 — Person 에서 Student 로", "약 5분",
         "아래 `Person` 은 그대로 두고, 이를 물려받는 `Student` 를 정의하세요.<br>① `__init__(self, name, major)` — `super().__init__(name)` 으로 이름을 맡기고 `major` 를 더합니다.<br>② `introduce(self)` 를 오버라이딩 — 부모의 인사말 뒤에 `\". 전공은 컴퓨터공학입니다\"` 를 붙여 돌려줍니다. `super().introduce()` 를 쓰세요.<br>`Student(\"김연세\", \"컴퓨터공학\").introduce()` → `\"안녕하세요, 김연세입니다. 전공은 컴퓨터공학입니다\"`",
         '''
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"안녕하세요, {self.name}입니다"

# 여기에 Student 클래스를 정의하세요


s = Student("김연세", "컴퓨터공학")
print(s.introduce())
print(isinstance(s, Person))
''',
         'Student("김연세", "컴퓨터공학").introduce() == "안녕하세요, 김연세입니다. 전공은 컴퓨터공학입니다" and Student("이미래", "경영학").major == "경영학" and isinstance(Student("a", "b"), Person) and Person("박원주").introduce() == "안녕하세요, 박원주입니다"',
         '''
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"안녕하세요, {self.name}입니다"

class Student(Person):
    def __init__(self, name, major):
        super().__init__(name)
        self.major = major

    def introduce(self):
        return super().introduce() + f". 전공은 {self.major}입니다"

s = Student("김연세", "컴퓨터공학")
print(s.introduce())       # 안녕하세요, 김연세입니다. 전공은 컴퓨터공학입니다
print(isinstance(s, Person))   # True
''', raises=True, heading="## 2교시 실습")

practice("✏️ 실습 2-2", "다형성 — 도형의 넓이 합계", "약 6분",
         "① 부모 `Shape` — `area(self)` 가 `0` 을 돌려줍니다.<br>② `Rectangle(Shape)` — `__init__(self, width, height)`, `area()` 는 `width * height`.<br>③ `Circle(Shape)` — `__init__(self, radius)`, `area()` 는 `math.pi * radius ** 2`.<br>④ 함수 `total_area(shapes)` — 도형 리스트를 받아 넓이의 합을 돌려줍니다. <b>종류를 묻지 않고</b> `shape.area()` 만 부릅니다.<br>`total_area([Rectangle(3, 4), Circle(1)])` → `12 + 3.14159… = 15.14159…`",
         '''
import math

# 여기에 Shape, Rectangle, Circle 클래스와 total_area 함수를 정의하세요


shapes = [Rectangle(3, 4), Circle(1), Rectangle(2, 2)]
for shape in shapes:
    print(type(shape).__name__, shape.area())
print(total_area(shapes))
''',
         "abs(total_area([Rectangle(3, 4), Circle(1)]) - (12 + math.pi)) < 1e-9 and Rectangle(2, 5).area() == 10 and abs(Circle(2).area() - 4 * math.pi) < 1e-9 and Shape().area() == 0 and total_area([]) == 0 and isinstance(Circle(1), Shape)",
         '''
import math

class Shape:
    def area(self):
        return 0

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

def total_area(shapes):
    total = 0
    for shape in shapes:
        total += shape.area()          # 사각형인지 원인지 묻지 않습니다
    return total

shapes = [Rectangle(3, 4), Circle(1), Rectangle(2, 2)]
for shape in shapes:
    print(type(shape).__name__, shape.area())
print(total_area(shapes))              # 19.141592653589793
''', raises=True)

practice("✏️ 실습 2-3", "스택 클래스 (도전)", "",
         "6주차의 스택(리스트의 `append` · `pop`)을 클래스로 감싸세요. 안에 리스트를 하나 두고 밖에서는 메서드로만 씁니다 — 캡슐화입니다. (시간이 남는 사람만)<br>① `__init__(self)` — 빈 리스트 속성 `items`.<br>② `push(self, item)` — 맨 위에 넣습니다.<br>③ `pop(self)` — 맨 위 것을 꺼내 돌려줍니다. 비어 있으면 `None`.<br>④ `peek(self)` — 꺼내지 않고 맨 위 것만 돌려줍니다. 비어 있으면 `None`.<br>⑤ `is_empty(self)` — 비었으면 `True`.<br>⑥ `size(self)` — 들어 있는 개수.",
         '''
# 여기에 Stack 클래스를 정의하세요


s = Stack()
s.push("a"); s.push("b"); s.push("c")
print(s.size(), s.peek())
print(s.pop(), s.pop(), s.pop(), s.pop())
print(s.is_empty())
''',
         '(lambda s: s.is_empty() and s.pop() is None and s.peek() is None and (s.push(1) or True) and (s.push(2) or True) and s.size() == 2 and s.peek() == 2 and s.pop() == 2 and s.pop() == 1 and s.is_empty() and s.size() == 0)(Stack())',
         '''
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

s = Stack()
s.push("a"); s.push("b"); s.push("c")
print(s.size(), s.peek())                       # 3 c
print(s.pop(), s.pop(), s.pop(), s.pop())       # c b a None
print(s.is_empty())                             # True
''', raises=True)

md(key("2교시 정리", "① 상속 `class 자식(부모):` — 공통 부분은 부모에 한 번만 쓰고 물려받습니다.<br>② 자식 `__init__` 첫 줄은 `super().__init__(…)`. 빠뜨리면 부모의 속성이 안 생깁니다.<br>③ 오버라이딩 — 같은 이름으로 다시 쓰면 자식 것이 이깁니다. `super().메서드()` 로 부모 것을 재사용.<br>④ 다형성 — 같은 이름으로 부르면 각자 알아서. 부르는 쪽의 `if` 가 사라지고, 새 종류를 더해도 부르는 코드는 그대로입니다.<br>⑤ 캡슐화 — `__속성` 으로 감추고 메서드로만 쓰게 합니다. 객체도 블랙박스입니다.") + "\n\n" + BREAK)

# ═════════════════════════ 3교시 ═════════════════════════
md("# 3교시 · 모듈과 패키지 시스템 · 외부 라이브러리\n\n" + period(3, "남이 만든 코드를 가져다 쓰다 — 모듈 · 패키지 · 라이브러리", [
    "클래스를 모듈(.py)에 저장하고 import 해서 쓴다",
    "패키지가 ‘모듈을 모은 폴더’임을 알고 from 패키지 import 모듈 을 쓴다",
    "이름 공간으로 이름 충돌을 피하고, import 가 모듈을 찾는 순서를 설명한다",
    "외부 라이브러리가 무엇인지, pip 으로 설치하는 흐름이 무엇인지 설명한다",
]))

md('''
## 3-1. 클래스도 모듈에 — `%%writefile` 로 저장하고 `import`

7주차 3-5에서 함수를 `.py` 파일에 저장해 **모듈(module)** 로 만들었습니다. 클래스도 똑같습니다. 오늘 만든 도형 클래스를 파일로 저장해 봅니다. 모듈 안에는 **정의만** 두고 `print` 는 넣지 않습니다(7주차 3-6).
''')

code('''
%%writefile shapes.py
"""도형 클래스 모음 — 9주차"""
import math

class Shape:
    def area(self):
        return 0

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2
''')

code('''
import shapes

r = shapes.Rectangle(3, 4)                 # 모듈.클래스(인자)
c = shapes.Circle(1)
print(r.area(), c.area())
print(isinstance(c, shapes.Shape))
''')

md('''
모듈 안의 함수를 `모듈.함수()` 로 부르듯, 클래스도 `모듈.클래스()` 로 만듭니다. `from shapes import Circle` 로 꺼내 오면 `Circle(1)` 로 짧게 쓸 수 있습니다. 어느 쪽이든 **출처가 보이는** `shapes.Circle` 이 수업의 기본입니다.

파일을 고친 뒤에는 7주차처럼 `importlib.reload(shapes)` 입니다. Python 은 한 번 읽은 모듈을 **기억해 두고** 다시 읽지 않기 때문입니다. 이 ‘기억’이 무엇인지는 3-4에서 봅니다.

## 3-2. 패키지 — 모듈을 모은 폴더

모듈이 많아지면 **폴더**로 정리합니다. 모듈(`.py` 파일)을 모아 둔 폴더가 **패키지(package)** 입니다. 폴더 안에 `__init__.py` 라는 파일이 있으면 Python 은 그 폴더를 패키지로 봅니다. (내용은 비어 있어도 됩니다.)

```
geometry/                ← 패키지 (폴더)
├─ __init__.py           ← "이 폴더는 패키지입니다" 표시. 비어 있어도 됩니다
├─ shapes.py             ← 모듈
└─ units.py              ← 모듈
```

직접 만들어 봅니다. 폴더를 먼저 만들고, 그 안에 파일 세 개를 씁니다.
''')

code('''
import os
os.makedirs("geometry", exist_ok=True)     # 폴더 만들기 (이미 있으면 그냥 지나갑니다)
print(os.listdir("."))                     # 현재 폴더의 파일 목록 — geometry 가 보여야 합니다
''')

code('''
%%writefile geometry/__init__.py
"""geometry 패키지 — 도형과 단위 변환"""
''')

code('''
%%writefile geometry/shapes.py
import math

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2
''')

code('''
%%writefile geometry/units.py
def cm_to_inch(cm):
    return cm / 2.54

def inch_to_cm(inch):
    return inch * 2.54
''')

md('''
패키지 안의 모듈은 **점으로 이어서** 부릅니다. `패키지.모듈.이름`. `import` 방법은 7주차 3-2의 표와 같고, 앞에 패키지 이름이 하나 더 붙을 뿐입니다.
''')

code('''
import geometry.shapes                         # ① 패키지.모듈 — 부를 때도 전체 이름
print(geometry.shapes.Rectangle(3, 4).area())

from geometry import units                     # ② 패키지에서 모듈만 꺼내기 — 수업의 기본
print(units.cm_to_inch(2.54))

from geometry.shapes import Circle             # ③ 모듈에서 클래스만 꺼내기
print(Circle(1).area())

import geometry.units as gu                    # ④ 별명
print(gu.inch_to_cm(10))
''')

md('''
표준 라이브러리에도 패키지가 많습니다. `os.path.join()` 의 `os.path`, `urllib.request`, `json`, `collections`. 7주차에서 쓴 `import math` 의 `math` 는 모듈 하나이고, 12주차에 만날 `numpy` 는 폴더 수십 개로 된 큰 패키지입니다.

| 단위 | 실체 | 예 |
|:---|:---|:---|
| **모듈**(module) | `.py` 파일 하나 | `math`, `random`, 오늘의 `shapes.py` |
| **패키지**(package) | 모듈을 모은 **폴더** (`__init__.py` 포함) | `geometry`, `os`, `json`, `numpy` |
| **라이브러리**(library) | 쓸 수 있게 묶어 **배포**된 모듈 · 패키지 전체를 부르는 말 | 표준 라이브러리, `numpy` 라이브러리 |

세 말은 엄격히 구분되지 않습니다. “`numpy` 모듈”, “`numpy` 패키지”, “`numpy` 라이브러리” 모두 통합니다. 중요한 것은 **`import` 로 가져와 `이름.기능` 으로 쓴다**는 공통점입니다.

## 3-3. 이름 공간 — 같은 이름이 부딪히지 않는 이유

7주차 3-4에서 `from math import *` 가 내 `sqrt` 를 **조용히 덮어쓰는** 것을 보았습니다. 그때 ‘이름이 속한 울타리’를 **이름 공간(namespace)** 이라고 했습니다. 오늘 그 울타리들을 한눈에 봅니다.

| 이름 공간 | 누가 만드나 | 들어 있는 것 | 수명 |
|:---|:---|:---|:---|
| **내장**(built-in) | Python 시작 때 | `print`, `len`, `int`, `str` … | 프로그램 내내 |
| **전역**(global) | 노트북(모듈) 수준에서 | 셀에서 만든 변수 · 함수 · 클래스, `import` 한 모듈 이름 | 커널이 살아 있는 동안 |
| **지역**(local) | 함수 · 메서드를 **호출**할 때 | 매개변수, 함수 안에서 만든 변수 | 함수가 끝날 때까지 (7주차 2-4) |
| **모듈 · 객체** | `import` 할 때 · 인스턴스를 만들 때 | `math.pi`, `shapes.Circle`, `s1.name` | 모듈 · 객체가 살아 있는 동안 |

이름을 쓰면 Python 은 **지역 → 전역 → 내장** 순서로 찾습니다. 그래서 함수 안에서 `print` 를 쓰면 지역 · 전역에 없으니 내장에서 찾아 쓰고, 내가 전역에 `print = 3` 이라고 쓰면 내장의 `print` 가 **가려집니다.** (실제로 해 보면 `print()` 가 안 됩니다. `Kernel → Restart` 로만 돌아옵니다.)

`math.sqrt` 처럼 **모듈 이름을 앞에 붙이는** 것은 “전역이 아니라 `math` 의 울타리 안에서 찾아라”는 뜻입니다. 내 `sqrt` 와 `math.sqrt` 가 공존하는 이유입니다. 객체도 같습니다. `s1.name` 과 `s2.name` 은 다른 울타리의 같은 이름입니다.

**예상해 보기** — 아래 셀에서 `area` 라는 이름이 세 번 나옵니다. 각각 어느 울타리의 것일까요?
''')

code('''
from geometry import shapes

area = "전역의 area"                           # 전역

def report(shape):
    area = shape.area()                        # 지역 — 전역의 area 와 남남
    return f"넓이 {area:.2f}"

print(report(shapes.Circle(1)))                # shapes.Circle 의 메서드 area
print(area)                                    # 전역의 area 는 그대로
''')

md('''
이름이 겹칠 때 피하는 길은 세 가지입니다. ① `import 모듈 as 별명` — `import geometry.units as gu`, ② `from 모듈 import 이름 as 별명` — `from math import sqrt as msqrt`, ③ 그냥 `모듈.이름` 으로 부르기. 수업의 기본은 ③입니다.

## 3-4. `import` 는 모듈을 어디서 찾나 — 세 단계

`import shapes` 라고 쓰면 Python 은 다음 순서로 찾습니다. `ModuleNotFoundError` 가 났을 때 어디를 봐야 하는지가 여기서 나옵니다.

1. **`sys.modules`** — 이미 읽어 둔 모듈의 **기억(캐시)**. 한 번 읽은 모듈은 여기 들어 있고, 다시 `import` 해도 **파일을 다시 읽지 않습니다.** 7주차에서 파일을 고쳐도 바뀌지 않아 `importlib.reload()` 가 필요했던 이유입니다.
2. **현재 폴더** — 노트북이 있는 곳. `%%writefile` 로 만든 파일이 여기 있습니다.
3. **`sys.path` 에 적힌 폴더들** — 표준 라이브러리 폴더, 설치한 외부 라이브러리 폴더(`site-packages`).
''')

code('''
import sys

print("shapes" in sys.modules, "geometry.units" in sys.modules, "pandas" in sys.modules)
print(len(sys.modules), "개 모듈이 읽혀 있음")
for p in sys.path:                          # 찾는 폴더 목록 — '' 또는 현재 폴더가 맨 앞에 있습니다
    print(repr(p))
''')

md(warn("내 파일 이름을 표준 모듈과 같게 짓지 마세요", "현재 폴더를 표준 라이브러리보다 <b>먼저</b> 찾기 때문에, 내 파일을 `random.py` 나 `math.py` 로 저장하면 `import random` 이 <b>내 파일</b>을 읽습니다. 그러면 `random.randint` 가 없다는 `AttributeError` 가 납니다. 초보자가 가장 많이 겪는 미스터리 중 하나입니다. `my_random.py` 처럼 이름을 피하세요."))

md('''
| 오류 | 뜻 | 먼저 볼 곳 |
|:---|:---|:---|
| `ModuleNotFoundError: No module named 'shapes'` | 2 · 3 단계 어디에도 그 파일이 없다 | `%%writefile` 셀을 실행했나? 이름 오타? 외부 라이브러리라면 설치했나? |
| `ImportError: cannot import name 'Circle' from 'shapes'` | 모듈은 찾았는데 그 안에 그 이름이 없다 | 파일 안의 클래스 · 함수 이름 확인, 고쳤다면 `reload` |
| `AttributeError: module 'random' has no attribute 'randint'` | 엉뚱한 모듈을 읽었다 | 같은 이름의 내 파일이 현재 폴더에 있나? |

## 3-5. 외부 라이브러리 — Python 의 가장 큰 장점

지금까지 쓴 모듈은 **표준 라이브러리**(Python 에 기본 포함)와 **내가 만든 것** 두 종류였습니다. 세 번째가 **외부 라이브러리(third-party library)** 입니다. 전 세계 개발자들이 만들어 **PyPI**(Python Package Index, [pypi.org](https://pypi.org))에 공개한 패키지로, 60만 개가 넘습니다.

3주차에서 Python 이 널리 쓰이는 이유로 ‘풍부한 라이브러리’를 꼽았습니다. 행렬 계산, 그래프 그리기, 웹 서버, 인공지능 — 거의 모든 분야에 **이미 잘 만들어진 패키지**가 있습니다. Python 프로그래밍의 많은 부분은 이런 패키지들을 **찾아서 잘 이어 붙이는** 일입니다. 그래서 Python 을 ‘접착제 언어(glue language)’라고도 부릅니다.

| 분야 | 패키지 | 하는 일 |
|:---|:---|:---|
| 수치 계산 | **`numpy`** | 큰 배열 · 행렬 계산. 거의 모든 과학 패키지의 바탕 |
| 데이터 분석 | **`pandas`** | 표(엑셀 같은) 데이터 읽기 · 합치기 · 집계 |
| 시각화 | **`matplotlib`** | 그래프 · 히스토그램 · 산점도 |
| 기계 학습 | `scikit-learn` | 기본적인 기계 학습 알고리즘과 평가 도구 |
| 딥러닝 | `pytorch`, `tensorflow` | 신경망. 이미지 · 자연어 처리 모델 |
| 자연어 처리 | `nltk`, `transformers` | 텍스트 가공, 언어 모델 — 13주차 |
| 웹 요청 | `requests` | 인터넷에서 데이터 받아오기 — 14주차의 API |
| 웹 서버 | `flask`, `django` | 웹 사이트 · 앱의 뼈대 |

굵게 쓴 셋은 12주차에 직접 씁니다. 오늘은 **설치하고 가져오는 흐름**만 봅니다.

## 3-6. 설치하기 — `pip`

외부 라이브러리는 **설치**해야 `import` 할 수 있습니다. 설치 도구가 **pip** 입니다. Python 을 설치하면 함께 들어 있고, **터미널(명령 프롬프트)** 에서 씁니다. 노트북 셀이 아닙니다.

```
pip install numpy          ← PyPI 에서 numpy 를 받아 site-packages 폴더에 설치
```

| 명령 | 하는 일 |
|:---|:---|
| `pip install 패키지` | 설치. 그 패키지가 **의존하는** 다른 패키지도 함께 설치됩니다 |
| `pip install -U 패키지` | 최신 버전으로 업그레이드 |
| `pip uninstall 패키지` | 삭제 |
| `pip list` | 설치된 패키지 목록 |
| `pip show 패키지` | 버전 · 설치 위치 · 의존 패키지 보기 |
| `pip install -r requirements.txt` | 파일에 적힌 패키지들을 한꺼번에 설치 — 남의 프로젝트를 받았을 때 |

**의존성(dependency)** 이란 “B 를 쓰려면 A 가 먼저 있어야 한다”는 관계입니다. `pandas` 는 `numpy` 에 의존합니다. pip 은 이런 관계를 따라가 **필요한 것을 모두** 설치해 줍니다. 수십 개를 손으로 찾아 설치하던 시절과 비교하면 큰 발전입니다.

''' + note("수업 사이트에서는 설치가 조금 다릅니다", "이 사이트의 Python(Pyodide)은 여러분의 <b>브라우저 안</b>에서 돕니다. 터미널이 없는 대신, `numpy` · `pandas` · `matplotlib` 처럼 자주 쓰는 패키지는 <b>`import` 하는 순간 인터넷에서 자동으로 받아옵니다</b>(처음 한 번, 몇 초). 그 밖의 순수 Python 패키지는 셀에서 `%pip install 패키지` 로 설치합니다.<br>여러분 PC 에 Python 을 설치해 쓸 때는 위 표의 `pip install` 입니다. 12주차에 PC 에서 가상환경을 만들고 직접 설치해 봅니다."))

md('''
## 3-7. 맛보기 — `numpy` 가져와 보기

`numpy` 를 가져와 점수 리스트를 다뤄 봅니다. 처음 실행하면 패키지를 받아오느라 몇 초 걸립니다. 지금은 **`import` 해서 `이름.기능` 으로 쓴다**는 흐름만 보세요. 내용은 12주차에 배웁니다.
''')

code('''
import numpy as np                           # 관습적인 별명 — 전 세계가 np 로 씁니다

scores = [72, 88, 95, 60]
arr = np.array(scores)                       # numpy 배열 — 리스트와 닮았지만 계산 기능이 붙어 있습니다
print(arr)
print(arr.mean(), arr.max(), arr.std())      # 평균 · 최댓값 · 표준편차 — 메서드입니다
print(arr + 5)                               # 모든 원소에 한 번에 — 리스트는 이렇게 못 합니다
print(type(arr), np.__version__)
''')

md('''
`arr.mean()` 은 **메서드**입니다. `np.array(…)` 로 만든 `arr` 은 `numpy` 가 정의한 `ndarray` **클래스의 인스턴스**입니다. 오늘 1교시에 배운 것이 그대로입니다. 누군가 `class ndarray:` 를 쓰고 `def mean(self):` 를 넣어 두었고, 우리는 설계도를 몰라도 **메서드 이름**만으로 씁니다.

`np.__version__` 처럼 패키지의 버전은 `__version__` 속성으로 봅니다. 모르는 패키지는 7주차의 `dir(np)` · `help(np.array)` 로 탐색합니다.
''')

md(key("외부 라이브러리 정리", "① 모듈(파일) → 패키지(폴더) → 라이브러리(배포 단위). 모두 `import` 로 가져와 `이름.기능` 으로 씁니다.<br>② 외부 라이브러리는 PyPI 에서 `pip install` 로 설치합니다. 의존 패키지도 함께 옵니다.<br>③ `import` 는 캐시 → 현재 폴더 → `sys.path` 순서로 찾습니다. `ModuleNotFoundError` 는 이 세 곳을 봅니다.<br>④ 남의 패키지도 결국 클래스와 함수입니다. 1교시의 <b>객체 · 메서드</b>를 알면 어떤 라이브러리든 같은 눈으로 읽을 수 있습니다."))

# ── 3교시 실습 ──
practice("✏️ 실습 3-1", "bank.py — 계좌 클래스 모듈", "약 6분",
         "2-6의 `BankAccount` 를 아래 `%%writefile` 셀에 넣어 `bank.py` 모듈로 저장하세요. 정의만 넣고 `print` 는 넣지 않습니다.<br>① `__init__(self, owner, balance=0)` — `owner` 와 감춘 잔액 `__balance`.<br>② `deposit(self, amount)` — 양수일 때만 더합니다.<br>③ `withdraw(self, amount)` — 잔액보다 많으면 `False` 를 돌려주고 바꾸지 않습니다. 아니면 빼고 `True`.<br>④ `get_balance(self)` — 잔액을 돌려줍니다.<br>⑤ `__str__(self)` — `\"김연세: 1500원\"` 모양.<br>다음 셀은 모듈을 다시 읽어 시험합니다. 파일을 고칠 때마다 두 셀을 <b>차례로</b> 실행하세요.",
         '''
%%writefile bank.py
# 여기에 BankAccount 클래스를 정의하세요

''',
         '(lambda acc: acc.get_balance() == 1000 and (acc.deposit(500) or True) and acc.get_balance() == 1500 and acc.withdraw(2000) is False and acc.get_balance() == 1500 and acc.withdraw(300) is True and acc.get_balance() == 1200 and str(acc) == "김연세: 1200원" and (acc.deposit(-100) or True) and acc.get_balance() == 1200)(importlib.reload(bank).BankAccount("김연세", 1000))',
         '''
%%writefile bank.py
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:
            return False
        self.__balance -= amount
        return True

    def get_balance(self):
        return self.__balance

    def __str__(self):
        return f"{self.owner}: {self.__balance}원"
''',
         extra='''
import importlib, bank
importlib.reload(bank)             # 파일을 고쳤을 때 다시 읽어 옵니다
acc = bank.BankAccount("김연세", 1000)
acc.deposit(500)
print(acc.withdraw(2000), acc.withdraw(300))
print(acc)
''', extra_raises=True, heading="## 3교시 실습")

practice("✏️ 실습 3-2", "패키지에 모듈 더하기 — geometry/triangle.py", "약 5분",
         "3-2에서 만든 `geometry` 패키지에 모듈을 하나 더합니다. 아래 셀로 `geometry/triangle.py` 를 만들고, `Triangle` 클래스를 정의하세요.<br>① `__init__(self, base, height)` — 밑변과 높이.<br>② `area(self)` — `base * height / 2`.<br>다음 셀은 `from geometry.triangle import Triangle` 로 가져와 시험합니다. `Triangle(3, 4).area()` → `6.0`",
         '''
%%writefile geometry/triangle.py
# 여기에 Triangle 클래스를 정의하세요

''',
         'importlib.reload(geometry.triangle).Triangle(3, 4).area() == 6.0 and geometry.triangle.Triangle(10, 5).area() == 25.0 and geometry.triangle.Triangle(2, 3).base == 2 and geometry.triangle.Triangle.__module__ == "geometry.triangle"',
         '''
%%writefile geometry/triangle.py
class Triangle:
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return self.base * self.height / 2
''',
         extra='''
import importlib, geometry.triangle
importlib.reload(geometry.triangle)
from geometry.triangle import Triangle
print(Triangle(3, 4).area())
''', extra_raises=True)

practice("✏️ 실습 3-3", "numpy 로 점수 다루기", "약 4분",
         "`import numpy as np` 뒤에 세 변수를 만드세요.<br>① `arr` — `scores` 리스트를 `np.array()` 로 바꾼 배열.<br>② `mean_score` — `arr.mean()` 의 값. `78.75`<br>③ `curved` — 모든 점수에 5점을 더한 배열 `arr + 5`. 단, 100점을 넘지 않게 `np.minimum(arr + 5, 100)` 을 쓰세요. `[77, 93, 100, 65]`<br>모르는 함수는 `help(np.minimum)` 로 물어보세요.",
         '''
import numpy as np

scores = [72, 88, 95, 60]
# 여기에 arr, mean_score, curved 를 만드세요


print(arr)
print(mean_score)
print(curved)
''',
         "abs(mean_score - 78.75) < 1e-6 and list(curved) == [77, 93, 100, 65] and type(arr).__name__ == 'ndarray' and len(arr) == 4",
         '''
import numpy as np

scores = [72, 88, 95, 60]
arr = np.array(scores)
mean_score = arr.mean()
curved = np.minimum(arr + 5, 100)        # 5점씩 올리되 100점을 넘지 않게

print(arr)               # [72 88 95 60]
print(mean_score)        # 78.75
print(curved)            # [ 77  93 100  65]
''', raises=True)

md(key("3교시 정리", "① 클래스도 `%%writefile` 로 모듈에 저장하고 `모듈.클래스()` 로 씁니다. 고친 뒤에는 `importlib.reload()`.<br>② 패키지는 `__init__.py` 가 있는 폴더. `from 패키지 import 모듈` 이 기본입니다.<br>③ 이름 공간 — 지역 → 전역 → 내장 순서로 찾습니다. `모듈.이름` 은 그 모듈의 울타리에서 찾으라는 뜻.<br>④ `import` 는 캐시(`sys.modules`) → 현재 폴더 → `sys.path` 순서로 찾습니다. 내 파일 이름을 표준 모듈과 같게 짓지 않습니다.<br>⑤ 외부 라이브러리는 `pip install` 로 PyPI 에서 설치합니다. `numpy` 의 배열도 결국 클래스의 인스턴스이고, 메서드로 씁니다."))

# ═════════════════════════ 주차 정리 ═════════════════════════
md('''
# 9주차 정리

| 개념 | 한 줄 요약 |
|:---|:---|
| **객체** | 데이터(속성) + 기능(메서드). Python 의 모든 값은 객체 |
| **클래스 / 인스턴스** | 설계도 / 설계도로 만든 제품. `클래스이름(인자)` 로 만든다 |
| **`__init__`** | 인스턴스를 만들 때 자동 실행. 속성을 여기서 모두 만든다 |
| **`self`** | 점 앞의 객체 자신. 모든 메서드의 첫 매개변수. `self.속성` 으로 자기 데이터 접근 |
| **메서드** | 클래스 안의 함수. `객체.메서드()` 로 부르면 `self` 가 자동으로 들어간다 |
| **`__str__`** | `print(객체)` 가 쓸 문자열을 돌려준다 |
| **상속** | `class 자식(부모):` — 공통 부분을 물려받는다. 자식 `__init__` 첫 줄은 `super().__init__()` |
| **오버라이딩** | 자식이 같은 이름의 메서드를 다시 써서 동작을 바꾼다 |
| **다형성** | 같은 이름으로 불러도 객체 종류에 따라 다르게 동작. 부르는 쪽의 `if` 가 사라진다 |
| **캡슐화** | 세부는 감추고(`__속성`) 메서드로만 쓰게 한다 |
| **모듈 / 패키지 / 라이브러리** | `.py` 파일 / `__init__.py` 가 있는 폴더 / 배포 단위. 모두 `import` 로 가져온다 |
| **이름 공간** | 지역 → 전역 → 내장 순서로 찾는다. `모듈.이름` 은 그 모듈의 울타리 |
| **`import` 탐색 순서** | `sys.modules` 캐시 → 현재 폴더 → `sys.path` |
| **pip** | PyPI 의 외부 라이브러리를 의존성까지 설치하는 도구 |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| `AttributeError: … has no attribute 'x'` | 그 객체에 그 속성 · 메서드가 없다 | `__init__` 에서 안 만든 속성 · `super().__init__()` 을 빠뜨림 · `__` 로 감춘 속성 · 엉뚱한 모듈을 읽음 |
| `TypeError: … takes 0 positional arguments but 1 was given` | 메서드에 `self` 가 없다 | `def introduce():` |
| `TypeError: … missing 1 required positional argument: 'self'` | 인스턴스가 아니라 클래스로 메서드를 불렀다 | `Student.introduce()` (`s.introduce()` 여야 함) |
| `<__main__.Student object at 0x…>` | 오류는 아니지만 신호 | `__str__` 이 없다 |
| `ModuleNotFoundError` | 모듈 파일을 찾지 못했다 | `%%writefile` 을 안 했다 · 오타 · 외부 라이브러리 미설치 |
| `ImportError: cannot import name` | 모듈은 있는데 그 이름이 없다 | 클래스 이름 오타 · 고친 뒤 `reload` 안 함 |

''' + key("오늘의 한 문장", "함수는 <b>일</b>에 이름을 붙이고, 클래스는 <b>데이터와 일을 한 묶음</b>에 이름을 붙입니다. 그 묶음을 파일에 담으면 모듈, 폴더에 모으면 패키지, 세상에 내놓으면 라이브러리 — 우리가 `import` 하는 모든 것은 누군가 이렇게 만든 클래스와 함수입니다.") + f'''

<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 10주차 고급 알고리듬: 재귀와 동적 프로그래밍</b><br>
함수가 <b>자기 자신을 부르는</b> 재귀 호출(recursion)과, 같은 계산을 두 번 하지 않는 동적 프로그래밍을 배웁니다. 7주차 2-6의 <b>호출 스택</b> 그림과 6주차의 반복문을 다시 보고 오세요.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 노트북과 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">bank.py</code> 를 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
''')

# ═════════════════════════ 과제 ═════════════════════════
FIRST_HW_CELL = len(CELLS)

md(f'''
# 9주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">4 ~ 9주차 종합 — 클래스로 만들기</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>모든 문제는 <b>클래스를 정의</b>하는 문제입니다. 자가 점검은 여러분의 클래스로 인스턴스를 만들어 <b>여러 가지 값으로</b> 메서드를 불러 봅니다</li><li>4주차(변수 · 문자열), 5주차(리스트 · 딕셔너리 · if 문), 6주차(반복문 · 스택 · 큐), 7주차(함수 · 모듈), 9주차(클래스 · 상속 · 패키지)의 내용만으로 풀 수 있습니다</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 클래스 · 메서드 이름과 매개변수 순서(`Rectangle(width, height)` 등)를 바꾸지 마세요. 점검 셀이 그 이름으로 부릅니다.<br>③ 점검 셀은 예시와 <b>다른 값</b>으로도 인스턴스를 만들어 봅니다. 예시 값 하나만 맞추는 코드는 통과하지 못합니다.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다.<br>⑤ 막히면 먼저 <b>“이 객체는 어떤 데이터를 갖고(속성), 무엇을 할 수 있나(메서드)”</b>를 한국어로 적어 보세요. 그다음에 `class` 한 줄과 `__init__` 을 씁니다."))

practice("📝 과제 1", "직사각형 클래스", "",
         "`Rectangle` 클래스를 정의하세요.<br>① `__init__(self, width, height)` — 두 속성 `width`, `height`.<br>② `area(self)` — 넓이.<br>③ `perimeter(self)` — 둘레 `2 * (width + height)`.<br>④ `is_square(self)` — 가로와 세로가 같으면 `True`.<br>⑤ `__str__(self)` — `\"3 x 4 직사각형\"` 모양. (`x` 는 영어 소문자 엑스, 앞뒤 공백 하나)<br>`Rectangle(3, 4).perimeter()` → `14`, `Rectangle(5, 5).is_square()` → `True`",
         '''
# 여기에 Rectangle 클래스를 정의하세요


r = Rectangle(3, 4)
print(r, r.area(), r.perimeter(), r.is_square())
print(Rectangle(5, 5).is_square())
''',
         'Rectangle(3, 4).area() == 12 and Rectangle(3, 4).perimeter() == 14 and Rectangle(3, 4).is_square() is False and Rectangle(5, 5).is_square() is True and str(Rectangle(3, 4)) == "3 x 4 직사각형" and Rectangle(2.5, 2).area() == 5.0 and Rectangle(7, 1).width == 7',
         '''
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def __str__(self):
        return f"{self.width} x {self.height} 직사각형"

r = Rectangle(3, 4)
print(r, r.area(), r.perimeter(), r.is_square())
print(Rectangle(5, 5).is_square())
''', raises=True, show_answer=False)

practice("📝 과제 2", "학생 성적 클래스", "",
         "`Student` 클래스를 정의하세요.<br>① `__init__(self, name)` — 이름과, 빈 딕셔너리 속성 `scores` (`{과목: 점수}`).<br>② `add_score(self, subject, score)` — 과목 점수를 넣습니다. 같은 과목을 다시 넣으면 덮어씁니다.<br>③ `average(self)` — 모든 과목 평균. 과목이 없으면 `0`.<br>④ `best_subject(self)` — 점수가 가장 높은 과목 이름. 같으면 먼저 넣은 과목. 과목이 없으면 `None`. (6주차의 ‘최댓값 찾기’ 또는 `max()`)<br>⑤ `__str__(self)` — `\"김연세 (3과목, 평균 85.0)\"` 모양. 평균은 `round(…, 1)`.",
         '''
# 여기에 Student 클래스를 정의하세요


s = Student("김연세")
s.add_score("수학", 90)
s.add_score("영어", 80)
s.add_score("과학", 85)
print(s.average(), s.best_subject())
print(s)
''',
         '(lambda s: s.average() == 0 and s.best_subject() is None and str(s) == "김연세 (0과목, 평균 0)" and (s.add_score("수학", 90) or True) and (s.add_score("영어", 80) or True) and (s.add_score("과학", 85) or True) and abs(s.average() - 85) < 1e-6 and s.best_subject() == "수학" and str(s) == "김연세 (3과목, 평균 85.0)" and (s.add_score("영어", 95) or True) and s.best_subject() == "영어" and abs(s.average() - 90) < 1e-6 and len(s.scores) == 3)(Student("김연세"))',
         '''
class Student:
    def __init__(self, name):
        self.name = name
        self.scores = {}

    def add_score(self, subject, score):
        self.scores[subject] = score

    def average(self):
        if len(self.scores) == 0:
            return 0
        return sum(self.scores.values()) / len(self.scores)

    def best_subject(self):
        best = None
        for subject, score in self.scores.items():
            if best is None or score > self.scores[best]:
                best = subject
        return best

    def __str__(self):
        return f"{self.name} ({len(self.scores)}과목, 평균 {round(self.average(), 1)})"

s = Student("김연세")
s.add_score("수학", 90)
s.add_score("영어", 80)
s.add_score("과학", 85)
print(s.average(), s.best_subject())
print(s)
''', raises=True, show_answer=False)

practice("📝 과제 3", "스택 클래스로 괄호 짝 검사", "",
         "① 실습 2-3의 `Stack` 클래스를 정의하세요 (`push`, `pop`, `peek`, `is_empty`, `size`). 정답 예시를 보지 않고 다시 써 보세요.<br>② 함수 `is_balanced(text)` — 7주차 과제 3의 괄호 짝 검사(`()` · `[]` · `{}` 세 종류)를 <b>리스트가 아니라 `Stack` 객체로</b> 다시 쓰세요. `stack.push(ch)`, `stack.pop()`, `stack.is_empty()` 만 씁니다.<br>`is_balanced(\"{[(1 + 2) * 3]}\")` → `True`, `is_balanced(\"([)]\")` → `False`",
         '''
# 여기에 Stack 클래스와 is_balanced 함수를 정의하세요


for text in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", ""]:
    print(repr(text), is_balanced(text))
''',
         '[is_balanced(t) for t in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", "", "(a[b]{c})", "(]", "[(])"]] == [True, False, False, False, True, True, True, False, False] and (lambda s: (s.push(1) or True) and (s.push(2) or True) and s.size() == 2 and s.peek() == 2 and s.pop() == 2 and s.pop() == 1 and s.pop() is None and s.is_empty())(Stack())',
         '''
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

def is_balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = Stack()
    for ch in text:
        if ch in "([{":
            stack.push(ch)
        elif ch in pairs:
            if stack.is_empty() or stack.pop() != pairs[ch]:
                return False
    return stack.is_empty()

for text in ["{[(1 + 2) * 3]}", "([)]", "((", "))", "no brackets", ""]:
    print(repr(text), is_balanced(text))
''', raises=True, show_answer=False)

practice("📝 과제 4", "상속과 다형성 — 직원과 관리자", "",
         "세 클래스와 함수 하나를 정의하세요.<br>① `Person(name)` — 속성 `name`, 메서드 `introduce()` 는 `\"김연세입니다\"` 를 돌려줍니다.<br>② `Employee(Person)` — `__init__(self, name, salary)`. `super().__init__(name)` 뒤 `salary` 를 더합니다. `pay()` 는 `salary` 를 돌려줍니다. `introduce()` 를 오버라이딩해 `\"김연세입니다. 월급은 300만원입니다\"` 를 돌려줍니다 (`salary` 단위는 만원).<br>③ `Manager(Employee)` — `__init__(self, name, salary, bonus)`. `pay()` 는 `salary + bonus`. `introduce()` 는 부모(`Employee`)의 문장 뒤에 `\". 관리자입니다\"` 를 붙입니다. `super()` 를 쓰세요.<br>④ 함수 `total_pay(staff)` — 직원 리스트를 받아 `pay()` 의 합을 돌려줍니다. 종류를 묻지 않습니다.<br>`total_pay([Employee(\"a\", 300), Manager(\"b\", 400, 100)])` → `800`",
         '''
# 여기에 Person, Employee, Manager 클래스와 total_pay 함수를 정의하세요


staff = [Employee("김연세", 300), Manager("이미래", 400, 100), Employee("박원주", 250)]
for person in staff:
    print(person.introduce(), "→", person.pay())
print(total_pay(staff))
''',
         'Employee("김연세", 300).introduce() == "김연세입니다. 월급은 300만원입니다" and Person("김연세").introduce() == "김연세입니다" and Employee("김연세", 300).pay() == 300 and Manager("이미래", 400, 100).pay() == 500 and Manager("이미래", 400, 100).introduce() == "이미래입니다. 월급은 400만원입니다. 관리자입니다" and total_pay([Employee("a", 300), Manager("b", 400, 100), Employee("c", 250)]) == 1050 and total_pay([]) == 0 and isinstance(Manager("m", 1, 1), Employee) and isinstance(Manager("m", 1, 1), Person)',
         '''
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"{self.name}입니다"

class Employee(Person):
    def __init__(self, name, salary):
        super().__init__(name)
        self.salary = salary

    def pay(self):
        return self.salary

    def introduce(self):
        return super().introduce() + f". 월급은 {self.salary}만원입니다"

class Manager(Employee):
    def __init__(self, name, salary, bonus):
        super().__init__(name, salary)
        self.bonus = bonus

    def pay(self):
        return self.salary + self.bonus

    def introduce(self):
        return super().introduce() + ". 관리자입니다"

def total_pay(staff):
    total = 0
    for person in staff:
        total += person.pay()
    return total

staff = [Employee("김연세", 300), Manager("이미래", 400, 100), Employee("박원주", 250)]
for person in staff:
    print(person.introduce(), "→", person.pay())
print(total_pay(staff))
''', raises=True, show_answer=False)

practice("📝 과제 5", "notebook.py — 노트와 노트북 모듈 (도전)", "",
         "노트를 정리하는 프로그램을 <b>모듈</b>로 만듭니다. 아래 `%%writefile` 셀에 두 클래스를 정의해 `notebook.py` 로 저장하세요.<br>① `Note(contents=\"\")` — 속성 `contents`. `write(self, contents)` 는 내용을 바꿉니다. `__str__` 은 내용을 돌려줍니다.<br>② `NoteBook(title, max_pages=300)` — 속성 `title`, `max_pages`, 그리고 빈 딕셔너리 `notes` (`{페이지 번호: Note}`).<br>&nbsp;&nbsp;· `add_note(self, note)` — 비어 있는 <b>가장 작은</b> 페이지 번호(1부터)에 노트를 넣고 그 번호를 돌려줍니다. 페이지가 `max_pages` 만큼 차 있으면 넣지 않고 `None` 을 돌려줍니다.<br>&nbsp;&nbsp;· `remove_note(self, page)` — 그 페이지의 노트를 빼서 돌려줍니다. 없는 페이지면 `None`.<br>&nbsp;&nbsp;· `page_count(self)` — 들어 있는 노트 수.<br>힌트: ‘비어 있는 가장 작은 번호’는 `for page in range(1, self.max_pages + 1): if page not in self.notes: …` 입니다. 2번을 지운 뒤 추가하면 2번에 들어가야 합니다.<br>다음 셀은 모듈을 다시 읽어 시험합니다. 파일을 고칠 때마다 두 셀을 차례로 실행하세요.",
         '''
%%writefile notebook.py
# 여기에 Note 와 NoteBook 클래스를 정의하세요

''',
         '(lambda nb: nb.page_count() == 0 and nb.add_note(notebook.Note("맑은 가을 날씨는")) == 1 and nb.add_note(notebook.Note("산책하기에")) == 2 and nb.add_note(notebook.Note("너무나도 좋다")) == 3 and nb.add_note(notebook.Note("넘침")) is None and nb.page_count() == 3 and str(nb.notes[2]) == "산책하기에" and str(nb.remove_note(2)) == "산책하기에" and nb.remove_note(2) is None and nb.page_count() == 2 and nb.add_note(notebook.Note("다시")) == 2 and str(nb.notes[2]) == "다시" and nb.title == "가을 단상" and (lambda n: (n.write("바뀜") or True) and str(n) == "바뀜")(notebook.Note("처음")) and str(notebook.Note()) == "")(importlib.reload(notebook).NoteBook("가을 단상", max_pages=3))',
         '''
%%writefile notebook.py
class Note:
    def __init__(self, contents=""):
        self.contents = contents

    def write(self, contents):
        self.contents = contents

    def __str__(self):
        return self.contents


class NoteBook:
    def __init__(self, title, max_pages=300):
        self.title = title
        self.max_pages = max_pages
        self.notes = {}

    def add_note(self, note):
        for page in range(1, self.max_pages + 1):     # 비어 있는 가장 작은 페이지를 찾습니다
            if page not in self.notes:
                self.notes[page] = note
                return page
        return None                                    # 다 찼습니다

    def remove_note(self, page):
        if page in self.notes:
            return self.notes.pop(page)
        return None

    def page_count(self):
        return len(self.notes)
''',
         extra='''
import importlib, notebook
importlib.reload(notebook)
my_notebook = notebook.NoteBook("가을 단상", max_pages=3)
for text in ["맑은 가을 날씨는", "산책하기에", "너무나도 좋다", "넘치는 글"]:
    print(my_notebook.add_note(notebook.Note(text)))
for page, note in my_notebook.notes.items():
    print(page, note)
print(my_notebook.page_count())
''', extra_raises=True, show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다.<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다. 과제 5를 했다면 `notebook.py` 도 함께 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
def to_nb(cells):
    out, seen = [], set()
    for i, (ctype, src, meta) in enumerate(cells):
        cid = hashlib.md5(f"w9-{i}-{src}".encode("utf-8")).hexdigest()[:8]
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
    cells = [("markdown", "# 컴퓨팅사고 9주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 강의 노트북 `" + LECTURE + "` 맨 끝 ‘9주차 과제’의 정답 예시입니다. 각 셀은 혼자서 실행됩니다. (과제 5는 `%%writefile` 셀이므로 노트북에서 실행한 뒤 `import notebook` 으로 확인합니다.)", {})]
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

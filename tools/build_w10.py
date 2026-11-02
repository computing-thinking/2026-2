import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 10주차 노트북 생성 스크립트 — 생각하기 판(수업용) · 풀이판(수업 후) · 과제 정답(교수용) 세 파일을 만든다
# 주제: 고급 알고리듬 — 어려운 문제를 컴퓨팅 사고로 푸는 법 (재귀 · 탐색과 정렬 · 그래프 모델링)
# 예제 문제 5개: 하노이 탑 · 숫자 맞히기(이진 탐색) · 줄 세우기(정렬) · 쾨니히스베르크 다리 · 미로 최단 경로
#
# 셀마다 part 를 붙인다:  T(think) = 생각하기 판에만  /  S(solve) = 풀이판에만  /  BOTH = 두 판 모두
#   생각하기 판: 문제 띠 · 설명 · 그림 · 게임 · 🤔 생각해 보기 상자 · 칠판 풀이를 받아 적는 빈 셀 · 실습(정답 없음) · 과제
#   풀이판:     문제 띠 · 🧠 풀이 상자 · 풀이 코드 · 정리 · 실습 정답
# 사용: python build_w10.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w10.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import base64, hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
THINK_NB = "컴퓨팅사고_10주차_알고리듬_생각하기.ipynb"
SOLVE_NB = "컴퓨팅사고_10주차_알고리듬_풀이.ipynb"
HW_SOL = "컴퓨팅사고_10주차_과제정답.ipynb"
T, S, BOTH = "think", "solve", "both"

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
    """문제 N 표지 — 다섯 문제의 시작을 알리는 띠"""
    return (f'<div style="background:#1F2937;color:#F9FAFB;padding:14px 22px;border-radius:12px;margin:12px 0;{BOX}">'
            f'<span style="background:#F59E0B;color:#1F2937;padding:3px 14px;border-radius:999px;font-weight:bold;">문제 {n}</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.3em;font-weight:bold;">{title}</span>'
            f'<div style="margin-top:8px;opacity:0.92;line-height:1.7;">{fmt(question)}</div></div>')


def img_fig(filename, caption, max_width=760):
    """강의자료 폴더의 PNG 를 base64 로 본문에 넣는다. 외부 파일 없이 어디서 열어도 보인다."""
    with open(os.path.join(DEST, filename), "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return (f'<div style="text-align:center;margin:10px 0;{BOX}">'
            f'<img src="data:image/png;base64,{data}" alt="{html.escape(caption)}" '
            f'style="max-width:min(100%,{max_width}px);height:auto;background:#FFFFFF;border-radius:8px;padding:6px;">'
            f'<div style="color:#6B7280;font-size:0.9em;margin-top:4px;">{fmt(caption)}</div></div>')


# 1-4 하노이 탑 게임 — 셀을 실행하면 HTML + JavaScript 게임판이 출력에 나타난다 (JupyterLab 은 실행된 셀의 HTML 출력 안 <script> 를 실행한다)
GAME_CELL = r'''
#@title ▶ 실행하세요 — 하노이 탑 직접 해 보기 (막대기를 두 번 눌러 원반을 옮깁니다)
from IPython.display import HTML, display
import random

_uid = f"hanoi{random.randint(0, 10 ** 9)}"      # 셀을 여러 번 실행해도 게임끼리 섞이지 않게 하는 이름표

_game = r"""
<div id="UID" style="box-sizing:border-box;max-width:100%;font-family:'Malgun Gothic',sans-serif;color:#1F2937;background:#FFFFFF;border:2px solid #0EA5A4;border-radius:12px;padding:12px 16px;">
  <div style="display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;margin-bottom:8px;">
    <b style="color:#0EA5A4;">🎮 하노이 탑</b>
    <label>원반 수
      <select class="hn-count" style="font-size:1em;padding:2px 6px;margin-left:4px;">
        <option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option>
      </select>
    </label>
    <button class="hn-reset" style="background:#F3F4F6;color:#1F2937;border:1px solid #6B7280;border-radius:6px;padding:3px 12px;cursor:pointer;">다시 시작</button>
    <button class="hn-solve" style="background:#0EA5A4;color:#FFFFFF;border:none;border-radius:6px;padding:4px 12px;cursor:pointer;">자동으로 풀기</button>
    <span style="margin-left:auto;">옮긴 횟수 <b class="hn-moves" style="color:#FF6B5A;font-size:1.2em;">0</b> &nbsp;/&nbsp; 최소 <b class="hn-min">7</b> 번</span>
  </div>
  <div class="hn-board" style="display:flex;justify-content:space-around;align-items:flex-end;height:190px;background:#F9FAFB;border-radius:8px;padding:10px 6px 0;position:relative;">
  </div>
  <div style="display:flex;justify-content:space-around;margin-top:4px;font-family:Consolas,monospace;font-weight:bold;"><span>source</span><span>temp</span><span>target</span></div>
  <div class="hn-msg" style="min-height:1.6em;margin-top:6px;color:#6B7280;">막대기를 누르면 맨 위 원반을 집고, 다른 막대기를 누르면 그곳에 놓습니다.</div>
</div>
<script>
(function () {
  const root = document.getElementById("UID");
  if (!root) return;
  const COLORS = ["#FDE68A", "#FCA5A5", "#93C5FD", "#86EFAC", "#C4B5FD"];
  const board = root.querySelector(".hn-board");
  const msg = root.querySelector(".hn-msg");
  const movesEl = root.querySelector(".hn-moves");
  const minEl = root.querySelector(".hn-min");
  const countSel = root.querySelector(".hn-count");
  let n = 3, stacks = [[], [], []], selected = null, moves = 0, busy = false, timer = null;

  function reset() {
    if (timer) { clearInterval(timer); timer = null; }
    busy = false;
    n = parseInt(countSel.value, 10);
    stacks = [[], [], []];
    for (let d = n; d >= 1; d--) stacks[0].push(d);      // 큰 것(n)이 아래, 작은 것(1)이 위
    selected = null; moves = 0;
    minEl.textContent = (2 ** n - 1);
    say("막대기를 누르면 맨 위 원반을 집고, 다른 막대기를 누르면 그곳에 놓습니다.", "#6B7280");
    render();
  }
  function say(text, color) { msg.textContent = text; msg.style.color = color || "#6B7280"; }
  function render() {
    movesEl.textContent = moves;
    board.innerHTML = "";
    stacks.forEach((stack, i) => {
      const peg = document.createElement("div");
      peg.style.cssText = "flex:1;height:100%;display:flex;flex-direction:column-reverse;align-items:center;cursor:pointer;position:relative;border-radius:8px;";
      if (selected === i) peg.style.background = "#E6F7F6";
      const rod = document.createElement("div");
      rod.style.cssText = "position:absolute;bottom:0;width:8px;height:150px;background:#6B7280;border-radius:4px 4px 0 0;";
      const base = document.createElement("div");
      base.style.cssText = "width:92%;height:10px;background:#6B7280;border-radius:3px;";
      peg.appendChild(rod); peg.appendChild(base);
      stack.forEach((d, level) => {
        const disk = document.createElement("div");
        const top = (level === stack.length - 1) && selected === i;
        disk.style.cssText = "height:24px;margin-top:3px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:12px;position:relative;z-index:1;" +
          "width:" + (28 + d * 13) + "%;background:" + COLORS[d - 1] + ";border:2px solid " + (top ? "#FF6B5A" : "#1F2937") + ";" +
          (top ? "transform:translateY(-14px);box-shadow:0 4px 8px rgba(0,0,0,0.2);" : "");
        disk.textContent = d;
        peg.appendChild(disk);
      });
      peg.addEventListener("click", () => click(i));
      board.appendChild(peg);
    });
  }
  function tryMove(from, to) {
    const a = stacks[from], b = stacks[to];
    if (a.length === 0) return false;
    const d = a[a.length - 1];
    if (b.length > 0 && b[b.length - 1] < d) return false;    // 작은 원반 위에 큰 원반 — 금지
    b.push(a.pop()); moves += 1;
    return true;
  }
  function click(i) {
    if (busy) return;
    if (selected === null) {
      if (stacks[i].length === 0) { say("빈 막대기입니다. 원반이 있는 막대기를 누르세요.", "#6B7280"); return; }
      selected = i; say("원반 " + stacks[i][stacks[i].length - 1] + " 을 집었습니다. 놓을 막대기를 누르세요.", "#0EA5A4");
    } else if (selected === i) {
      selected = null; say("내려놓았습니다.", "#6B7280");
    } else {
      const d = stacks[selected][stacks[selected].length - 1];
      if (tryMove(selected, i)) {
        say("원반 " + d + " 을 옮겼습니다.", "#6B7280");
        if (stacks[2].length === n) {
          const best = 2 ** n - 1;
          say("🎉 완료! " + moves + " 번 만에 옮겼습니다." + (moves === best ? " 최소 횟수입니다!" : " (최소는 " + best + " 번)"), "#FF6B5A");
        }
      } else {
        say("⛔ 규칙 위반: 작은 원반(" + stacks[i][stacks[i].length - 1] + ") 위에 큰 원반(" + d + ")을 올릴 수 없습니다.", "#FF6B5A");
      }
      selected = null;
    }
    render();
  }
  function solve() {                                   // 1-4 의 hanoi() 와 같은 재귀로 이동 목록을 만든 뒤 한 걸음씩 보여 줍니다
    reset();
    const plan = [];
    function hanoi(k, source, target, temp) {
      if (k === 1) { plan.push([source, target]); return; }
      hanoi(k - 1, source, temp, target);
      plan.push([source, target]);
      hanoi(k - 1, temp, target, source);
    }
    hanoi(n, 0, 2, 1);
    busy = true; say("재귀가 만든 " + plan.length + " 번의 이동을 차례로 보여 줍니다…", "#0EA5A4");
    let step = 0;
    timer = setInterval(() => {
      if (step >= plan.length) { clearInterval(timer); timer = null; busy = false; say("🎉 완료! " + moves + " 번 = 2^" + n + " − 1", "#FF6B5A"); render(); return; }
      const [from, to] = plan[step++];
      tryMove(from, to); render();
    }, Math.max(120, 700 - n * 110));
  }
  root.querySelector(".hn-reset").addEventListener("click", reset);
  root.querySelector(".hn-solve").addEventListener("click", solve);
  countSel.addEventListener("change", reset);
  reset();
})();
</script>
"""

display(HTML(_game.replace("UID", _uid)))
'''

BREAK = '<div style="text-align:center;color:#6B7280;">☕ 쉬는 시간 — 10분</div>'
CHECK_HEAD = "# 🔍 자가 점검 — 수정하지 말고 실행만 하세요\n"
BLANK = '''
# 칠판의 풀이를 보며 직접 써 보세요



'''

# ───────────────────────── 셀 모으기 ─────────────────────────
CELLS = []          # (type, source, metadata, part)
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w10.py 가 사용


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
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 10주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">고급 알고리듬 — 어려운 문제를 컴퓨팅 사고로 풀다</div>
<div style="font-size:1.25em;margin-top:6px;">재귀 &nbsp;·&nbsp; 탐색과 정렬 &nbsp;·&nbsp; 그래프 모델링 &nbsp;·&nbsp; 다섯 개의 고전 문제</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; {sub}</div>
</div>
'''


md(cover("수업용 노트북(문제와 실습) — 풀이는 칠판에서 함께 만듭니다"), part=T)
md(cover("풀이판 — 수업에서 칠판에 쓴 풀이와 코드를 정리한 것입니다"), part=S)

md('''
# 10주차 학습 안내

4주차부터 9주차까지 Python 의 **문법**을 배웠습니다. 변수 · 조건 · 반복 · 함수 · 클래스. 이제 도구는 갖추어졌습니다.
이번 주에는 문법을 새로 배우지 않습니다. 대신 **문법만으로는 풀리지 않는 문제**를 다섯 개 가져와, 3주차에 배운 **컴퓨팅 사고**의 네 요소로 어떻게 풀어 가는지 봅니다.

| 교시 | 생각의 도구 | 문제 |
|:---:|:---|:---|
| **1교시** | **재귀** — 문제를 같은 모양의 더 작은 문제로 쪼갠다 | ① 하노이 탑 |
| **2교시** | **탐색과 정렬** — 절반을 버리고, 반으로 나눈다 | ② 숫자 맞히기 &nbsp; ③ 줄 세우기 |
| **3교시** | **그래프 모델링** — 문제를 점과 선으로 추상화한다 | ④ 쾨니히스베르크의 다리 &nbsp; ⑤ 미로 최단 경로 |

다섯 문제 모두 수백 년 된 고전이거나 모든 컴퓨터과학 교과서에 나오는 문제입니다. 문제 자체보다 **푸는 방법의 모양**이 중요합니다. 오늘 배운 모양은 여러분 전공의 문제에서 다시 나타납니다.

**오늘 수업을 마치면**

1. 재귀 함수의 두 조건(멈추는 경우, 작아지는 문제)을 알고, 하노이 탑처럼 ‘같은 모양의 작은 문제’로 쪼개는 문제를 재귀로 풀 수 있습니다.
2. 하나씩 보는 방법과 절반씩 버리는 방법(이진 탐색)의 차이를 횟수로 설명하고, 이진 탐색을 직접 쓸 수 있습니다.
3. 정렬이 왜 필요한지 알고, 선택 정렬과 병합 정렬이 어떻게 다른지 비교 횟수와 시간으로 보일 수 있습니다.
4. 현실 문제를 그래프(점과 선)로 추상화하고, 큐를 이용한 너비 우선 탐색으로 최단 경로를 찾을 수 있습니다.

''' + key("이 노트북을 읽는 법", "이 노트북에는 다섯 문제의 <b>설명과 그림</b>만 있고 <b>풀이와 코드는 없습니다.</b> 풀이를 먼저 보면 생각을 멈추기 때문입니다. 🤔 <b>생각해 보기</b> 상자의 질문을 놓고 먼저 스스로 궁리해 본 뒤, 수업에서 칠판의 풀이를 함께 따라갑니다. 칠판에서 나온 코드는 빈 셀에 직접 쳐 보세요.<br>회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성합니다. 노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다.<br>풀이와 정리가 들어 있는 <b>풀이판</b>은 수업이 끝난 뒤 따로 올립니다."), part=T)

md('''
# 풀이판 읽는 법

''' + key("이 노트북은 수업 뒤에 봅니다", "수업용 노트북의 다섯 문제에 대해 칠판에서 함께 만든 <b>🧠 풀이 상자</b>와 <b>완성된 코드</b>, 각 교시의 <b>정리</b>, 실습의 <b>정답 예시</b>를 모았습니다.<br>코드 셀은 <b>위에서부터 차례로</b> 실행하세요. 앞 셀에서 정의한 함수를 뒤에서 씁니다.<br>수업 시간에 빈 셀에 직접 쓴 코드와 여기의 코드를 <b>비교</b>해 보세요. 다른 점이 있다면 어느 쪽이 더 읽기 쉬운지, 둘 다 맞는지 생각해 보세요."), part=S)

# ═════════════════════════ 1교시 ═════════════════════════
md("# 1교시 · 재귀 — 문제를 같은 모양의 작은 문제로 쪼개다\n\n" + period(1, "재귀와 하노이 탑", [
    "자기 자신을 부르는 함수(재귀)가 어떻게 끝나는지 호출 스택으로 설명한다",
    "재귀의 두 조건 — 멈추는 경우와 작아지는 문제 — 를 안다",
    "하노이 탑을 ‘n−1 개 옮기기’라는 같은 모양의 작은 문제로 분해해 푼다",
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
## 1-1. 어려운 문제란 무엇인가 — 3주차를 다시 꺼내며

3주차에 컴퓨팅 사고의 네 요소를 배웠습니다. 그때는 말로만 했고, 이제는 코드로 할 수 있습니다.

| 요소 | 한 줄 뜻 | 오늘 코드에서 나타나는 모양 |
|:---|:---|:---|
| **분해**(decomposition) | 큰 문제를 작은 문제로 나눈다 | 재귀 — “n 개 문제는 n−1 개 문제 + 한 걸음”, “반으로 나누면 같은 문제 둘” |
| **패턴 인식**(pattern recognition) | 작은 경우들에서 규칙을 찾는다 | 횟수 세기 — “1,000 이면 10번, 10억이면 30번” |
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
md("## 1-4. " + problem(1, "하노이 탑 (Tower of Hanoi)", "막대기 세 개 <b>source · temp · target</b> 이 있습니다. 서로 크기가 다른 원반 n 개가 <b>작은 것이 맨 위, 큰 것이 맨 아래</b>에 오도록 source 막대기에 꽂혀 있습니다. 이 원반들을 <b>target 막대기</b>로 옮기되, 옮긴 뒤에도 <b>같은 순서</b>로 쌓여 있어야 합니다. 조건은 세 가지입니다.<br>1. temp 막대기를 <b>중간 단계</b>로 활용할 수 있습니다.<br>2. 원반은 한 번에 하나씩 옮기며, 어느 막대기에서든 <b>항상 작은 원반이 큰 원반 위에</b> 오도록 옮겨야 합니다.<br>3. 원반 수가 몇 개이든 <b>가장 적은 횟수</b>로 옮겨야 합니다. 원반 3개라면 7번보다 적게는 불가능하고, 7번보다 많으면 낭비입니다.<br>원반이 n 개일 때 최소 몇 번 옮겨야 할까요? 64개라면?") + '''

''' + img_fig("컴퓨팅사고_10주차_하노이_문제.png", "시작 상태와 목표 상태. 원반 번호가 작을수록 작은 원반입니다."), part=BOTH)

md('''
### 직접 해 보기

코드를 쓰기 전에 손으로 먼저 풀어 봅니다. 아래 셀을 실행하면 게임판이 나타납니다. 막대기를 누르면 맨 위 원반을 집고, 다른 막대기를 누르면 그곳에 놓습니다. 규칙에 어긋나면 옮겨지지 않습니다.

원반 3개를 **7번** 만에, 4개를 **15번** 만에 옮겨 보세요. 되었다면 5개는 몇 번일지 **먼저 예상**하고 해 보세요. 그리고 생각해 보세요 — **원반 4를 옮기기 직전**, 나머지 원반 세 개는 어디에 있어야 할까요?
''')

code(GAME_CELL, form=True)

md('''
1883년 프랑스 수학자 뤼카(Lucas)가 낸 퍼즐입니다. 원반 3개는 손으로 해 볼 만합니다. 7번이면 됩니다. 4개는 15번. 그런데 **방법을 말로 설명**하려면 막힙니다. “먼저 원반 1을 target 으로, 그다음 원반 2를 temp 로, 다시 원반 1을 temp 로 …” 원반이 10개면 이 설명은 1,023 줄이 됩니다.

''' + ponder("생각해 보기 — 어디서부터 생각을 시작할까", "① 원반 3개를 7번에 옮겼다면 그 7번을 <b>말로</b> 설명해 보세요. 원반 10개라면 그 설명은 몇 줄이 될까요? 더 짧게 말할 방법은 없을까요?<br>② 원반이 1개, 2개, 3개, 4개일 때 최소 횟수를 나열해 보세요. 규칙이 보이나요? 64개면 몇 번이고, 1초에 한 번씩 옮기면 몇 년일까요?<br>③ 1-3에서 재귀에는 <b>멈추는 경우</b>와 <b>작아지는 문제</b>가 있어야 한다고 했습니다. 하노이 탑에서 ‘작아진 같은 문제’는 무엇일까요? 가장 큰 원반이 움직이는 <b>그 순간</b>을 떠올려 보세요.") + '''

칠판의 풀이를 따라 아래 빈 셀에 `hanoi(n, source, target, temp)` 를 직접 써 보세요.
''')
blank()

# ── 문제 1 풀이 ──
md('''
원반 3개는 7번, 4개는 15번. 그런데 **방법을 말로 설명**하려면 막힙니다. “먼저 원반 1을 target 으로, 그다음 원반 2를 temp 로, 다시 원반 1을 temp 로 …” 원반이 10개면 이 설명은 1,023 줄이 됩니다.

''' + think("분해 — 가장 큰 원반 하나만 생각한다", "원반 n 개를 source 에서 target 으로 옮기는 일 전체를 보지 말고, <b>맨 아래 가장 큰 원반 하나</b>만 봅니다. 이 원반이 target 으로 가려면, 그 위에 있던 n−1 개가 <b>모두 temp 에</b> 비켜 있어야 합니다. 그러면 일은 세 단계가 됩니다.<br>① 위의 n−1 개를 source 에서 temp 로 옮긴다 (target 을 중간 단계로 씀)<br>② 가장 큰 원반 하나를 source 에서 target 으로 옮긴다<br>③ temp 에 있던 n−1 개를 target 으로 옮긴다 (source 를 중간 단계로 씀)<br>①과 ③은 <b>원반 n−1 개를 옮기는 같은 문제</b>입니다. 막대기 이름만 다릅니다. “n−1 개를 어떻게 옮기는가”는 묻지 않습니다. 그것은 <b>같은 함수가 알아서</b> 합니다. 원반이 1개이면 그냥 옮깁니다 — 멈추는 경우.") + '''

''' + img_fig("컴퓨팅사고_10주차_하노이_분해.png", "원반 4개의 분해. ①과 ③은 ‘원반 3개 옮기기’ — 같은 문제가 더 작아진 것입니다. 원반 3개를 어떻게 옮기는지는 묻지 않습니다.", max_width=980) + '''

게임의 **자동으로 풀기** 버튼이 바로 이 세 단계를 되풀이한 것입니다. 세 단계를 코드로 옮기면 끝입니다. 함수 이름은 `hanoi(n, source, target, temp)` — 원반 `n` 개를 `source` 에서 `target` 으로, `temp` 를 중간 단계로 써서 옮깁니다. ①에서는 target 이, ③에서는 source 가 중간 단계가 되므로 **인자의 자리만 바뀝니다.**
''', part=S)

code('''
def hanoi(n, source, target, temp):
    """원반 n 개를 source 막대기에서 target 막대기로 옮긴다. temp 는 중간 단계."""
    if n == 1:                                   # 멈추는 경우: 원반 하나는 그냥 옮긴다
        print(f"원반 1 을 {source} → {target}")
        return
    hanoi(n - 1, source, temp, target)           # ① 위의 n-1 개를 temp 로 비켜 둔다 (target 이 중간 단계)
    print(f"원반 {n} 을 {source} → {target}")    # ② 가장 큰 원반을 target 으로
    hanoi(n - 1, temp, target, source)           # ③ 비켜 둔 n-1 개를 target 으로 (source 가 중간 단계)

hanoi(3, "source", "target", "temp")
''', part=S)

md('''
출력된 7줄을 위 그림에 그려 가며 따라가 보세요. 규칙을 한 번도 어기지 않습니다. 코드 어디에도 “작은 원반 위에 큰 원반을 올리지 말라”는 검사가 **없는데도** 그렇습니다. 분해가 옳으면 규칙은 저절로 지켜집니다.

`n = 4` 로 바꾸면 15줄이 나옵니다. **코드는 한 글자도 바뀌지 않습니다.** 1,023 줄짜리 설명을 쓰지 않아도 되는 이유입니다.

### 몇 번 옮기나 — 패턴 인식

이동 횟수만 세는 함수로 바꿔 봅니다. 출력 대신 **횟수를 돌려줍니다.**
''', part=S)

code('''
def hanoi_count(n):
    if n == 1:
        return 1
    return hanoi_count(n - 1) + 1 + hanoi_count(n - 1)     # ① + ② + ③

for n in range(1, 11):
    print(n, hanoi_count(n))
''', part=S)

md('''
1, 3, 7, 15, 31, 63, … 보이나요? **다음 수 = 앞의 수 × 2 + 1**, 즉 $2^n - 1$ 입니다. 작은 경우를 나열해 규칙을 찾는 것이 **패턴 인식**입니다. 규칙을 찾으면 재귀 없이 바로 계산할 수 있습니다.
''', part=S)

code('''
moves = 2 ** 64 - 1
print(f"원반 64개: {moves:,} 번")
seconds = moves                           # 1초에 한 번 옮긴다면
years = seconds / (60 * 60 * 24 * 365)
print(f"1초에 한 번씩 옮기면 약 {years:,.0f} 년")
''', part=S)

md(note("전설", "인도 베나레스의 사원에서 승려들이 황금 원반 64개를 옮기고 있으며, 다 옮기면 세상이 끝난다는 이야기가 퍼즐과 함께 전해집니다. 위 계산대로라면 약 5,850억 년이 걸리니 걱정하지 않아도 됩니다. 우주의 나이(약 138억 년)의 40배가 넘습니다. 이것이 <b>지수적 증가</b>($2^n$)의 크기입니다. 2교시에서는 거꾸로, <b>반씩 줄이면</b> 얼마나 빨리 끝나는지 봅니다."), part=S)

md(key("1교시 정리", "① 재귀 = 같은 모양의 더 작은 문제를 자기 자신에게 맡기기. <b>멈추는 경우</b>와 <b>작아지는 문제</b>가 필요합니다.<br>② 하노이 탑은 ‘가장 큰 원반 하나’만 보면 세 줄로 풀립니다. 이것이 <b>분해</b>입니다.<br>③ 분해가 옳으면 규칙 검사 없이도 규칙이 지켜집니다. 코드는 짧고, n 이 커져도 바뀌지 않습니다.<br>④ 작은 경우를 나열해 $2^n - 1$ 을 찾는 것이 <b>패턴 인식</b>입니다. 64개면 우주 나이의 40배."), part=S)

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
         "수업에서 본 `hanoi` 는 `print` 를 했습니다. 이번에는 이동을 <b>리스트로 모아 돌려주는</b> `hanoi_moves(n, source, target, temp)` 를 쓰세요. 각 이동은 `(출발 막대기, 도착 막대기)` 튜플입니다.<br>힌트: 멈추는 경우는 `[(source, target)]` 하나짜리 리스트. 작아지는 경우는 ① 의 리스트 + `[(source, target)]` + ③ 의 리스트 — 리스트 덧셈(5주차)으로 이어 붙입니다.<br>`hanoi_moves(2, \"A\", \"C\", \"B\")` → `[(\"A\", \"B\"), (\"A\", \"C\"), (\"B\", \"C\")]` (막대기 이름은 아무 문자열이나 됩니다)",
         '''
# 여기에 함수를 정의하세요


moves = hanoi_moves(3, "A", "C", "B")
print(len(moves), "번")
print(moves)
''',
         'hanoi_moves(1, "A", "C", "B") == [("A", "C")] and hanoi_moves(2, "A", "C", "B") == [("A", "B"), ("A", "C"), ("B", "C")] and len(hanoi_moves(3, "A", "C", "B")) == 7 and hanoi_moves(3, "A", "C", "B")[3] == ("A", "C") and len(hanoi_moves(10, "A", "C", "B")) == 1023',
         '''
def hanoi_moves(n, source, target, temp):
    if n == 1:
        return [(source, target)]
    return (hanoi_moves(n - 1, source, temp, target)      # ① 위의 n-1 개를 temp 로
            + [(source, target)]                          # ② 가장 큰 원반
            + hanoi_moves(n - 1, temp, target, source))   # ③ 비켜 둔 n-1 개를 target 으로

moves = hanoi_moves(3, "A", "C", "B")
print(len(moves), "번")                 # 7 번
print(moves)
''', raises=True)

md(BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md("# 2교시 · 탐색과 정렬 — 절반을 버리고, 반으로 나누다\n\n" + period(2, "숫자 맞히기와 줄 세우기", [
    "하나씩 보는 방법(선형 탐색)과 절반씩 버리는 방법(이진 탐색)의 차이를 횟수로 확인한다",
    "이진 탐색을 반복과 재귀 두 가지로 쓰고, 무엇을 쓸지 고르는 기준을 세운다",
    "정렬이 왜 필요한지 알고, 가장 단순한 정렬(선택 정렬)을 손으로 해 본다",
    "‘반으로 나눠 각각 정렬한 뒤 합치기’(병합 정렬)가 하노이 탑과 같은 재귀임을 안다",
]), part=BOTH)

# ── 문제 2 ──
md("## 2-1. " + problem(2, "숫자 맞히기 — 몇 번이면 반드시 맞힐까", "친구가 1 부터 1,000 사이의 정수 하나를 마음속에 정했습니다. 여러분이 수를 말하면 친구는 <b>“더 커” · “더 작아” · “맞았어”</b> 셋 중 하나로만 답합니다. 친구가 어떤 수를 정했든 <b>반드시</b> 맞히려면 질문이 최대 몇 번 필요할까요? 범위가 1 부터 10억이면?"), part=BOTH)

md('''
1 부터 차례로 “1이야?”, “2야?” 하고 물을 수도 있습니다. 운이 나쁘면 1,000번. 10억이면 10억 번입니다. 그런데 친구의 답에는 “맞았어”만 있는 것이 아닙니다. **“더 커” · “더 작아”** 가 있습니다. 이 정보를 쓰지 않고 있습니다.

''' + ponder("생각해 보기 — 한 번의 질문으로 얼마나 많이 버릴 수 있나", "① 첫 질문으로 어떤 수를 말하겠습니까? 왜 그 수인가요? “1” 이라고 말하면 답을 듣고 후보가 몇 개 남나요? “500” 이라고 말하면?<br>② 가장 좋은 질문을 계속하면 후보는 1,000 → ? → ? → … 어떻게 줄어드나요? 1 개가 남을 때까지 몇 번 걸리나요?<br>③ 범위가 10억이면 몇 번일까요? 범위가 2배가 되면 질문은 몇 번 늘어나나요? 규칙을 식으로 적어 보세요.<br>④ 이 방법이 통하려면 ‘더 커 · 더 작아’라는 답이 가능해야 합니다. 즉 후보들에 <b>순서</b>가 있어야 합니다. 순서가 없는 것(예: 사람 이름 목록에서 한 명 찾기)에도 쓸 수 있을까요?") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요. 숫자 맞히기를 흉내 내는 함수부터 시작합니다.
''')
blank()

# ── 문제 2 풀이 ──
md('''
1 부터 차례로 물으면 운이 나쁘면 1,000번입니다. 친구의 답 **“더 커” · “더 작아”** 를 쓰지 않고 있습니다.

''' + think("분해 — 절반을 버린다", "<b>가운데</b>를 묻습니다. “500 이야?” 답이 “더 커”이면 1 ~ 500 은 전부 버립니다. “더 작아”이면 500 ~ 1,000 을 버립니다. 어느 답이든 후보가 <b>절반</b>으로 줍니다.<br>1,000 → 500 → 250 → 125 → 62 → 31 → 15 → 7 → 3 → 1. <b>10번</b>이면 반드시 맞힙니다.<br>남은 후보 안에서 또 가운데를 묻습니다 — <b>같은 문제가 절반 크기로</b> 된 것입니다. 하노이 탑과 같은 분해입니다. 후보가 하나이면 그것이 답 — 멈추는 경우.<br>질문 k 번이면 $2^k$ 개까지 가립니다. 10억은 $2^{30}$ 보다 작으니 <b>30번</b>이면 됩니다. 하노이 탑의 $2^n$ 을 거꾸로 쓴 것입니다. 이렇게 정렬된 후보에서 절반씩 버리며 찾는 것을 <b>이진 탐색</b>(binary search)이라고 합니다.") + '''

숫자 맞히기를 그대로 코드로 옮깁니다. 후보 범위를 `low` 와 `high` 두 변수로 들고, 가운데 `mid` 를 묻습니다.
''', part=S)

code('''
def guess(secret, low=1, high=1000):
    """친구가 정한 수 secret 을 low ~ high 안에서 가운데부터 물어 맞힌다. 질문 횟수를 돌려준다."""
    count = 0
    while low <= high:                      # 후보가 남아 있는 동안
        mid = (low + high) // 2             # 가운데를 묻는다
        count += 1
        if mid == secret:
            print(f"{count}번째 질문: {mid} → 맞았어!")
            return count
        elif mid < secret:
            print(f"{count}번째 질문: {mid} → 더 커")
            low = mid + 1                   # 왼쪽 절반을 버린다
        else:
            print(f"{count}번째 질문: {mid} → 더 작아")
            high = mid - 1                  # 오른쪽 절반을 버린다

guess(731)
''', part=S)

md('''
`secret` 을 바꿔 가며 실행해 보세요. 어떤 수도 10번 안에 맞힙니다. 가장 운이 나쁜 수는 어느 것일까요? 1 부터 1,000 까지 **전부** 넣어 보면 됩니다. 출력 없이 횟수만 세는 판을 만듭니다.
''', part=S)

code('''
def guess_count(secret, low, high):
    count = 0
    while low <= high:
        mid = (low + high) // 2
        count += 1
        if mid == secret:
            return count
        elif mid < secret:
            low = mid + 1
        else:
            high = mid - 1

for n in [10, 100, 1000]:
    worst = max(guess_count(s, 1, n) for s in range(1, n + 1))     # 모든 수를 다 넣어 보고 가장 많은 횟수
    print(f"1 ~ {n:>5,}:   최대 {worst} 번")
''', part=S)

md('''
범위가 **10배** 커질 때 질문은 **3 ~ 4번**만 늘어납니다. 범위가 **2배**가 되면 질문은 정확히 **한 번** 늘어납니다 — 질문 k 번으로 $2^k$ 개까지 가릴 수 있으니, 필요한 횟수는 $2^k \\geq n$ 인 가장 작은 $k$, 즉 약 $\\log_2 n$ 입니다. 100만이면 20번, 10억이면 30번($2^{30} \\approx 10.7$억). 하나씩 묻는 방법(10억 번)과 비교하면 3천만 배 차이입니다. 이것이 ‘절반 버리기’의 힘입니다. (실습 2-1에서 이 횟수를 계산하는 함수를 직접 씁니다.)

## 2-2. 이진 탐색 — 정렬된 목록에서 찾기

숫자 맞히기는 사실 **“정렬된 목록에서 값 찾기”** 입니다. 1 ~ 1,000 이라는 목록이 이미 작은 순으로 놓여 있으니 가운데를 볼 수 있었습니다. 어떤 리스트든 **오름차순으로 정렬되어 있으면** 같은 방법이 통합니다. 이번에는 값이 **몇 번째**에 있는지(인덱스)를 돌려줍니다. 없으면 `-1`.
''', part=S)

code('''
def binary_search(items, target):
    """오름차순으로 정렬된 items 에서 target 의 인덱스. 없으면 -1."""
    low, high = 0, len(items) - 1           # 아직 후보인 구간
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1                   # 왼쪽 절반을 버린다
        else:
            high = mid - 1                  # 오른쪽 절반을 버린다
    return -1

scores = [12, 25, 31, 47, 58, 63, 77, 81, 90, 95]
print(binary_search(scores, 63))            # 5
print(binary_search(scores, 12))            # 0
print(binary_search(scores, 50))            # -1
''', part=S)

md('''
**예상해 보기** — 100만 개짜리 정렬된 리스트에서 맨 끝 값을 찾습니다. 하나씩 보는 **선형 탐색**은 몇 번 비교할까요? 이진 탐색은?
''', part=S)

code('''
def linear_search(items, target):
    """처음부터 하나씩 본다. (인덱스, 비교 횟수)"""
    for i, value in enumerate(items):
        if value == target:
            return i, i + 1
    return -1, len(items)

def binary_search_count(items, target):
    """이진 탐색. (인덱스, 비교 횟수)"""
    low, high, count = 0, len(items) - 1, 0
    while low <= high:
        mid = (low + high) // 2
        count += 1
        if items[mid] == target:
            return mid, count
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1, count

big = list(range(0, 2_000_000, 2))          # 0, 2, 4, …, 1,999,998 — 100만 개, 정렬됨
print("선형 탐색:", linear_search(big, 1_999_998))
print("이진 탐색:", binary_search_count(big, 1_999_998))
print("없는 값  :", binary_search_count(big, 7))
''', part=S)

md('''
100만 번과 20번. 같은 답을 내는데 일의 양이 5만 배 다릅니다. **알고리듬의 선택이 컴퓨터의 속도보다 중요한** 이유입니다.

단, 이진 탐색에는 전제가 하나 있습니다. **정렬되어 있어야 합니다.** 뒤죽박죽인 리스트에 쓰면 어떻게 될까요?
''', part=S)

code('''
messy = [47, 12, 90, 31, 77, 25]
print(binary_search(messy, 12))             # 12 가 있는데도…
print(messy.index(12))                      # 실제 위치
''', part=S)

md('''
`-1` — 있는 값을 “없다”고 답합니다. 가운데 `31` 보다 `12` 가 작으니 오른쪽을 버렸는데, `12` 는 왼쪽이 아니라 두 번째에 있었습니다. 절반을 버리는 논리는 **순서가 있을 때만** 성립합니다. 그래서 탐색 앞에는 **정렬**이 옵니다. 그것이 문제 3입니다.

## 2-3. 재귀와 반복 — 무엇을 쓸까

`binary_search` 는 `while` 로 썼습니다. 🧠 상자의 “남은 후보 안에서 같은 문제”라는 말 그대로 **재귀로** 쓸 수도 있습니다. 작아지는 문제는 `low`, `high` 가 좁아진 구간, 멈추는 경우는 구간이 비는 것입니다.
''', part=S)

code('''
def binary_search_rec(items, target, low, high):
    if low > high:                                            # 멈추는 경우: 후보가 없다
        return -1
    mid = (low + high) // 2
    if items[mid] == target:                                  # 멈추는 경우: 찾았다
        return mid
    if items[mid] < target:
        return binary_search_rec(items, target, mid + 1, high)   # 오른쪽 절반 — 같은 문제, 더 작게
    return binary_search_rec(items, target, low, mid - 1)        # 왼쪽 절반

print(binary_search_rec(scores, 63, 0, len(scores) - 1))
print(binary_search_rec(scores, 50, 0, len(scores) - 1))
''', part=S)

md('''
둘 다 맞습니다. 그러면 언제 무엇을 쓸까요?

| | 반복문 | 재귀 |
|:---|:---|:---|
| 어울리는 문제 | 한 줄로 쭉 가는 일 — 합계, 최댓값, 목록 훑기, 이진 탐색 | 가지를 치는 일 — 하노이 탑, 병합 정렬(2-4), 폴더 안의 폴더 |
| 생각의 방향 | “처음부터 끝까지 하나씩” | “가장 큰 한 조각만 생각하고 나머지는 자기 자신에게” |
| 비용 | 메모리가 거의 들지 않는다 | 호출마다 스택에 쌓인다. 너무 깊으면 `RecursionError` |
| 함정 | 무한 반복 · 범위(`low`, `high`) 갱신 실수 | 멈추는 경우 누락 |

이진 탐색은 다음 구간이 **하나**뿐이라(왼쪽 아니면 오른쪽) 반복문이 자연스럽습니다. 하노이 탑은 n−1 개 문제가 **두 번** 나와 가지를 치니 재귀가 자연스럽습니다. **문제의 정의가 가지를 치면 재귀, 한 줄로 가면 반복.**
''', part=S)

md(key("2-1 ~ 2-3 정리 — 이진 탐색", "① 하나씩 보면 n 번, <b>절반씩 버리면</b> $\\log_2 n$ 번. 10억 개도 30번.<br>② 가운데를 보고 왼쪽 또는 오른쪽 절반을 버린다. 후보 구간은 `low`, `high` 두 변수로 든다.<br>③ 전제: <b>정렬되어 있어야 한다.</b> 순서가 없으면 절반을 버릴 근거가 없다.<br>④ 반복과 재귀 둘 다 된다. 가지를 치지 않으니 반복이 자연스럽다."), part=S)

# ── 문제 3 ──
md("## 2-4. " + problem(3, "줄 세우기 — 정렬", "학생 n 명의 키가 뒤죽박죽 목록으로 있습니다. 키가 작은 순으로 줄을 세우려 합니다. 컴퓨터는 한 번에 <b>두 값을 비교</b>하고 <b>자리를 바꾸는</b> 일만 할 수 있습니다. 어떤 순서로 비교하고 바꿔야 할까요? 10명이면 비교를 몇 번 하나요? 100만 명이면?<br>(문제 2의 이진 탐색은 목록이 정렬되어 있어야 했습니다. 정렬은 그 준비 작업입니다.)"), part=BOTH)

md('''
```
키:  163  178  155  171  160  182  158  169  175  166      ← 10 명
```

''' + ponder("생각해 보기 — 손으로 먼저 줄 세우기", "① 위 열 명을 <b>손으로</b> 작은 순으로 정렬해 보세요. 어떤 순서로 비교했나요? 그 방법을 다른 사람에게 <b>말로</b> 설명해 보세요. 설명이 되면 그것이 알고리듬입니다.<br>② 그 방법으로 n 명을 정렬하면 비교를 몇 번 하나요? 10명이면? 100만 명이면? (하노이 탑처럼 작은 경우부터 세어 보세요.)<br>③ 하노이 탑에서는 ‘가장 큰 원반 하나’만 생각했습니다. 줄 세우기에서는 무엇 하나만 생각하면 될까요?<br>④ 목록을 <b>반으로 나누면</b> 두 개의 같은 문제가 됩니다. 반씩 정렬된 두 줄이 있다면 하나의 줄로 <b>합치는</b> 일은 쉬울까요? 두 줄의 <b>맨 앞</b>만 보면 되지 않을까요?") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요. 손으로 한 방법부터 코드로 옮깁니다.
''')
blank()

# ── 문제 3 풀이 ──
md('''
```
키:  163  178  155  171  160  182  158  169  175  166      ← 10 명
```

''' + think("가장 작은 사람 하나만 생각한다 — 선택 정렬", "줄 전체를 보지 말고 <b>맨 앞자리에 설 사람 하나</b>만 생각합니다. 열 명 중 가장 작은 사람(155)을 찾아 맨 앞 사람과 자리를 바꿉니다. 이제 맨 앞은 끝났습니다. 남은 아홉 명에서 가장 작은 사람을 찾아 두 번째 자리와 바꿉니다. … <b>같은 일이 한 명 줄어든 채</b> 되풀이됩니다. 이것을 <b>선택 정렬</b>(selection sort)이라고 합니다.<br>비교 횟수: 가장 작은 사람을 찾으려면 나머지 전부와 비교해야 하니 9 + 8 + … + 1 = <b>45번</b>. n 명이면 $n(n-1)/2$, 약 $n^2/2$ 번. 100만 명이면 <b>5천억 번</b>입니다.") + '''
''', part=S)

code('''
def selection_sort(items):
    """가장 작은 것을 찾아 앞으로 보내기를 되풀이한다. 새 리스트를 돌려준다. (원본은 그대로)"""
    result = list(items)                              # 복사본을 정렬합니다 (5주차: 리스트는 참조)
    n = len(result)
    for i in range(n - 1):                            # i 번째 자리를 채운다
        smallest = i
        for j in range(i + 1, n):                     # 남은 것 중 가장 작은 것을 찾는다
            if result[j] < result[smallest]:
                smallest = j
        result[i], result[smallest] = result[smallest], result[i]     # 자리를 바꾼다
    return result

heights = [163, 178, 155, 171, 160, 182, 158, 169, 175, 166]
print(selection_sort(heights))
print(heights)                                        # 원본은 그대로
''', part=S)

md('''
비교 횟수를 직접 세어 봅니다. 안쪽 `for` 가 한 번 돌 때마다 비교 한 번입니다.
''', part=S)

code('''
def selection_sort_count(items):
    result, n, count = list(items), len(items), 0
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            count += 1
            if result[j] < result[smallest]:
                smallest = j
        result[i], result[smallest] = result[smallest], result[i]
    return count

import random
for n in [10, 100, 1000]:
    data = [random.randint(140, 200) for _ in range(n)]
    print(f"{n:>5} 명: 비교 {selection_sort_count(data):>8,} 번   (n(n-1)/2 = {n * (n - 1) // 2:,})")
''', part=S)

md('''
10배 많은 사람을 세우는 데 **100배**의 비교가 듭니다. 100만 명이면 5천억 번 — 1초에 1억 번 비교해도 1시간 반입니다. 더 나은 방법이 있을까요? 1교시의 분해를 다시 꺼냅니다.

''' + think("분해 — 반으로 나누어 각각 정렬하고, 합친다 (병합 정렬)", "열 명을 <b>다섯 명씩 두 줄</b>로 나눕니다. 각 줄을 정렬하는 것은 <b>같은 문제가 절반 크기로</b> 된 것이니 같은 함수에 맡깁니다(재귀). 한 명짜리 줄은 이미 정렬되어 있습니다 — 멈추는 경우.<br>남은 일은 <b>정렬된 두 줄을 하나로 합치기</b>뿐입니다. 이것은 쉽습니다. 두 줄의 <b>맨 앞</b>을 비교해 작은 쪽을 꺼내 새 줄에 붙입니다. 한쪽이 비면 다른 쪽을 통째로 붙입니다. n 명이면 비교 n 번 이하.<br>이것을 <b>병합 정렬</b>(merge sort)이라고 합니다. 하노이 탑의 ‘n−1 개 문제 둘 + 한 걸음’과 똑같은 모양입니다. ‘절반 문제 둘 + 합치기’.<br>비교 횟수: 반으로 나누는 층이 $\\log_2 n$ 개이고 각 층에서 합치기에 n 번. 합해서 약 $n \\log_2 n$. 100만 명이면 <b>2천만 번</b> — 5천억 번의 2만 분의 1입니다.") + '''

합치기(`merge`)부터 씁니다. 정렬된 두 리스트를 받아 정렬된 하나를 돌려줍니다.
''', part=S)

code('''
def merge(left, right):
    """정렬된 두 리스트를 하나의 정렬된 리스트로 합친다. 두 줄의 맨 앞만 비교한다."""
    result = []
    i, j = 0, 0                                   # 각 줄에서 다음에 볼 자리
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:                   # 맨 앞끼리 비교해 작은 쪽을 꺼낸다
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])                       # 한쪽이 비었으면 남은 쪽을 통째로 붙인다
    result.extend(right[j:])
    return result

print(merge([155, 160, 163, 171, 178], [158, 166, 169, 175, 182]))
''', part=S)

md('''
이제 병합 정렬은 세 줄입니다. 하노이 탑의 세 줄과 비교해 보세요.
''', part=S)

code('''
def merge_sort(items):
    if len(items) <= 1:                           # 멈추는 경우: 0 ~ 1 개는 이미 정렬됨
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid])                # ① 앞 절반을 정렬한다 — 같은 문제, 절반 크기
    right = merge_sort(items[mid:])               # ② 뒤 절반을 정렬한다
    return merge(left, right)                     # ③ 둘을 합친다

print(merge_sort(heights))
''', part=S)

md('''
**예상해 보기** — 사람 수가 2배가 될 때 선택 정렬과 병합 정렬의 시간은 각각 몇 배가 될까요? Python 에 내장된 `sorted()` 와도 비교합니다.
''', part=S)

code('''
import time

for n in [1000, 2000, 4000]:
    data = [random.randint(1, 10 ** 6) for _ in range(n)]
    for name, func in [("선택 정렬", selection_sort), ("병합 정렬", merge_sort), ("sorted()", sorted)]:
        start = time.time()
        func(data)
        print(f"{n:>5} 개  {name:<8} {time.time() - start:7.4f} 초")
    print()
''', part=S)

md('''
선택 정렬은 2배에 **약 4배**, 병합 정렬은 **약 2배**로 늘어납니다. 100만 개가 되면 차이는 수만 배로 벌어집니다. 둘 다 같은 답을 내고, 둘 다 몇 줄짜리 코드입니다. 차이는 오직 **문제를 어떻게 쪼갰는가**입니다.

<details><summary><b>📎 더 알아보기 — Python 의 <code>sorted()</code> 는 무엇을 쓰나</b></summary>

`sorted()` 와 `list.sort()` 는 **팀소트(Timsort)** 라는 알고리듬을 씁니다. 병합 정렬을 바탕으로, 이미 정렬된 구간을 찾아 활용하도록 개선한 것입니다. 2002년 Python 개발자 팀 피터스(Tim Peters)가 만들었고, 지금은 Java 와 Android 도 씁니다. C 로 구현되어 있어 우리가 Python 으로 쓴 병합 정렬보다 훨씬 빠르지만, 비교 횟수의 **모양**($n \\log n$)은 같습니다.

실무에서는 정렬을 직접 쓰지 않고 `sorted()` 를 씁니다. 오늘 직접 쓴 이유는 “같은 문제를 다르게 쪼개면 일의 양이 얼마나 달라지는가”를 보기 위해서입니다. 정렬 알고리듬은 이 밖에도 버블 정렬(과제 3), 삽입 정렬, 퀵 정렬 등 여러 가지가 있고, 각각 쪼개는 방법이 다릅니다.

</details>
''', part=S)

md(key("2-4 정리 — 정렬", "① <b>선택 정렬</b>: 가장 작은 것 하나만 생각한다. 찾아서 앞으로, 되풀이. 비교 약 $n^2/2$ 번 — 10배 커지면 100배.<br>② <b>병합 정렬</b>: 반으로 나눠 각각 정렬(재귀)하고 <b>합친다</b>. 합치기는 두 줄의 맨 앞만 비교. 비교 약 $n \\log_2 n$ 번 — 10배 커지면 약 13배.<br>③ 하노이 탑 · 이진 탐색 · 병합 정렬은 모두 <b>같은 문제를 더 작게</b> 만드는 분해입니다. 반으로 나누면 $\\log_2 n$ 층이면 끝납니다.<br>④ 정렬은 <b>탐색의 준비 작업</b>입니다. 한 번 정렬해 두면 그 뒤의 모든 탐색이 30번이면 끝납니다."), part=S)

# ── 2교시 실습 ──
practice("✏️ 실습 2-1", "몇 번이면 맞힐까 — 절반 버리기 횟수", "약 4분",
         "후보가 `n` 개일 때(1 부터 `n` 까지), 가운데를 묻는 방법으로 <b>반드시</b> 맞히는 데 필요한 최대 질문 수를 돌려주는 `guess_steps(n)` 을 쓰세요.<br>힌트: 후보를 절반씩 줄입니다. `n` 을 `n // 2` 로 바꾸며 <b>0 이 될 때까지</b> 몇 번 걸리는지 세면 됩니다. 1,000 → 500 → 250 → … → 1 → 0.<br>`guess_steps(1)` → `1`, `guess_steps(1000)` → `10`, `guess_steps(10 ** 9)` → `30`",
         '''
# 여기에 함수를 정의하세요


for n in [1, 2, 10, 100, 1000, 10 ** 6, 10 ** 9]:
    print(f"{n:>13,} 개 → 최대 {guess_steps(n)} 번")
''',
         "[guess_steps(n) for n in [1, 2, 3, 4, 10, 100, 1000]] == [1, 2, 2, 3, 4, 7, 10] and guess_steps(10 ** 6) == 20 and guess_steps(10 ** 9) == 30",
         '''
def guess_steps(n):
    count = 0
    while n > 0:                 # 후보가 남아 있는 동안
        n = n // 2               # 가운데를 물으면 (최악의 경우) 절반이 남는다
        count += 1
    return count

for n in [1, 2, 10, 100, 1000, 10 ** 6, 10 ** 9]:
    print(f"{n:>13,} 개 → 최대 {guess_steps(n)} 번")       # 1 2 4 7 10 20 30
''', raises=True, heading="## 2교시 실습")

practice("✏️ 실습 2-2", "이진 탐색 — 직접 쓰기", "약 6분",
         "<b>오름차순으로 정렬된</b> 리스트 `items` 에서 `target` 의 인덱스를 돌려주는 `binary_search(items, target)` 을 수업의 코드를 <b>보지 않고</b> 쓰세요. 없으면 `-1`. `items.index()` 와 `in` 은 쓰지 않습니다.<br>🧠 후보 구간을 `low`, `high` 로 들고 가운데 `mid` 를 봅니다. 같으면 찾았고, `target` 이 더 크면 `low = mid + 1`, 더 작으면 `high = mid - 1`. 구간이 비면(`low > high`) 없는 것입니다.<br>`binary_search([1, 3, 5, 7, 9, 11], 7)` → `3`",
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
        elif items[mid] < target:
            low = mid + 1                     # 왼쪽 절반을 버린다
        else:
            high = mid - 1                    # 오른쪽 절반을 버린다
    return -1

data = [1, 3, 5, 7, 9, 11]
print(binary_search(data, 7), binary_search(data, 1), binary_search(data, 11), binary_search(data, 4))     # 3 0 5 -1
''', raises=True)

practice("✏️ 실습 2-3", "두 줄 합치기 — merge (도전)", "",
         "정렬된 두 리스트 `left`, `right` 를 받아 <b>정렬된 하나의 리스트</b>로 합쳐 돌려주는 `merge(left, right)` 를 쓰세요. `sorted()` 와 `sort()` 는 쓰지 않습니다.<br>🧠 두 줄의 <b>맨 앞</b>만 비교합니다. 작은 쪽을 꺼내 결과에 붙이고 그 줄의 자리를 한 칸 옮깁니다(`i` 또는 `j`). 한쪽이 비면 다른 쪽의 남은 것을 통째로 붙입니다. 원본 두 리스트는 바꾸지 않습니다.<br>`merge([1, 4, 9], [2, 3, 10])` → `[1, 2, 3, 4, 9, 10]`. (시간이 남는 사람만) 이 `merge` 로 `merge_sort` 까지 써 보세요.",
         '''
# 여기에 함수를 정의하세요


print(merge([1, 4, 9], [2, 3, 10]))
print(merge([], [5, 6]))
''',
         'merge([1, 4, 9], [2, 3, 10]) == [1, 2, 3, 4, 9, 10] and merge([], [5, 6]) == [5, 6] and merge([7], []) == [7] and merge([1, 1, 2], [1, 3]) == [1, 1, 1, 2, 3] and merge(list(range(0, 100, 2)), list(range(1, 100, 2))) == list(range(100))',
         '''
def merge(left, right):
    result = []
    i, j = 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

print(merge([1, 4, 9], [2, 3, 10]))        # [1, 2, 3, 4, 9, 10]
print(merge([], [5, 6]))                   # [5, 6]
''', raises=True)

md(BREAK)

# ═════════════════════════ 3교시 ═════════════════════════
md("# 3교시 · 그래프 모델링 — 문제를 점과 선으로 추상화하다\n\n" + period(3, "쾨니히스베르크의 다리와 미로 최단 경로", [
    "현실의 문제에서 중요하지 않은 것을 지워 점과 선(그래프)으로 바꾼다",
    "그래프를 딕셔너리로 표현하고, 차수를 세어 오일러의 정리로 답한다",
    "미로를 그래프로 보고, 큐를 이용한 너비 우선 탐색으로 최단 경로를 찾는다",
    "오늘 배운 네 가지 생각의 틀을 한 표로 정리한다",
]), part=BOTH)

# ── 문제 4 ──
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
''', part=BOTH)

md(ponder("생각해 보기 — 무엇을 지울 수 있나", "① 다리 7개를 한 번씩만 건너는 순서를 직접 찾아보세요. 몇 번 실패하면 ‘없다’고 <b>확신</b>할 수 있을까요? 모든 순서를 다 시도하면 몇 가지일까요?<br>② 이 문제에서 땅의 <b>모양</b>, 다리의 <b>길이</b>, 강의 <b>폭</b>은 중요한가요? 지워도 되는 것을 모두 지우고 그림을 <b>다시 그려</b> 보세요. 무엇이 남나요?<br>③ 산책 <b>중간에</b> 지나가는 땅에서는 다리를 몇 개 쓰나요? 그 수에 어떤 조건이 붙을까요? 출발점과 도착점은 다를까요?<br>④ 남은 그림을 5주차의 자료형(리스트 · 딕셔너리) 중 무엇으로 적을 수 있을까요?") + '''

칠판의 풀이를 따라 아래 빈 셀에 써 보세요.
''')
blank()

# ── 문제 4 풀이 ──
md(think("추상화 — 중요하지 않은 것을 지운다", "산책에서 중요한 것은 무엇일까요? 땅의 <b>모양</b>은 상관없습니다. 다리의 <b>길이</b>도, 강의 <b>폭</b>도 상관없습니다. 중요한 것은 두 가지뿐입니다. <b>어떤 땅들이 있고, 어떤 다리가 어느 땅을 잇는가.</b><br>그래서 땅을 <b>점</b>으로, 다리를 <b>선</b>으로 바꿉니다. 지도가 아니라 점 4개와 선 7개짜리 그림이 됩니다. 이것이 <b>그래프</b>(graph)입니다 — 통계 그래프가 아니라 ‘점과 선의 구조’라는 뜻의 수학 용어입니다. 점은 <b>정점</b>(vertex), 선은 <b>변</b>(edge)이라고 부릅니다.<br>오일러는 그다음 질문을 바꾸었습니다. “어떤 순서로 건너야 하나?”가 아니라 “<b>각 땅에 다리가 몇 개씩 붙어 있나?</b>”") + '''

Python 에서 그래프는 5주차의 **딕셔너리**로 표현합니다. 키는 정점, 값은 그 정점에서 선으로 이어진 정점들의 리스트입니다. 다리가 두 개면 이름이 두 번 들어갑니다.
''', part=S)

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
''', part=S)

md('''
한 정점에 붙은 선의 수를 그 정점의 **차수(degree)** 라고 합니다. N 은 3, W 는 5, E 는 3, S 는 3. **모두 홀수**입니다.

''' + think("패턴 인식 — 왜 차수가 답을 결정하나", "산책 중간에 지나가는 땅을 생각합니다. 그 땅에 <b>들어오는</b> 다리 하나, <b>나가는</b> 다리 하나를 씁니다. 다시 들르면 또 둘. 모든 다리를 한 번씩만 쓰므로, 중간에 지나가는 땅의 다리 수는 <b>반드시 짝수</b>여야 합니다.<br>홀수 다리를 가진 땅은 <b>출발점이나 도착점</b>일 수밖에 없습니다. 출발점과 도착점은 많아야 둘. 그러므로 <b>홀수 차수의 정점이 0개 또는 2개</b>일 때만 산책길이 있습니다.<br>쾨니히스베르크는 홀수 차수 정점이 <b>4개</b>. 산책길은 <b>없습니다.</b> 다리를 하나도 건너 보지 않고 답했습니다.") + '''

이 판단을 함수로 씁니다. 그래프 하나를 받아 “모든 선을 한 번씩 지나는 길이 있는가”를 돌려줍니다. 이런 길을 **오일러 경로(Euler path)** 라고 합니다.
''', part=S)

code('''
def odd_degree_vertices(graph):
    """차수가 홀수인 정점의 목록"""
    return [v for v, neighbors in graph.items() if len(neighbors) % 2 == 1]

def has_euler_path(graph):
    """모든 변을 정확히 한 번씩 지나는 길이 있으면 True (홀수 차수 정점이 0 개 또는 2 개)"""
    return len(odd_degree_vertices(graph)) in (0, 2)

print(odd_degree_vertices(bridges))
print(has_euler_path(bridges))
''', part=S)

md('''
**예상해 보기** — 다리를 하나 더 놓으면 어떻게 될까요? 북쪽 땅과 남쪽 땅 사이에 여덟 번째 다리를 놓습니다. (실제로 1875년에 비슷한 다리가 놓였습니다.)
''', part=S)

code('''
import copy
bridges8 = copy.deepcopy(bridges)        # 원본을 건드리지 않도록 복사 (5주차: 리스트 · 딕셔너리는 참조)
bridges8["N"].append("S")
bridges8["S"].append("N")

print(odd_degree_vertices(bridges8))
print(has_euler_path(bridges8))
''', part=S)

md('''
홀수 차수 정점이 W 와 E 둘만 남습니다. 이제 산책길이 **있습니다.** W 에서 출발해 E 에서 끝나면 됩니다.
''', part=S)

md(note("그래프 이론의 시작, 그리고 지금", "오일러의 이 풀이가 <b>그래프 이론</b>의 출발점입니다. 290년 뒤, 같은 생각이 곳곳에 있습니다. 지하철 노선도(역 = 정점, 선로 = 변), SNS 친구 관계(사람 = 정점, 친구 = 변), 인터넷(컴퓨터 = 정점, 회선 = 변), 분자 구조(원자 = 정점, 결합 = 변). 내비게이션이 길을 찾는 것도, 검색 엔진이 중요한 페이지를 고르는 것도 그래프 위의 계산입니다. <b>복잡한 현실에서 점과 선만 남기는 추상화</b>가 이 모든 것의 첫걸음입니다.") + '''

## 3-2. 그래프를 걷기 — 이웃을 따라가며 모두 방문하기

차수만으로 답이 나오는 문제는 드뭅니다. 보통은 그래프를 **직접 걸어야** 합니다. 걷는 방법에는 두 가지가 있는데, 6주차의 **스택과 큐**가 그 둘을 나눕니다.

가장 기본적인 질문부터: “A 에서 출발해 **갈 수 있는 곳**이 어디까지인가?” 아래 `friends` 그래프에서 지민이 갈 수 있는 사람은 누구누구일까요?
''', part=BOTH)

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
''', part=BOTH)

md('''
손으로 따라가 보세요. 그리고 생각해 보세요 — 컴퓨터가 따라가게 하려면 무엇을 **기억**해야 할까요? 기억하지 않으면 어떤 일이 생길까요? 칠판의 풀이를 따라 아래 빈 셀에 써 보세요.
''')
blank()

md('''
이웃을 따라가되, **이미 가 본 곳은 다시 가지 않습니다.**
''', part=S)

code('''
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
''', part=S)

md('''
`visited` 가 없으면 지민 → 민수 → 지민 → 민수 … 를 영원히 돕니다. “가 본 곳 표시”는 그래프를 걸을 때 **빠뜨리면 안 되는 것**입니다. 재귀의 ‘멈추는 경우’와 같은 역할입니다.

큐를 썼으므로 **가까운 곳부터** 둘러봅니다. 지민의 친구(민수, 하늘)를 먼저, 그다음 친구의 친구(바다), 그다음 친구의 친구의 친구(솔). 이렇게 **가까운 순서로 넓혀 가는** 탐색을 **너비 우선 탐색(BFS, breadth-first search)** 이라고 합니다. 큐 대신 스택을 쓰면 한 방향으로 **깊이 파고드는** 깊이 우선 탐색(DFS)이 됩니다. 1교시의 재귀가 바로 스택이므로, 재귀로 쓴 탐색은 DFS 입니다.

가까운 순서로 둘러본다는 성질이 다음 문제의 열쇠입니다.
''', part=S)

# ── 문제 5 ──
md("## 3-3. " + problem(5, "미로 최단 경로", "격자 미로가 있습니다. `#` 은 벽, `.` 은 길, `S` 는 출발, `G` 는 목표입니다. 상하좌우 한 칸씩 움직일 때, S 에서 G 까지 <b>가장 짧은 길은 몇 걸음</b>일까요? 갈 수 없으면 −1 입니다.") + '''

```
S . . # . .
. # . # . .
. # . . . #
. . # # . .
# . . . . G
```
''', part=BOTH)

md(ponder("생각해 보기 — 미로도 그래프일까", "① 손으로 가장 짧은 길을 찾아보세요. 그것이 <b>정말 최단</b>이라고 어떻게 확신하나요? 모든 길을 다 찾아 비교해야 할까요?<br>② 미로의 길 칸 하나를 점으로, 이웃한 길 칸 사이를 선으로 보면 문제 4와 같은 <b>그래프</b>가 됩니다. 그러면 3-2의 ‘갈 수 있는 곳’ 방법을 그대로 쓸 수 있을까요?<br>③ ‘갈 수 있는가’와 ‘<b>몇 걸음</b>인가’는 무엇이 다른가요? 6주차의 <b>스택과 큐</b> 중 어느 쪽을 쓰면 <b>가까운 곳부터</b> 둘러보게 될까요? 가까운 곳부터 둘러보면 왜 최단 거리가 저절로 나올까요?") + '''

미로는 문자열 리스트로 둡니다. 칸은 `(행, 열)` 튜플입니다. 아래 셀의 `find` 는 글자가 있는 칸을 찾고, `neighbors` 는 상하좌우 이웃 중 격자 안이고 벽이 아닌 칸만 돌려줍니다. 이 둘은 미로를 **그래프로 보이게 하는 도구**일 뿐이고, 길을 찾는 생각은 아직 들어 있지 않습니다. 실습 3-3과 과제 5에서도 그대로 씁니다.
''')

md(think("추상화 — 미로도 그래프다", "미로의 <b>길 칸 하나</b>를 정점으로, <b>이웃한 길 칸 사이</b>를 변으로 보면 미로는 그래프입니다. 쾨니히스베르크에서 땅과 다리가 하던 역할을 칸과 이웃 관계가 합니다. 그래프가 되었으니 3-2의 `reachable` 을 쓸 수 있습니다.<br>그런데 ‘갈 수 있나’가 아니라 ‘<b>몇 걸음</b>인가’를 물었습니다. BFS 는 <b>가까운 곳부터</b> 둘러보므로, 어떤 칸에 <b>처음 도착한 순간</b>의 걸음 수가 곧 <b>최단 거리</b>입니다. 더 짧은 길이 있었다면 그 길로 먼저 도착했을 것이기 때문입니다. 그러니 `visited` 집합 대신 <b>거리를 적는 딕셔너리</b>를 두면 됩니다.") + '''

미로는 문자열 리스트로 둡니다. 칸은 `(행, 열)` 튜플입니다. 이웃은 상하좌우 네 방향인데, 격자 밖이거나 벽이면 뺍니다.
''', part=S)

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
''', part=BOTH)

md('''
칠판의 풀이를 따라 아래 빈 셀에 써 보세요. `neighbors(maze, current)` 가 그래프의 `graph[current]` 역할을 합니다.
''')
blank()

md('''
`neighbors` 가 그래프의 `graph[current]` 역할을 합니다. 미리 딕셔너리를 만들지 않고 **물을 때마다** 이웃을 계산할 뿐, 하는 일은 같습니다. 이제 3-2의 `reachable` 에 거리만 더합니다.
''', part=S)

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
''', part=S)

md('''
9걸음입니다. 미로를 손으로 따라가 확인해 보세요. 길이 여러 개인데 BFS 는 그중 가장 짧은 것을 **자동으로** 고릅니다. “모든 길을 다 찾아 비교한다”는 코드는 어디에도 없습니다. 가까운 곳부터 둘러본다는 **순서**가 그 일을 대신합니다.

거리 표 `distance` 를 미로 위에 그려 보면 물결이 퍼지듯 숫자가 번져 가는 것이 보입니다.
''', part=S)

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
''', part=S)

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
''', part=S)

md(key("3교시 정리 — 그래프", "① <b>추상화</b>: 땅과 다리, 칸과 이웃, 사람과 친구 — 모두 점과 선으로 바꾸면 <b>같은 문제</b>가 됩니다.<br>② 그래프는 딕셔너리 `{정점: [이웃들]}` 로 표현합니다. 차수 = 이웃 목록의 길이.<br>③ 오일러: 홀수 차수 정점이 0개 또는 2개일 때만 모든 변을 한 번씩 지나는 길이 있습니다. 걸어 보지 않고 답합니다.<br>④ <b>BFS</b> = 큐 + 가 본 곳 표시. 가까운 순서로 둘러보므로 <b>처음 도착한 순간이 최단 거리</b>입니다."), part=S)

# ── 3교시 실습 ──
practice("✏️ 실습 3-1", "오일러 경로 판정", "약 5분",
         "아래 그래프 `envelope` 에 대해 수업에서 본 `odd_degree_vertices` 와 `has_euler_path` 를 <b>보지 않고 다시 써서</b> 판정하세요. 그런 다음 `envelope` 에 변을 <b>하나 더해</b>(양쪽 목록에 추가) 오일러 경로가 생기게 만들고, 그 그래프를 `envelope_fixed` 에 두세요.<br>`envelope` 은 ‘봉투’ 모양입니다: 정사각형 네 꼭짓점 A B C D 와 대각선 A–C, B–D. 한붓그리기가 될까요? 🧠 어느 두 정점을 이어야 홀수 차수 정점이 둘로 줄어드는지 생각하세요.",
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
         "3-2의 `friends` 그래프에서, `start` 에서 각 사람까지의 <b>거리</b>(몇 명을 거쳐야 하는지)를 딕셔너리로 돌려주는 `bfs_distances(graph, start)` 를 쓰세요. 자기 자신은 0, 친구는 1, 친구의 친구는 2. 갈 수 없는 사람은 딕셔너리에 넣지 않습니다.<br>수업에서 본 `shortest_path_length` 와 같은 구조입니다. 목표가 없으니 큐가 빌 때까지 돌고 `distance` 전체를 돌려줍니다.<br>`bfs_distances(friends, \"지민\")` → `{\"지민\": 0, \"민수\": 1, \"하늘\": 1, \"바다\": 2, \"솔\": 3}`",
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
         "3-3의 `find`, `neighbors` 를 그대로 쓰고, S 에서 <b>갈 수 있는 길 칸의 개수</b>(S 자신 포함)를 돌려주는 `count_reachable(maze)` 를 쓰세요. 수업에서 본 `reachable` 을 미로에 맞게 고치면 됩니다. (시간이 남는 사람만)<br>위의 `maze` 에서는 길 칸 22개가 모두 닿습니다.",
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
NEXT_WEEK = f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:16px 24px;border-radius:12px;margin-top:10px;{BOX}">
<b>다음 주 — 11주차 파일 입출력과 예외 처리</b><br>
프로그램이 파일을 읽고 쓰는 법, 그리고 오류가 났을 때 멈추지 않고 <b>대처하는</b> 법(`try` · `except`)을 배웁니다. 함수를 값처럼 다루는 일급 객체와 데코레이터도 나옵니다.<br>
수업 후 <code style="background:#FFFFFF;color:#0B7C7B;padding:1px 6px;border-radius:4px;">File → Download</code> 로 오늘 작성한 노트북을 내려받아 두세요. 아래 과제도 잊지 마세요. 수고하셨습니다!
</div>
'''

md('''
# 10주차 마무리

오늘 다섯 문제를 풀며 쓴 생각의 틀은 넷이었습니다 — **재귀**(분해), **절반 버리기와 반으로 나누기**(탐색과 정렬), **횟수 세기**(패턴 인식), **그래프 모델링**(추상화). 문법은 하나도 새로 배우지 않았습니다.

칠판의 풀이와 개념 정리, 각 문제의 완성된 코드가 들어 있는 **풀이판** 노트북은 수업이 끝난 뒤 수업 사이트에 올립니다. 오늘 빈 셀에 직접 쓴 코드와 풀이판의 코드를 **비교**해 보세요.

''' + key("오늘의 한 문장", "어려운 문제는 <b>통째로</b> 풀리지 않습니다. 가장 큰 조각 하나, 절반 버리기, 반으로 나누기, 점과 선만 남기기 — <b>문제를 다시 쓰는 것</b>이 풀이의 90%이고, 코드는 그 뒤에 따라옵니다.") + "\n\n" + NEXT_WEEK)

md('''
# 10주차 정리

오늘 다섯 문제를 풀며 쓴 생각의 틀은 넷입니다. 문법은 하나도 새로 배우지 않았습니다.

| 생각의 틀 | 컴퓨팅 사고 요소 | 핵심 질문 | 오늘의 문제 |
|:---|:---|:---|:---|
| **재귀** | 분해 | “가장 큰 한 조각만 보면, 나머지는 같은 문제인가?” | 하노이 탑 · 병합 정렬 |
| **절반 버리기 · 반으로 나누기** | 분해 | “한 번에 후보의 절반을 버릴 수 있는가? 반으로 나누면 같은 문제 둘인가?” | 숫자 맞히기 · 줄 세우기 |
| **횟수 세기** | 패턴 인식 | “입력이 2배가 되면 일은 몇 배가 되는가?” | $2^n$ · $\\log_2 n$ · $n^2$ · $n \\log n$ |
| **그래프 모델링** | 추상화 | “무엇을 지우면 점과 선만 남는가?” | 쾨니히스베르크 · 미로 |

| 개념 | 한 줄 요약 |
|:---|:---|
| **재귀** | 멈추는 경우 + 작아지는 문제. 호출 스택에 쌓였다 돌아온다 |
| **이진 탐색** | 정렬된 목록에서 가운데를 보고 절반을 버린다. $\\log_2 n$ 번 — 10억 개도 30번 |
| **선형 탐색** | 처음부터 하나씩. n 번. 정렬이 필요 없는 대신 느리다 |
| **선택 정렬** | 가장 작은 것을 찾아 앞으로. 약 $n^2/2$ 번 비교 |
| **병합 정렬** | 반으로 나눠 각각 정렬(재귀)하고 합친다. 약 $n \\log_2 n$ 번 |
| **그래프** | `{정점: [이웃들]}`. 차수 = 이웃 수 |
| **오일러 경로** | 홀수 차수 정점이 0개 또는 2개일 때만 있다 |
| **BFS** | 큐 + 가 본 곳 표시. 처음 도착 = 최단 거리 |
| **지수적 증가** | $2^n$ — 64개 원반은 우주 나이의 40배. 알고리듬 선택이 컴퓨터 성능보다 중요한 이유 |

### 오늘 만난 오류와 신호

| 이름 | 뜻 | 오늘의 예 |
|:---|:---|:---|
| `RecursionError` | 재귀가 너무 깊다 | 멈추는 경우가 없다 · 입력이 작아지지 않는다 |
| 끝나지 않는 셀 | 오류는 아니지만 신호 | `low` · `high` 를 갱신하지 않은 이진 탐색 · `visited` 없는 그래프 탐색 (■ 버튼으로 중단) |
| 답은 나오는데 틀림 | 가장 무서운 신호 | 정렬되지 않은 리스트에 이진 탐색 — 있는 값을 “없다”고 한다 |
| `KeyError` | 그 키가 없다 | 그래프에 없는 정점 · `distance` 에 없는 칸 |
| `IndexError` | 격자 밖 · 리스트 끝 | `neighbors` 에서 범위 검사 누락 · `merge` 에서 빈 줄의 맨 앞을 보려 함 |

''' + key("오늘의 한 문장", "어려운 문제는 <b>통째로</b> 풀리지 않습니다. 가장 큰 조각 하나, 절반 버리기, 반으로 나누기, 점과 선만 남기기 — <b>문제를 다시 쓰는 것</b>이 풀이의 90%이고, 코드는 그 뒤에 따라옵니다. 이 방법들은 모두 수백 년 전 사람들이 종이와 연필로 찾아낸 것입니다. 컴퓨터는 그 생각을 빠르게 실행할 뿐입니다.") + "\n\n" + NEXT_WEEK, part=S)

# ═════════════════════════ 과제 ═════════════════════════ (생각하기 판에만. 정답은 교수용 파일)
FIRST_HW_CELL = len(CELLS)

md(f'''
# 10주차 과제

<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">과제</span>&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">생각의 틀 적용하기 — 재귀 · 탐색과 정렬 · 그래프</span><ul style="margin:10px 0 0 0;line-height:1.7;"><li>과제 1 ~ 4는 필수, 과제 5는 도전 문제입니다</li><li>각 문제에 <b>어떤 생각의 틀</b>을 쓰는지 적혀 있습니다. 코드보다 먼저 🤔 상자의 질문처럼 ‘무엇 하나만 생각하면 되는가’를 한국어로 적어 보세요</li><li>4 ~ 9주차의 문법과 오늘의 네 가지 틀만으로 풀 수 있습니다</li><li>제출 기한과 방법은 LearnUs 공지를 따릅니다</li></ul></div>

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 함수 이름과 매개변수 순서를 바꾸지 마세요. 점검 셀이 그 이름으로 부릅니다.<br>③ 점검 셀은 예시와 <b>다른 값</b>으로도 함수를 부릅니다. 점검 셀이 <b>끝나지 않으면</b> `low` · `high` 갱신이나 ‘가 본 곳 표시’가 빠진 것입니다. ■ 버튼으로 멈추고 고치세요.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다."))

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

practice("📝 과제 2", "정수 제곱근 — 이진 탐색으로", "",
         "<b>틀: 절반 버리기.</b> 0 이상의 정수 `n` 에 대해, 제곱이 `n` 을 넘지 않는 <b>가장 큰 정수</b>를 돌려주는 `isqrt(n)` 을 <b>이진 탐색으로</b> 쓰세요. `math.sqrt` 와 `** 0.5` 는 쓰지 않습니다.<br>🧠 답은 0 과 `n` 사이 어딘가에 있습니다 — 숫자 맞히기와 같습니다. 가운데 `mid` 를 골라 `mid * mid` 가 `n` 보다 큰지 작은지로 절반을 버립니다. 단, 정확히 맞는 수가 없을 수 있습니다(`n = 10` 이면 답은 3). 구간이 빌 때까지 돌며 <b>조건을 만족한 가장 큰 `mid`</b> 를 기억해 두세요.<br>`isqrt(16)` → `4`, `isqrt(10)` → `3`, `isqrt(0)` → `0`. 1 부터 하나씩 세면 `isqrt(10 ** 18)` 은 10억 번이지만 이진 탐색은 60번입니다.",
         '''
# 여기에 함수를 정의하세요


for n in [0, 1, 10, 16, 99, 100, 10 ** 18]:
    print(n, "→", isqrt(n))
''',
         '[isqrt(n) for n in [0, 1, 2, 3, 4, 10, 16, 99, 100, 101]] == [0, 1, 1, 1, 2, 3, 4, 9, 10, 10] and isqrt(10 ** 18) == 10 ** 9 and isqrt(10 ** 18 - 1) == 10 ** 9 - 1',
         '''
def isqrt(n):
    low, high = 0, n
    answer = 0                                # 지금까지 찾은, 제곱이 n 을 넘지 않는 가장 큰 수
    while low <= high:
        mid = (low + high) // 2
        if mid * mid <= n:
            answer = mid                      # 조건을 만족한다 — 기억해 두고
            low = mid + 1                     #   더 큰 수도 되는지 오른쪽을 본다
        else:
            high = mid - 1                    # 너무 크다 — 왼쪽 절반만
    return answer

for n in [0, 1, 10, 16, 99, 100, 10 ** 18]:
    print(n, "→", isqrt(n))                   # 0 1 3 4 9 10 1000000000
''', raises=True, show_answer=False)

practice("📝 과제 3", "버블 정렬 — 이웃끼리 비교해 바꾸기", "",
         "<b>틀: 알고리듬을 말로 적고 코드로 옮기기.</b> 세 번째 정렬 방법입니다. 리스트를 왼쪽부터 훑으며 <b>이웃한 두 값</b>을 비교해, 왼쪽이 더 크면 자리를 바꿉니다. 끝까지 한 번 훑으면 가장 큰 값이 맨 오른쪽에 가 있습니다(거품이 떠오르듯). 이것을 <b>정렬될 때까지</b> 되풀이합니다. 정렬된 <b>새 리스트</b>를 돌려주는 `bubble_sort(items)` 를 쓰세요. 원본은 바꾸지 않습니다. `sorted()` 와 `sort()` 는 쓰지 않습니다.<br>🧠 한 번 훑을 때마다 맨 오른쪽 하나가 확정되니, 다음 훑기는 그만큼 짧아도 됩니다. 훑는 동안 한 번도 바꾸지 않았다면 이미 정렬된 것이니 멈출 수 있습니다.<br>`bubble_sort([5, 1, 4, 2, 8])` → `[1, 2, 4, 5, 8]`. 비교 횟수는 선택 정렬과 같은 약 $n^2/2$ 입니다 — 왜 그런지 생각해 보세요.",
         '''
# 여기에 함수를 정의하세요


data = [5, 1, 4, 2, 8]
print(bubble_sort(data))
print(data)                               # 원본은 그대로여야 합니다
''',
         'bubble_sort([5, 1, 4, 2, 8]) == [1, 2, 4, 5, 8] and bubble_sort([]) == [] and bubble_sort([3]) == [3] and bubble_sort([2, 2, 1, 1]) == [1, 1, 2, 2] and bubble_sort(list(range(50, 0, -1))) == list(range(1, 51)) and (lambda d: (bubble_sort(d), d)[1] == [5, 1, 4, 2, 8])([5, 1, 4, 2, 8])',
         '''
def bubble_sort(items):
    result = list(items)                              # 복사본을 정렬합니다
    n = len(result)
    for end in range(n - 1, 0, -1):                   # 이번 훑기에서 확정할 마지막 자리
        swapped = False
        for i in range(end):                          # 이웃끼리 비교
            if result[i] > result[i + 1]:
                result[i], result[i + 1] = result[i + 1], result[i]
                swapped = True
        if not swapped:                               # 한 번도 안 바꿨으면 이미 정렬됨
            break
    return result

data = [5, 1, 4, 2, 8]
print(bubble_sort(data))                  # [1, 2, 4, 5, 8]
print(data)                               # [5, 1, 4, 2, 8]
''', raises=True, show_answer=False)

practice("📝 과제 4", "같은 점수가 몇 명 — 이진 탐색 두 번", "",
         "<b>틀: 절반 버리기 (응용).</b> <b>오름차순으로 정렬된</b> 점수 리스트 `scores` 에서 `x` 점이 <b>몇 개</b> 있는지 돌려주는 `count_score(scores, x)` 를 쓰세요. 100만 명짜리 리스트에서도 빨라야 합니다. `scores.count()` 와 `for` 로 전부 훑는 방법은 쓰지 않습니다.<br>🧠 `x` 가 <b>처음</b> 나오는 위치와 <b>마지막</b> 나오는 위치를 각각 이진 탐색으로 찾으면, 개수 = 마지막 − 처음 + 1. 처음 위치를 찾을 때는 `scores[mid] == x` 여도 멈추지 말고 <b>왼쪽을 더</b> 봅니다(과제 2의 ‘기억해 두고 계속’과 같은 요령). `x` 가 없으면 0.<br>`count_score([70, 80, 80, 80, 90], 80)` → `3`",
         '''
# 여기에 함수를 정의하세요


scores = [70, 80, 80, 80, 90]
print(count_score(scores, 80), count_score(scores, 70), count_score(scores, 75))
''',
         'count_score([70, 80, 80, 80, 90], 80) == 3 and count_score([70, 80, 80, 80, 90], 70) == 1 and count_score([70, 80, 80, 80, 90], 90) == 1 and count_score([70, 80, 80, 80, 90], 75) == 0 and count_score([], 5) == 0 and count_score([5] * 1000, 5) == 1000 and count_score([i // 10 for i in range(1000000)], 777) == 10 and count_score([i // 10 for i in range(1000000)], 100000) == 0',
         '''
def first_index(scores, x):
    """x 가 처음 나오는 인덱스. 없으면 -1"""
    low, high, found = 0, len(scores) - 1, -1
    while low <= high:
        mid = (low + high) // 2
        if scores[mid] == x:
            found = mid                       # 기억해 두고
            high = mid - 1                    #   더 왼쪽에도 있는지 본다
        elif scores[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return found

def last_index(scores, x):
    """x 가 마지막으로 나오는 인덱스. 없으면 -1"""
    low, high, found = 0, len(scores) - 1, -1
    while low <= high:
        mid = (low + high) // 2
        if scores[mid] == x:
            found = mid
            low = mid + 1                     #   더 오른쪽에도 있는지 본다
        elif scores[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return found

def count_score(scores, x):
    first = first_index(scores, x)
    if first == -1:
        return 0
    return last_index(scores, x) - first + 1

scores = [70, 80, 80, 80, 90]
print(count_score(scores, 80), count_score(scores, 70), count_score(scores, 75))     # 3 1 0
''', raises=True, show_answer=False)

practice("📝 과제 5", "미로의 최단 경로 그리기 (도전)", "",
         "<b>틀: BFS + 어디서 왔는지 기억.</b> 3-3의 `find`, `neighbors` 를 그대로 쓰고, S 에서 G 까지의 <b>최단 경로를 칸의 리스트</b>로 돌려주는 `shortest_path(maze)` 를 쓰세요. 리스트의 첫 원소는 S 의 칸, 마지막은 G 의 칸입니다. 갈 수 없으면 빈 리스트 `[]`.<br>🧠 BFS 를 돌며 `came_from[다음 칸] = 지금 칸` 을 적어 둡니다. G 에 도착하면 `came_from` 을 따라 S 까지 <b>거꾸로</b> 올라가며 모은 뒤 뒤집습니다. 1교시의 호출 스택이 돌아갈 곳을 기억하던 것과 같은 생각입니다.<br>점검 셀은 경로가 ① S 에서 시작해 G 에서 끝나고, ② 매 걸음이 상하좌우 한 칸이며 벽이 아니고, ③ 길이가 최단 거리 + 1 인지 확인합니다. 최단 경로가 여럿이면 어느 것이든 통과합니다.",
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

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 4의 자가 점검이 모두 ✅ 인지 확인합니다. (과제 5는 3교시 문제 5의 `maze` · `find` · `neighbors` 셀이 먼저 실행되어 있어야 합니다.)<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


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
    cells = [("markdown", "# 컴퓨팅사고 10주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 수업용 노트북 `" + THINK_NB + "` 맨 끝 ‘10주차 과제’의 정답 예시입니다. 과제 5는 3교시의 `maze` · `find` · `neighbors` 가 먼저 정의되어 있어야 합니다(아래 첫 코드 셀에 복사해 둠).", {})]
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
    for label, cells in [("생각하기", THINK_CELLS), ("풀이", SOLVE_CELLS)]:
        n_code = sum(1 for c in cells if c[0] == "code")
        print(f"{label}: cells={len(cells)} code={n_code}")
    # 생각하기 판에 🧠 풀이 상자 · 정답이 없고, 풀이판에 🤔 · 빈 셀 · 실습 상자가 없는지 확인
    assert not [s for t, s, m in THINK_CELLS if '">🧠' in s or "💡" in s], "생각하기 판에 풀이가 섞임"
    assert not [s for t, s, m in SOLVE_CELLS if "🤔" in s or s.startswith("# 칠판의 풀이") or ("✏️ 실습 " in s and "정답" not in s)], "풀이판에 수업용 셀이 섞임"
    print(f"practices={len(PRACTICES)} first_hw_cell={FIRST_HW_CELL}")
    if "--write" in sys.argv:
        save(to_nb(THINK_CELLS, "w10t"), os.path.join(DEST, THINK_NB))
        save(to_nb(SOLVE_CELLS, "w10s"), os.path.join(DEST, SOLVE_NB))
        save(to_nb(hw_solution_cells(), "w10h"), os.path.join(DEST, HW_SOL))
        print("saved:", THINK_NB, "/", SOLVE_NB, "/", HW_SOL)

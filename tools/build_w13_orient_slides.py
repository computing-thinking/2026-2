# 컴퓨팅사고 13주차 2교시 — AI 프로젝트 오리엔테이션 (python-pptx)
# build_w12_slides.py(12주차 1교시 개관)를 바탕으로 팀 배정 뒤 바뀐 내용(일정 · 팀 결과 · 평가 · 교수의 팀 배정 예제)을 반영. 사용: python tools/build_w13_orient_slides.py <출력.pptx>
# 디자인은 컴퓨팅사고_1주차_260827_포맷참고.pptx 를 따른다: 흰 배경 · 맑은 고딕 · 청록 0EA5A4 / 산호 FF6B5A · 둥근 카드 · 쪽번호
import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

OUT = sys.argv[1]
TEAL, TEAL_DK, CORAL, DARK, GRAY = "0EA5A4", "0B7C7B", "FF6B5A", "1F2937", "6B7280"
TINT, TINT2, AMBER_T, AMBER_DK, WHITE, LINE, LIGHT = "E6F7F6", "FFF0EE", "FFF7E6", "B45309", "FFFFFF", "BFE9E7", "F3F4F6"
FONT = "맑은 고딕"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
slides = []


def rgb(h): return RGBColor.from_string(h)


def new_slide(bg=WHITE):
    s = prs.slides.add_slide(BLANK)
    f = s.background.fill; f.solid(); f.fore_color.rgb = rgb(bg)
    slides.append(s)
    return s


def shape(s, kind, x, y, w, h, fill, line=None, line_w=None, radius=None, name=None):
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    if line: sh.line.color.rgb = rgb(line); sh.line.width = Pt(line_w or 1)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    if name: sh.name = name
    return sh


def card(s, x, y, w, h, fill, line=None, line_w=None):
    r = min(0.18 / min(w, h), 0.5)
    return shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, line_w, radius=r, name="카드")


def text(s, t, x, y, w, h, size=15, bold=False, color=DARK, align="left", valign="top", italic=False, fill=None, name=None):
    """t: 문자열(줄바꿈 \n 허용) 또는 [(text, {bold,color,size,italic}), ...] 런 목록"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name: tb.name = name
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[valign]
    if fill:
        tb.fill.solid(); tb.fill.fore_color.rgb = rgb(fill)
    runs = t if isinstance(t, list) else [(t, {})]
    p = tf.paragraphs[0]
    p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    for txt, o in runs:
        lines = txt.split("\n")
        for i, ln in enumerate(lines):
            if i > 0:
                p = tf.add_paragraph(); p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
            r = p.add_run(); r.text = ln
            f = r.font; f.name = FONT; f.size = Pt(o.get("size", size)); f.bold = o.get("bold", bold); f.italic = o.get("italic", italic)
            f.color.rgb = rgb(o.get("color", color))
            r._r.get_or_add_rPr().set("lang", "ko-KR")
            # 한글 글꼴(ea)도 맑은 고딕으로
            rPr = r._r.get_or_add_rPr()
            for tag in ("ea", "cs"):
                el = rPr.find("{http://schemas.openxmlformats.org/drawingml/2006/main}" + tag)
                if el is None:
                    from pptx.oxml.ns import qn
                    el = rPr.makeelement(qn("a:" + tag), {}); rPr.append(el)
                el.set("typeface", FONT)
    return tb


def bullets(s, items, x, y, w, h, size=15, color=DARK, space=6):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    from pptx.oxml.ns import qn
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Emu(Inches(0.22)))); pPr.set("indent", str(-Emu(Inches(0.22))))
        bu = pPr.makeelement(qn("a:buClr"), {}); c = bu.makeelement(qn("a:srgbClr"), {"val": TEAL}); bu.append(c); pPr.append(bu)
        bc = pPr.makeelement(qn("a:buChar"), {"char": "•"}); pPr.append(bc)
        for j, part in enumerate(it.split("\n")):
            if j: p.add_line_break()
            r = p.add_run(); r.text = part
            f = r.font; f.name = FONT; f.size = Pt(size); f.color.rgb = rgb(color)
            rPr = r._r.get_or_add_rPr()
            for tag in ("ea", "cs"):
                el = rPr.makeelement(qn("a:" + tag), {"typeface": FONT}); rPr.append(el)
    return tb


def badge(s, x, y, d, color, label="", size=15):
    shape(s, MSO_SHAPE.OVAL, x, y, d, d, color, name="배지")
    if label:
        text(s, label, x, y, d, d, size=size, bold=True, color=WHITE, align="center", valign="middle")


def title_bar(s, title, sub=None):
    text(s, title, 0.72, 0.42, 11.9, 0.7, size=30, bold=True, name="제목")
    if sub: text(s, sub, 0.72, 1.18, 11.9, 0.4, size=16, color=GRAY, name="부제")


def three_cards(s, items, y, h):
    x0, gap = 0.72, 0.32
    w = (11.9 - gap * 2) / 3
    for i, it in enumerate(items):
        x = x0 + i * (w + gap)
        card(s, x, y, w, h, it.get("fill", TINT))
        badge(s, x + 0.32, y + 0.36, 0.5, it.get("color", TEAL), it.get("badge", str(i + 1)), 14)
        text(s, it["head"], x + 0.98, y + 0.34, w - 1.2, 0.54, size=19, bold=True, color=it.get("hcolor", it.get("color", TEAL_DK)), valign="middle")
        text(s, it["body"], x + 0.34, y + 1.1, w - 0.68, h - 1.3, size=15)


def section(num, title, sub):
    s = new_slide(TINT)
    shape(s, MSO_SHAPE.OVAL, 9.5, 1.1, 3.6, 3.6, WHITE)
    shape(s, MSO_SHAPE.OVAL, 11.3, 4.0, 1.5, 1.5, TINT2)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.75, 2.25, 1.15, 1.15, TEAL, radius=0.2)
    text(s, num, 0.75, 2.25, 1.15, 1.15, size=30, bold=True, color=WHITE, align="center", valign="middle")
    text(s, title, 0.75, 3.6, 9, 0.9, size=40, bold=True)
    text(s, sub, 0.75, 4.65, 9, 0.5, size=18, color=TEAL_DK)
    return s




def mono(s, t, x, y, w, h, size=13, color=WHITE, fill=DARK):
    """코드 상자 — 어두운 배경에 Consolas"""
    card(s, x, y, w, h, fill)
    tb = s.shapes.add_textbox(Inches(x + 0.25), Inches(y + 0.18), Inches(w - 0.5), Inches(h - 0.36))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ln in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = ln
        f = r.font; f.name = "Consolas"; f.size = Pt(size); f.color.rgb = rgb(color)
    return tb


def arrow_right(s, x, y, w=0.36, h=0.3, color=CORAL):
    shape(s, MSO_SHAPE.RIGHT_ARROW, x, y, w, h, color)


# ───────────── 1. 표지 ─────────────
s = new_slide()
shape(s, MSO_SHAPE.OVAL, 10.2, -2.4, 5.4, 5.4, TINT)
shape(s, MSO_SHAPE.OVAL, 11.6, 3.1, 3.6, 3.6, TINT2)
text(s, "컴퓨팅사고 · 13주차 · 2교시", 0.75, 1.55, 8, 0.4, size=16, color=GRAY)
text(s, "AI 프로젝트 오리엔테이션", 0.75, 2.05, 11, 1.3, size=54, bold=True)
text(s, [("오늘 팀을 만나고 문제를 정합니다", {"color": TEAL_DK, "bold": True}), ("   ·   ", {"color": GRAY}),
         ("무엇을 · 어떻게 · 평가", {"color": CORAL, "bold": True}), ("   ·   ", {"color": GRAY}),
         ("교수가 먼저 해 본 예", {"color": TEAL_DK, "bold": True})], 0.75, 3.55, 11.5, 0.5, size=21)
text(s, "교양기초 (3학점)  ·  2026학년도 2학기  ·  연세대 미래캠퍼스", 0.75, 5.3, 10, 0.4, size=16)

# ───────────── 1b. 오늘 2교시 진행 순서 ─────────────
s = new_slide()
title_bar(s, "오늘 2교시 — 이렇게 진행합니다", "팀끼리 모여 앉은 채로 듣습니다  ·  약 50분")
steps = [["모여 앉기", "3분", "배정표의 팀 번호대로 자리를 옮깁니다", TEAL],
         ["프로젝트 개요", "15분", "왜 · 무엇을 · 일정 · 역할 · 평가 — 교수가 설명 (이 슬라이드)", TEAL],
         ["팀원 인사", "5분", "이름 · 계열 · 설문에 적은 ‘불편 3가지’ 중 하나씩. 끝나면 바로 연락처 교환(단톡방)", CORAL],
         ["역할 정하기", "5분", "문제 정의자 · 프롬프터 · 검증자 · 기록자 — 발표 회차가 따라옵니다", CORAL],
         ["문제 정하기", "20분", "개인 → 공유 → 선택 → 정의 네 단계. 목요일 3교시에 팀마다 발표 3분 + 질문 2분", CORAL]]
x0, gap = 0.72, 0.18; w = (11.9 - gap * 4) / 5; y, h = 2.0, 3.5
for i, st in enumerate(steps):
    x = x0 + i * (w + gap); c = st[3]
    card(s, x, y, w, h, TINT2 if c == CORAL else TINT)
    badge(s, x + (w - 0.5) / 2, y + 0.3, 0.5, c, str(i + 1), 14)
    text(s, st[0], x + 0.1, y + 0.95, w - 0.2, 0.5, size=17, bold=True, color=CORAL if c == CORAL else TEAL_DK, align="center", valign="middle")
    text(s, st[1], x + 0.1, y + 1.45, w - 0.2, 0.4, size=14, bold=True, color=GRAY, align="center")
    text(s, st[2], x + 0.2, y + 1.95, w - 0.4, 1.5, size=12.5)
    if i < 4: arrow_right(s, x + w - 0.08, y + 0.4, 0.3, 0.3)
card(s, 0.72, 5.75, 11.9, 1.0, AMBER_T)
text(s, "산호색 셋은 팀이 합니다. 오늘 끝날 때 팀마다 ① 역할표 ② 고른 문제(입력 · 출력 · 범위 한 줄씩)가 있어야 합니다. 팀 규칙 한 장은 목요일까지.", 0.95, 5.75, 11.5, 1.0, size=14, color=AMBER_DK, valign="middle")

# ───────────── 1c. 연락처 교환과 다음 모임까지 ─────────────
s = new_slide()
title_bar(s, "인사가 끝나면 — 연락처부터, 그리고 목요일까지", "팀은 수업 시간 50분으로는 부족합니다. 수업 밖에서 이어져야 팀입니다")
three_cards(s, [
    {"head": "연락처 교환 — 지금", "badge": "1", "color": CORAL, "fill": TINT2,
     "body": "인사 끝나자마자 단톡방(카카오톡 등)을 만들고 전원이 들어옵니다.\n방 이름은 ‘컴퓨팅사고 N팀’.\n\n팀 규칙 한 장의 ‘연락 방법’ 칸이 이것입니다. 질문은 수업 시간이나 LearnUs 메시지로."},
    {"head": "목요일 3교시까지", "badge": "2", "color": TEAL, "fill": TINT,
     "body": "팀명을 정합니다 — 한글 2 ~ 6자, 고른 문제와 관련 있게.\n오늘 고른 문제를 단톡방에서 다듬습니다 — 입력 · 출력 · 범위 한 줄씩. 팀 규칙 한 장도 완성.\n\n발표 자료는 수요일 밤까지 공용 Slides 파일의 우리 팀 자리에 (일정 뒤 슬라이드). 문제 정의자가 발표 3분을 준비합니다."},
    {"head": "추가 모임을 권장합니다", "badge": "3", "color": CORAL, "fill": TINT2,
     "body": "수업 사이에 짧게라도 한 번 모이세요. 30분이면 됩니다. 온라인(영상 통화)도 됩니다.\n\n14주차는 만드는 주입니다. 수업 세 번만으로는 완성하기 어렵습니다. 모인 기록은 과정 기록에 남깁니다."},
], 2.0, 3.6)
card(s, 0.72, 5.9, 11.9, 0.9, AMBER_T)
text(s, "연락이 끊기는 팀원이 생기면 — 팀 규칙에 적은 ‘불참 시 처리’대로 하고, 이틀 안에 교수에게 알립니다. 늦게 알리면 팀 전체가 손해를 봅니다. 기여도 평가는 이 기록을 봅니다.", 0.95, 5.9, 11.5, 0.9, size=14, color=AMBER_DK, valign="middle")

# ───────────── 2. 지금까지와 앞으로 ─────────────
s = new_slide()
title_bar(s, "지금까지와 앞으로", "도구는 손에 들었습니다. 이제 쓰는 쪽을 바꿉니다")
y, h, w = 1.95, 4.5, 5.75
card(s, 0.72, y, w, h, LIGHT); card(s, 6.87, y, w, h, TINT)
text(s, "지금까지  (4 ~ 12주차)", 1.1, y + 0.35, 5, 0.5, size=20, bold=True, color=GRAY)
text(s, "앞으로  (13 ~ 15주차)", 7.25, y + 0.35, 5, 0.5, size=20, bold=True, color=TEAL_DK)
for i, r in enumerate([["문제", "교수가 정한 문제", "팀이 스스로 찾은 내 생활의 불편"],
                       ["코드", "노트북의 빈 셀을 채움", "AI 와 함께 처음부터 만듦"],
                       ["단위", "혼자", "3 ~ 4명 팀, 역할을 돌아가며"],
                       ["결과", "자가 점검 ✅", "돌아가는 프로그램 + 과정 기록 + 발표"]]):
    ry = y + 1.1 + i * 0.8
    text(s, r[0], 1.1, ry, 0.9, 0.6, size=14, bold=True, color=GRAY, valign="middle")
    text(s, r[1], 2.0, ry, 4.2, 0.6, size=16, valign="middle")
    text(s, r[0], 7.25, ry, 0.9, 0.6, size=14, bold=True, color=TEAL_DK, valign="middle")
    text(s, r[2], 8.15, ry, 4.3, 0.6, size=16, bold=True, valign="middle")
text(s, "▶", 6.42, 3.85, 0.5, 0.5, size=20, color=CORAL, align="center", valign="middle")

# ───────────── 3. 왜 이렇게 하나 ─────────────
s = new_slide()
title_bar(s, "왜 이렇게 하나?", "AI 가 코드를 써 주는 시대, 사람의 몫은 무엇인가")
three_cards(s, [
    {"head": "현장이 이미 이렇다", "color": TEAL, "fill": TINT,
     "body": "문제를 정하고, AI 에게 코드를 요청하고, 결과를 검증한다.\n지금 프로그램이 만들어지는 방식입니다."},
    {"head": "사람의 몫 두 가지", "color": CORAL, "fill": TINT2,
     "body": "어떤 문제를 풀 것인가 — 문제 정의.\n맞게 풀렸는가 — 검증.\n1교시 언어모델의 한계(환각 · 비결정성)가 이것을 더 중요하게 만듭니다."},
    {"head": "문법을 배운 이유", "color": TEAL, "fill": TINT,
     "body": "AI 가 쓴 코드를 읽고, 고치고, 설명하기 위해서입니다.\n읽지 못하는 코드는 검증할 수 없습니다."},
], 2.0, 3.9)
text(s, "주도권은 여러분에게 — 교수는 팀을 짜 주고, 길을 잃을 때 묻는 사람입니다.", 0.72, 6.25, 11.9, 0.4, size=15, italic=True, color=GRAY)

# ───────────── 4. 섹션 01 ─────────────
section("01", "뼈대와 일정", "여섯 단계  ·  12주차에 한 번 지나간 길  ·  남은 3주")

# ───────────── 5. 여섯 단계 ─────────────
s = new_slide()
title_bar(s, "AI 응용은 이렇게 만든다 — 여섯 단계", "어떤 주제든 순서는 같습니다")
steps = [["불편 찾기", "반복되는 귀찮은 일을 적는다", "무엇이 매번 귀찮은가?"],
         ["문제로 다듬기", "입력 · 출력 · 범위를 정한다", "무엇을 넣으면 무엇이 나와야 해결인가?"],
         ["데이터 · 도구", "데이터가 어디 있는지, 어떤 라이브러리 · AI 를 쓸지", "데이터는 어디서 구하나?"],
         ["만들기", "AI 에게 요구사항을 전달해 코드를 만들고, 읽고, 고친다", "이 코드가 하는 일을 설명할 수 있나?"],
         ["검증", "여러 입력으로 돌려 보고 틀린 곳을 찾는다", "어떤 입력에서 틀리나?"],
         ["발표 · 기록", "무엇을 왜 만들었고 어디서 막혔는지 남긴다", "다른 팀이 따라 만들 수 있나?"]]
x0, gap = 0.72, 0.18; w = (11.9 - gap * 5) / 6; y, h = 2.0, 3.9
for i, st in enumerate(steps):
    x = x0 + i * (w + gap); hi = i in (1, 4)
    card(s, x, y, w, h, TINT2 if hi else TINT)
    badge(s, x + (w - 0.5) / 2, y + 0.3, 0.5, CORAL if hi else TEAL, str(i + 1), 14)
    text(s, st[0], x + 0.1, y + 0.95, w - 0.2, 0.5, size=16, bold=True, color=CORAL if hi else TEAL_DK, align="center", valign="middle")
    text(s, st[1], x + 0.16, y + 1.55, w - 0.32, 1.25, size=12.5)
    text(s, st[2], x + 0.16, y + 2.85, w - 0.32, 0.95, size=12, italic=True, color=GRAY)
text(s, "산호색 단계(② 문제로 다듬기, ⑤ 검증)가 사람의 몫입니다. 나머지는 AI 와 라이브러리가 많이 도와줍니다.", 0.72, 6.2, 11.9, 0.4, size=15, color=GRAY)

# ───────────── 6. 12주차가 축소판이었다 ─────────────
s = new_slide()
title_bar(s, "12주차 뉴스 제목 분류기가 이 뼈대의 축소판이었습니다", "여섯 단계를 한 번 지나가 봤습니다 — 이번에는 팀이 직접 밟습니다")
card(s, 0.72, 1.95, 7.6, 4.55, TINT)
for i, r in enumerate([["① 불편", "뉴스 제목을 주제별로 나누고 싶다"],
                       ["② 문제", "입력: 제목 한 줄  →  출력: 스포츠 · 경제 · 날씨 · 음식 중 하나"],
                       ["③ 데이터 · 도구", "제목 160개 CSV  ·  minirnn 라이브러리"],
                       ["④ 만들기", "import → 모델 → fit → predict  (코드 10줄)"],
                       ["⑤ 검증", "따로 떼어 둔 테스트셋 정확도 — 훈련 점수가 아니라"],
                       ["⑥ 발표 · 기록", "노트북 자체가 기록, 과제로 제출"]]):
    ry = 2.2 + i * 0.72
    text(s, r[0], 1.05, ry, 1.9, 0.55, size=15, bold=True, color=TEAL_DK, valign="middle")
    text(s, r[1], 3.0, ry, 5.1, 0.55, size=15, valign="middle")
card(s, 8.65, 1.95, 3.97, 4.55, TINT2)
text(s, "프로젝트에서는", 9.0, 2.25, 3.3, 0.5, size=19, bold=True, color=CORAL)
bullets(s, ["여섯 단계를 팀이 직접 밟습니다", "문제도, 데이터도, 도구도 팀이 고릅니다", "①② 에 시간을 가장 많이 씁니다", "잠시 뒤 교수가 밟은 길을 예로 보여 드립니다"], 9.0, 2.9, 3.3, 3.4)

# ───────────── 7. 남은 일정 ─────────────
s = new_slide()
title_bar(s, "남은 일정 — 발표 4회, 제출 1회", "회차마다 팀당 5분 — 발표 3분 + 질문 2분, 7팀 35분. 발표자는 역할이 정합니다 (다음 섹션)")
rows = [["오늘", "13주 2교시", "오리엔테이션 · 팀 인사 · 역할 · 문제 정하기", "", "", TEAL],
        ["1회차", "13주 3교시 (목)", "팀명 · 팀 규칙 · 문제 정의 마무리", "팀명 · 누구의 불편, 입력 · 출력 · 범위", "문제 정의자", CORAL],
        ["강의", "14주 1교시", "AI 개발 · 검증 도구 소개 (교수) — 챗봇(Claude · Gemini · ChatGPT) · AI API · VS Code · OpenClaw 등", "", "", TEAL],
        ["2회차", "14주 2교시", "데이터 · 도구 · 첫 코드", "데이터는 어디서, AI 에게 무엇을 요청했나", "프롬프터", CORAL],
        ["3회차", "14주 3교시", "만들기 · 검증", "어떤 입력에서 틀렸고 어떻게 고쳤나", "검증자", CORAL],
        ["제출", "15주 월요일", "AI 응용 과제물 제출 — 프로그램 + 과정 기록", "", "", GRAY],
        ["4회차", "15주 1교시", "최종 발표", "시연 + 과정 기록", "기록자 (3명 팀은 전원)", CORAL]]
y0 = 1.9
text(s, "언제", 1.95, y0, 2, 0.35, size=12, bold=True, color=GRAY)
text(s, "팀이 하는 일", 4.0, y0, 4, 0.35, size=12, bold=True, color=GRAY)
text(s, "발표 내용 (3분 + 질문 2분)", 8.25, y0, 3, 0.35, size=12, bold=True, color=GRAY)
text(s, "발표자", 11.0, y0, 1.6, 0.35, size=12, bold=True, color=GRAY)
for i, r in enumerate(rows):
    y = y0 + 0.4 + i * 0.6; c = r[5]
    card(s, 0.72, y, 11.9, 0.52, TINT2 if c == CORAL else (LIGHT if c == GRAY else TINT))
    text(s, r[0], 0.9, y, 1.0, 0.52, size=13.5, bold=True, color=c if c != TEAL else TEAL_DK, valign="middle")
    text(s, r[1], 1.95, y, 2.0, 0.52, size=13, bold=True, valign="middle")
    text(s, r[2], 4.0, y, 4.2 if r[3] else 8.5, 0.52, size=12.5, valign="middle")
    if r[3]:
        text(s, r[3], 8.25, y, 2.7, 0.52, size=12.5, valign="middle")
        text(s, r[4], 11.0, y, 1.6, 0.52, size=12.5, bold=True, color=CORAL, valign="middle")
card(s, 0.72, 6.5, 11.9, 0.55, AMBER_T)
text(s, "오늘 문제를 정하지 못하면 목요일 발표가 없고, 14주차는 만드는 데 다 써야 합니다. 제출은 15주 월요일, 발표는 그 주 1교시입니다.", 0.95, 6.5, 11.5, 0.55, size=13, color=AMBER_DK, valign="middle")

# ───────────── 7b. 발표 자료는 이렇게 ─────────────
s = new_slide()
title_bar(s, "발표 자료는 공용 Google Slides 파일에", "회차마다 파일 하나 — 교수가 만들고, 링크는 LearnUs 공지에. 팀은 자기 자리 5장 중 3장 이상을 채웁니다")
card(s, 0.72, 1.95, 7.3, 4.75, TINT)
text(s, "파일 하나의 구조 (36장)", 1.05, 2.2, 5, 0.45, size=18, bold=True, color=TEAL_DK)
card(s, 1.05, 2.8, 1.5, 0.7, LIGHT); text(s, "표지\n(교수)", 1.05, 2.8, 1.5, 0.7, size=12, align="center", valign="middle")
for i in range(7):
    x = 2.7 + i * 0.76
    hi = i == 2
    card(s, x, 2.8, 0.68, 0.7, TINT2 if hi else WHITE, line=CORAL if hi else LINE, line_w=1.5 if hi else 1)
    text(s, f"{i + 1}팀\n5장", x, 2.8, 0.68, 0.7, size=11, bold=hi, color=CORAL if hi else DARK, align="center", valign="middle")
text(s, "우리 팀 자리 5장 — 3장 이상 채웁니다", 1.05, 3.7, 6.5, 0.4, size=14, bold=True, color=CORAL)
for i, r in enumerate([["1장", "팀명 · 팀원 이름 · 이번 회차 발표자"], ["2장", "그 회차의 발표 항목 — 1회차는 누구의 불편, 입력 · 출력 · 범위"], ["3 ~ 5장", "자유 — 그림 · 화면 · 표 · 막힌 곳. 3장까지는 꼭, 4 · 5장은 있으면. 남는 장은 비워 둡니다"]]):
    y = 4.15 + i * 0.55
    badge(s, 1.05, y + 0.08, 0.4, TEAL, r[0], 10)
    text(s, r[1], 1.6, y, 6.2, 0.55, size=13.5, valign="middle")
text(s, "항목 제목은 교수가 미리 적어 둡니다. 팀은 빈칸을 채우면 됩니다. 글자 크기 18 이상, 5장을 넘기지 않습니다 — 발표는 3분입니다.", 1.05, 5.9, 6.7, 0.7, size=12.5, italic=True, color=GRAY)
card(s, 8.35, 1.95, 4.27, 4.75, TINT2)
text(s, "규칙 네 줄", 8.7, 2.2, 3.5, 0.45, size=18, bold=True, color=CORAL)
bullets(s, ["Google 계정으로 로그인해서 편집합니다. 휴대폰 · 아이패드의 Slides 앱도 됩니다.",
            "마감은 수업 전날 밤. 마감 뒤 파일은 잠깁니다(보기만).",
            "다른 팀 자리는 건드리지 않습니다. 실수로 지웠으면 바로 단톡방에 알립니다 — 되돌릴 수 있습니다.",
            "다른 팀 것을 참고했으면 기록에 ‘N팀 방식 참고’라고 적습니다. 참고는 괜찮고, 숨기는 것이 문제입니다."], 8.7, 2.8, 3.6, 3.8, size=13, space=5)

# ───────────── 8. 섹션 02 ─────────────
section("02", "교수가 먼저 해 본 예", "팀 배정 문제를 AI 와 함께 풀기  ·  여섯 단계 그대로")

# ───────────── 9. 예제 — 불편 → 문제 ─────────────
s = new_slide()
title_bar(s, "① 불편 → ② 문제 — “25명을 조건에 맞게 팀으로 나누기”", "여러분의 팀은 이렇게 정해졌습니다")
card(s, 0.72, 1.95, 4.3, 4.75, LIGHT)
text(s, "① 불편", 1.05, 2.2, 3, 0.45, size=18, bold=True, color=GRAY)
text(s, "25명을 손으로 팀 나누기.\n계열도 섞고, 관심도 맞추고, 실력도 고르게 — 한 명을 옮기면 다른 조건이 깨집니다.\n\n12주차 2교시 ‘적어낸 불편’ 표의 마지막 줄이 이것이었습니다.", 1.05, 2.75, 3.7, 3.5, size=14)
card(s, 5.3, 1.95, 7.32, 4.75, TINT)
text(s, "② 문제로 다듬기 — 세 질문", 5.65, 2.2, 6, 0.45, size=18, bold=True, color=TEAL_DK)
for i, r in enumerate([["입력", "설문 응답 CSV — 학번 · 이름 · 계열 · 코딩 자신감(1~5) · AI 사용 경험 · 관심 주제 2개"],
                       ["출력", "팀 배정표 — 팀 번호 · 이름 · 계열 · 팀 공통 관심 주제  (+ 교수용 점검표)"],
                       ["범위", "25명, 3 ~ 4명 팀. 조건은 네 가지, 중요한 순서대로:\n  계열 안 겹치게 > 관심 주제 겹치게 > 자신감 평균 고르게 > AI 경험 고르게"]]):
    y = 2.8 + i * 1.15
    badge(s, 5.65, y + 0.1, 0.45, TEAL, str(i + 1), 13)
    text(s, r[0], 6.25, y, 0.8, 0.65, size=15, bold=True, valign="middle")
    text(s, r[1], 7.05, y, 5.4, 1.1, size=13.5, valign="middle")
card(s, 5.65, 6.08, 6.62, 0.55, AMBER_T)
text(s, "다듬다가 뺀 조건 — ‘성별을 섞는다’. 3명 팀에서는 한 명이 반드시 혼자가 되어 지킬 수 없는 조건이었습니다.", 5.8, 6.15, 6.4, 0.55, size=12, color=AMBER_DK, valign="middle")

# ───────────── 10. 예제 — 데이터 · 도구 ─────────────
s = new_slide()
title_bar(s, "③ 데이터 · 도구 — 데이터가 없으면 먼저 만든다", "설문지를 설계하는 것도 프로그램 설계의 일부였습니다")
card(s, 0.72, 1.95, 6.6, 4.75, TINT)
text(s, "데이터 — Google Forms 설문 7문항", 1.05, 2.2, 6, 0.45, size=18, bold=True, color=TEAL_DK)
for i, r in enumerate([["학번 · 이름", "숫자만 · 같은 학번은 마지막 응답만"], ["계열", "객관식 4개 — 미정이면 앞으로 신청할 제1전공"],
                       ["코딩 자신감", "1 ~ 5 선형 배율"], ["AI 사용 경험", "거의 안 씀 / 가끔 씀 / 매일 씀"],
                       ["관심 주제", "6개 중 정확히 2개 체크"], ["불편 3가지", "장문형 — 배정엔 안 쓰고 팀 논의 재료"]]):
    y = 2.8 + i * 0.6
    text(s, r[0], 1.05, y, 1.7, 0.5, size=13.5, bold=True, valign="middle")
    text(s, r[1], 2.75, y, 4.4, 0.5, size=13, valign="middle")
card(s, 7.65, 1.95, 4.97, 2.3, TINT2)
text(s, "설계하다 배운 것", 8.0, 2.15, 4, 0.45, size=17, bold=True, color=CORAL)
bullets(s, ["보기에 쉼표를 쓰면 안 된다 — 체크박스 응답이 쉼표로 이어져 저장되니까", "배정에 쓰는 문항은 모두 선택형 · 필수로", "배포한 뒤에는 문항을 고치지 않는다"], 8.0, 2.65, 4.3, 1.6, size=12.5, space=3)
card(s, 7.65, 4.4, 4.97, 2.3, LIGHT)
text(s, "도구", 8.0, 4.6, 4, 0.45, size=17, bold=True)
bullets(s, ["pandas — CSV 읽기 (12주차 지도의 그 라이브러리)", "Colab 노트북 — 설문 CSV 를 올려 실행", "AI 채팅 — 기준을 글로 설명하고 코드를 요청"], 8.0, 5.1, 4.3, 1.6, size=12.5, space=3)

# ───────────── 11. 예제 — 만들기 ─────────────
s = new_slide()
title_bar(s, "④ 만들기 — 기준을 글로 쓰고, AI 가 코드를 쓰고, 읽고 고친다", "알고리듬은 10주차의 탐색이었습니다")
card(s, 0.72, 1.95, 5.75, 4.75, TINT)
text(s, "AI 에게 전달한 요구사항 (요약)", 1.05, 2.15, 5, 0.45, size=17, bold=True, color=TEAL_DK)
mono(s, "설문 응답 CSV 를 읽어 25명을 3명 기본(남으면 4명) 팀으로\n나누는 Python 코드를 써 주세요.\n기준은 중요한 순서대로\n 1. 팀 전원이 같은 계열이 되지 않게\n 2. 팀원끼리 관심 주제가 겹치게\n 3. 코딩 자신감 평균이 팀마다 비슷하게\n 4. AI 사용 경험이 팀마다 비슷하게\n출력은 학생에게 보여줄 배정표와\n교수만 볼 점검표(자신감 평균 포함) 두 가지.", 1.05, 2.65, 5.1, 2.75, size=11.5)
text(s, "② 에서 다듬은 입력 · 출력 · 조건이 그대로 요청문입니다. 문제 정의가 곧 프롬프트입니다.", 1.05, 5.5, 5.1, 1.1, size=13, italic=True, color=GRAY)
card(s, 6.87, 1.95, 5.75, 2.3, TINT2)
text(s, "AI 가 고른 방법 — 읽어 보니 10주차 탐색", 7.2, 2.15, 5.2, 0.45, size=17, bold=True, color=CORAL)
bullets(s, ["조건에서 벗어난 정도를 점수(비용)로 매긴다", "무작위로 나눈 뒤, 두 사람을 맞바꿔 점수가 나아지면 바꾸기를 반복", "처음부터 300번 다시 해 가장 좋은 것을 고른다"], 7.2, 2.65, 5.1, 1.6, size=13, space=3)
card(s, 6.87, 4.4, 5.75, 2.3, LIGHT)
text(s, "읽고 고친 것", 7.2, 4.6, 5, 0.45, size=17, bold=True)
bullets(s, ["조건마다 가중치(10 · 1 · 3 · 4 · 1)를 두어 ‘중요한 순서’를 숫자로 — 처음 코드에는 없었음", "시작 난수(SEED)를 고정 — 다시 돌려도 같은 결과가 나오도록", "문항 제목이 조금 달라도 찾도록 (공백 무시)"], 7.2, 5.1, 5.1, 1.6, size=13, space=3)

# ───────────── 12. 예제 — 검증 ─────────────
s = new_slide()
title_bar(s, "⑤ 검증 — 돌아간다고 끝이 아니다", "가짜 데이터로 먼저, 진짜 데이터로 다시, 숫자로 확인")
three_cards(s, [
    {"head": "가짜 응답으로 먼저", "badge": "1", "color": TEAL, "fill": TINT,
     "body": "설문을 받기 전에 가짜 응답 25명을 만들어 돌려 봤습니다(USE_SAMPLE).\n코드가 도는지, 표 모양이 맞는지, 팀 수가 8개인지.\n\n12주차의 테스트셋과 같은 생각입니다."},
    {"head": "진짜 데이터에서는", "badge": "2", "color": CORAL, "fill": TINT2,
     "body": "응답이 23명 — 25명이 아니었습니다.\n출석부와 학번을 대조해 미응답 2명을 찾아 행을 더했습니다.\n같은 학번이 두 번이면 마지막 응답만.\n\n데이터는 늘 조금 틀려 있습니다."},
    {"head": "점검표로 확인", "badge": "3", "color": TEAL, "fill": TINT,
     "body": "팀마다 계열 수 · 자신감 평균 · AI 경험 평균 · 관심 주제가 안 겹치는 쌍의 수를 표로.\n‘잘 됐다’는 느낌이 아니라 숫자로 봅니다.\n\n이 표는 자신감이 들어 있어 공개하지 않습니다."},
], 2.0, 3.75)
card(s, 0.72, 6.0, 11.9, 0.8, LIGHT)
text(s, "결과 — 7팀 (4명 팀 4개, 3명 팀 3개).  코드는 AI 가 썼지만, 25명이 아닌 것을 알아챈 것도, 성별 조건을 뺀 것도, 가중치를 정한 것도 사람입니다.", 0.95, 6.0, 11.5, 0.8, size=14, bold=True, valign="middle")

# ───────────── 13. 예제 — 정리 ─────────────
s = new_slide()
title_bar(s, "이 예에서 가져갈 것", "여섯 단계 중 사람이 한 일과 AI 가 한 일")
rows = [["① 불편", "25명 손으로 나누기 — 조건 하나 맞추면 다른 게 깨짐", "사람"],
        ["② 문제", "입력 CSV · 출력 배정표 · 조건 4개 순서 · 뺀 조건 1개", "사람"],
        ["③ 데이터 · 도구", "설문 7문항 설계, 쉼표 규칙 · pandas · Colab", "사람 + AI 에게 물어봄"],
        ["④ 만들기", "요구사항 → 코드 (탐색 · 비용 · 300회 재시도) → 가중치 · SEED 추가", "AI 가 쓰고 사람이 읽고 고침"],
        ["⑤ 검증", "가짜 25명 → 진짜 23명 발견 → 2명 추가 → 점검표", "사람"],
        ["⑥ 기록", "진행 개요 문서 · 노트북 · 이 슬라이드", "사람 + AI"]]
y0 = 1.95
for i, r in enumerate(rows):
    y = y0 + i * 0.62; hi = i in (1, 4)
    card(s, 0.72, y, 11.9, 0.54, TINT2 if hi else TINT)
    text(s, r[0], 1.0, y, 1.9, 0.54, size=14, bold=True, color=CORAL if hi else TEAL_DK, valign="middle")
    text(s, r[1], 2.9, y, 6.6, 0.54, size=13.5, valign="middle")
    text(s, r[2], 9.6, y, 2.9, 0.54, size=13.5, bold=True, align="right", valign="middle")
card(s, 0.72, 5.75, 11.9, 1.0, AMBER_T)
text(s, "🔑  코드를 치는 시간은 가장 짧았습니다. 시간은 기준을 정하고, 설문을 설계하고, 결과를 의심하는 데 들었습니다. 여러분 프로젝트도 같을 것입니다 — ② 와 ⑤ 에 시간을 쓰세요.", 0.95, 5.75, 11.5, 1.0, size=14, color=AMBER_DK, valign="middle")

# ───────────── 14. 섹션 03 ─────────────
section("03", "팀과 진행", "배정 결과  ·  역할과 발표 회차  ·  문제 정의 네 단계")

# ───────────── 15. 팀 배정 결과 ─────────────
s = new_slide()
title_bar(s, "팀 배정 결과", "배정표는 LearnUs 공지에 — 이름은 거기서 확인하세요")
card(s, 0.72, 1.95, 4.3, 4.75, TINT)
text(s, "구성", 1.05, 2.2, 3, 0.45, size=18, bold=True, color=TEAL_DK)
text(s, [("7", {"bold": True, "color": CORAL, "size": 44}), ("팀", {"bold": True, "size": 22})], 1.05, 2.75, 3.7, 0.9, valign="middle")
text(s, "4명 팀 4개  ·  3명 팀 3개  =  25명", 1.05, 3.7, 3.7, 0.5, size=15, bold=True)
bullets(s, ["설문 응답 + 미응답자 2명은 출석부로 보충", "주제는 아직 없습니다 — 오늘 정합니다", "팀 번호는 배정표의 번호를 씁니다"], 1.05, 4.35, 3.7, 2.2, size=13.5, space=4)
card(s, 5.3, 1.95, 7.32, 4.75, LIGHT)
text(s, "배정 기준 — 중요한 순서", 5.65, 2.2, 6, 0.45, size=18, bold=True)
for i, c in enumerate([["계열", "팀 전원이 같은 계열이 되지 않게"], ["관심 주제", "팀원끼리 관심 주제가 겹치게 — 배정표의 ‘팀 공통 관심 주제’"],
                       ["코딩 자신감", "평균이 팀마다 비슷하게 (점수는 비공개)"], ["AI 사용 경험", "팀마다 비슷하게"]]):
    y = 2.85 + i * 0.8
    badge(s, 5.65, y + 0.08, 0.45, TEAL, str(i + 1), 13)
    text(s, c[0], 6.25, y, 2.0, 0.6, size=15, bold=True, valign="middle")
    text(s, c[1], 8.25, y, 4.2, 0.6, size=14, valign="middle")
card(s, 5.65, 6.05, 6.62, 0.5, AMBER_T)
text(s, "팀을 바꿔 달라는 요청은 받지 않습니다. 이질적인 팀이 이 프로젝트의 설계입니다.", 5.8, 6.05, 6.4, 0.5, size=12.5, color=AMBER_DK, valign="middle")

# ───────────── 16. 역할 ─────────────
s = new_slide()
title_bar(s, "역할은 고정, 발표는 역할 순서대로", "2주 동안 역할을 바꾸지 않습니다. 대신 역할마다 발표 회차가 하나씩 — 모두가 한 번은 발표합니다")
roles = [["문제 정의자", "누구의 어떤 불편인지, 입력 · 출력 · 범위를 정리한다", "1회차 · 13주 3교시", "문제 정의"],
         ["프롬프터", "AI 에게 요구사항을 전달하고 코드를 받아 온다", "2회차 · 14주 2교시", "데이터 · 도구 · 첫 코드"],
         ["검증자", "받은 코드를 여러 입력으로 돌려 보고 AI 의 오류를 찾는다", "3회차 · 14주 3교시", "만들기 · 검증"],
         ["기록자", "과정과 시행착오를 기록하고 제출물을 모은다", "4회차 · 15주 1교시", "최종 발표 (4명 팀)"]]
x0, gap = 0.72, 0.26; w = (11.9 - gap * 3) / 4; y, h = 1.95, 3.3
for i, r in enumerate(roles):
    x = x0 + i * (w + gap); g = i == 3
    card(s, x, y, w, h, LIGHT if g else TINT)
    badge(s, x + 0.3, y + 0.3, 0.5, GRAY if g else TEAL, str(i + 1), 14)
    text(s, r[0], x + 0.95, y + 0.28, w - 1.1, 0.54, size=18, bold=True, color=GRAY if g else TEAL_DK, valign="middle")
    text(s, r[1], x + 0.3, y + 1.0, w - 0.6, 1.1, size=13.5)
    card(s, x + 0.3, y + 2.15, w - 0.6, 0.95, TINT2)
    text(s, [("발표  ", {"size": 12, "color": GRAY, "bold": True}), (r[2], {"bold": True, "color": CORAL, "size": 13.5}), ("\n" + r[3], {"size": 12.5})], x + 0.45, y + 2.15, w - 0.9, 0.95, valign="middle")
card(s, 0.72, 5.45, 5.75, 1.35, TINT2)
text(s, "3명 팀", 1.05, 5.55, 2, 0.4, size=16, bold=True, color=CORAL)
text(s, "기록자 없이 셋이 역할 1 ~ 3 을 맡고, 기록은 돌아가며. 최종 발표는 셋이 1분씩 — 문제 · 시연 · 검증.", 1.05, 5.95, 5.1, 0.8, size=13)
card(s, 6.72, 5.45, 5.9, 1.35, TINT)
text(s, "한 사람만 코딩하는 팀이 되지 않으려면", 7.05, 5.55, 5.3, 0.4, size=16, bold=True, color=TEAL_DK)
text(s, "발표 뒤 질문은 발표자가 아닌 팀원에게 합니다. “이 코드가 하는 일을 설명해 보세요”는 누구에게나 갑니다. 코딩 자신감이 낮은 사람이 프롬프터를 맡으면 참여가 올라갑니다.", 7.05, 5.95, 5.3, 0.85, size=13)

# ───────────── 17. 4단계 ─────────────
s = new_slide()
title_bar(s, "팀에서 문제를 고르는 네 단계 — 오늘 남은 20분", "순서가 중요합니다 — 개인 먼저, 팀은 그 다음. 목요일 3교시에 발표 3분 + 질문 2분")
steps = [["개인", "각자 겪는 불편 3가지를 적는다\n(5분)", "대화 금지\n설문에 적은 것을 써도 됩니다"],
         ["공유", "한 사람씩 돌아가며 읽는다", "평가 · 반박 없이\n듣기만"],
         ["선택", "비슷한 것을 묶고, 각자 2표씩 투표해 하나를 고른다", "다수결보다\n‘우리가 만들 수 있는가’"],
         ["정의", "고른 불편을 Python 과 AI 로 풀 수 있는 문제로 다듬는다", "세 질문에 답한다\n(다음 슬라이드)"]]
x0, gap = 0.72, 0.26; w = (11.9 - gap * 3) / 4; y, h = 2.0, 3.8
for i, st in enumerate(steps):
    x = x0 + i * (w + gap); odd = i % 2 == 1
    card(s, x, y, w, h, TINT2 if odd else TINT)
    badge(s, x + 0.3, y + 0.32, 0.5, CORAL if odd else TEAL, str(i + 1), 14)
    text(s, st[0], x + 0.95, y + 0.3, w - 1.1, 0.54, size=20, bold=True, color=CORAL if odd else TEAL_DK, valign="middle")
    text(s, st[1], x + 0.32, y + 1.1, w - 0.64, 1.3, size=15)
    text(s, "규칙", x + 0.32, y + 2.45, 1, 0.3, size=12, bold=True, color=GRAY)
    text(s, st[2], x + 0.32, y + 2.75, w - 0.64, 0.95, size=14, bold=True)
text(s, "개인 → 팀 순서로 가야, 목소리 큰 한 사람의 생각으로 바로 정해지는 것을 막을 수 있습니다.", 0.72, 6.15, 11.9, 0.4, size=15, italic=True, color=GRAY)

# ───────────── 18. 세 질문 ─────────────
s = new_slide()
title_bar(s, "다듬을 때 답할 세 질문", "세 질문에 답하지 못하면 아직 ‘문제’가 아닙니다 — 교수의 팀 배정도 이 세 줄에서 시작했습니다")
three_cards(s, [
    {"head": "입력", "badge": "in", "color": TEAL, "fill": TINT, "body": "프로그램에 무엇을 넣는가?\n\n예) 듣고 싶은 과목 목록, 한 달 지출 내역, 팀원별 가능한 시간, 설문 응답 CSV"},
    {"head": "출력", "badge": "out", "color": CORAL, "fill": TINT2, "body": "무엇이 나오면 불편이 해결된 것인가?\n\n예) 안 겹치는 시간표, 항목별 합계 그래프, 공통으로 비는 시간, 팀 배정표"},
    {"head": "범위", "badge": "≤", "color": TEAL, "fill": TINT, "body": "14주차 한 주 안에 만들 수 있는 크기인가?\n\n‘계산이 끝나는가’까지 묻습니다. 과목 30개의 조합을 전부 따질 수 있나? 조건을 먼저 걸어 줄여야 하나?"},
], 2.0, 3.6)
card(s, 0.72, 5.9, 11.9, 0.85, AMBER_T)
text(s, "🤔  “불편” 말고 “궁금한 것”, “전공에서 반복되는 작업”까지 넓혀도 됩니다. 설문에 적은 ‘불편 3가지’가 팀 배정표에 함께 있습니다 — 그것부터 읽으세요.", 0.95, 5.9, 11.5, 0.85, size=15, color=AMBER_DK, valign="middle")

# ───────────── 19. 섹션 04 ─────────────
section("04", "평가와 약속", "25점  ·  개인 점수 = 결과물 × 기여도  ·  AI 사용 규칙")

# ───────────── 20. 평가 ─────────────
s = new_slide()
title_bar(s, "평가 — 전체 100점 중 25점", "팀이 만든 결과를 교수가, 각자의 기여를 팀원이 평가합니다")
card(s, 0.72, 1.95, 5.75, 4.75, TINT)
text(s, "배점", 1.05, 2.2, 3, 0.45, size=18, bold=True, color=TEAL_DK)
text(s, [("25", {"bold": True, "color": CORAL, "size": 40}), ("점", {"bold": True, "size": 18}), ("  =  ", {"size": 18, "color": GRAY}),
         ("15", {"bold": True, "color": TEAL_DK, "size": 30}), (" 과제물", {"bold": True, "size": 15}), (" + ", {"size": 18, "color": GRAY}),
         ("10", {"bold": True, "color": TEAL_DK, "size": 30}), (" 참여도", {"bold": True, "size": 15})], 1.05, 2.75, 5.1, 1.1, valign="middle")
for i, r in enumerate([["과제물  15점", "15주 월요일에 제출하는 AI 응용 과제물 — 돌아가는 프로그램 + 과정 기록, 15주 1교시 최종 발표"],
                       ["수업 참여도  10점", "13 ~ 15주차 팀 활동 — 팀 규칙 · 역할 수행 · 발표 4회 · 다른 팀 질문"]]):
    y = 4.05 + i * 1.2
    card(s, 1.05, y, 5.1, 1.05, WHITE)
    text(s, r[0], 1.25, y + 0.08, 4.7, 0.4, size=15, bold=True, color=TEAL_DK)
    text(s, r[1], 1.25, y + 0.45, 4.7, 0.6, size=12.5)
card(s, 6.87, 1.95, 5.75, 4.75, TINT2)
text(s, "개인 점수는 이렇게 정해집니다", 7.2, 2.2, 5, 0.45, size=18, bold=True, color=CORAL)
card(s, 7.2, 2.8, 5.1, 1.0, WHITE, line=CORAL, line_w=2)
text(s, [("개인 점수  =  ", {"bold": True, "size": 17}), ("결과물 평가", {"bold": True, "size": 17, "color": TEAL_DK}), ("  ×  ", {"size": 17}), ("팀 기여도", {"bold": True, "size": 17, "color": CORAL})], 7.2, 2.8, 5.1, 1.0, align="center", valign="middle")
for i, r in enumerate([["결과물 평가", "교수가", "팀이 만든 결과물을 팀 단위로 평가합니다. 팀원 모두 같은 값입니다."],
                       ["팀 기여도", "팀원이", "팀원끼리 서로의 기여를 평가합니다. 똑같이 기여했으면 똑같이, 무임승차는 그만큼 깎입니다."]]):
    y = 4.0 + i * 1.2
    text(s, r[0], 7.2, y, 1.6, 0.5, size=14, bold=True, color=TEAL_DK if i == 0 else CORAL, valign="middle")
    text(s, r[1], 8.8, y, 0.8, 0.5, size=13, bold=True, color=GRAY, valign="middle")
    text(s, r[2], 7.2, y + 0.45, 5.1, 0.7, size=12.5)
text(s, "기여도 평가 방법과 제출 형식의 세부는 LearnUs 공지로 알립니다.", 7.2, 6.3, 5.1, 0.35, size=12, italic=True, color=GRAY)

# ───────────── 21. 약속 ─────────────
s = new_slide()
title_bar(s, "두 가지 약속", "AI 는 적극 쓰되, 설명할 수 있어야  ·  팀 점수에는 기여도가 곱해진다")
card(s, 0.72, 1.95, 5.75, 4.4, TINT)
badge(s, 1.05, 2.3, 0.55, TEAL, "AI", 13)
text(s, "AI 는 권장합니다. 조건은 하나", 1.75, 2.28, 4.6, 0.6, size=19, bold=True, color=TEAL_DK, valign="middle")
bullets(s, ["ChatGPT · Claude · Gemini 등 어떤 도구든 됩니다. 14주 1교시에 도구(챗봇 · AI API · VS Code · OpenClaw)를 소개합니다.",
            "팀원 누구든 그 코드가 무슨 일을 하는지 설명할 수 있어야 합니다.", "설명하지 못하는 코드는 검증자가 되돌려 보냅니다.",
            "AI 가 쓴 코드를 그대로 제출하는 것은 금지(수업계획서). 어디를 왜 고쳤는지 기록에 남기세요."], 1.05, 3.1, 5.1, 3.1, size=13.5, space=4)
card(s, 6.87, 1.95, 5.75, 4.4, TINT2)
badge(s, 7.2, 2.3, 0.55, CORAL, "팀", 13)
text(s, "기여도는 곱셈입니다", 7.9, 2.28, 4.6, 0.6, size=19, bold=True, color=CORAL, valign="middle")
bullets(s, ["결과물이 아무리 좋아도 기여도가 0 이면 개인 점수는 0 입니다.", "역할마다 발표 회차가 있으므로 누구나 한 번은 팀을 대표해 발표합니다 — 기여할 자리는 늘 있습니다.",
            "발표 뒤 다른 팀이 질문합니다. 답하는 것도, 묻는 것도 기여입니다."], 7.2, 3.1, 5.1, 3.1, size=13.5, space=4)

# ───────────── 22. 정리 ─────────────
s = new_slide()
title_bar(s, "2교시 정리", "다섯 줄로")
for i, p in enumerate([["남은 3주, 팀이 정한 문제를 AI 와 함께 푼다", "사람의 몫은 문제 정의와 검증 — 1교시 언어모델의 한계가 그 이유"],
                       ["뼈대는 여섯 단계", "불편 → 문제(입력 · 출력 · 범위) → 데이터 · 도구 → 만들기 → 검증 → 발표.  12주차 분류기와 교수의 팀 배정이 그 예"],
                       ["교수의 팀 배정 예에서 — 코드보다 기준 · 설문 · 검증에 시간이 들었다", "응답 23명을 알아챈 것도, 성별 조건을 뺀 것도 사람"],
                       ["7팀, 역할은 고정하고 발표 4회를 역할 순서대로", "오늘 역할과 문제, 목요일까지 팀명. 발표 자료는 회차마다 공용 Slides 파일에 — 전날 밤 마감"],
                       ["25점 = 과제물 15 + 수업 참여도 10", "개인 점수 = 결과물 평가(교수) × 팀 기여도(팀원).  AI 는 권장, 설명은 필수"]]):
    y = 1.95 + i * 0.92; odd = i % 2 == 1
    card(s, 0.72, y, 11.9, 0.8, TINT2 if odd else TINT)
    badge(s, 1.0, y + 0.15, 0.5, CORAL if odd else TEAL, str(i + 1), 14)
    text(s, p[0], 1.7, y, 5.3, 0.8, size=15, bold=True, valign="middle")
    text(s, p[1], 7.1, y, 5.3, 0.8, size=13.5, valign="middle")
text(s, "지금부터 — 팀원 인사 → 연락처 교환 → 역할 정하기 → 문제 정하기. 끝날 때 역할표와 문제 한 줄을 교수에게 보여 주세요.", 0.72, 6.65, 11.9, 0.4, size=14, italic=True, color=GRAY)

# 쪽번호
N = len(slides)
for i, s in enumerate(slides):
    text(s, f"{i + 1}/{N}", 12.2, 7.05, 0.9, 0.3, size=10, color=GRAY, align="right", name="쪽번호")

prs.save(OUT)
print("saved", OUT, N, "slides")

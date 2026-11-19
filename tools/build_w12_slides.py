# 컴퓨팅사고 12주차 1교시 — AI 프로젝트 개관 슬라이드 (python-pptx)
# 디자인은 컴퓨팅사고_1주차_260827_포맷참고.pptx 를 따른다: 흰 배경 · 맑은 고딕 · 청록 0EA5A4 / 산호 FF6B5A · 둥근 카드 · 쪽번호
import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

OUT, QR = sys.argv[1], sys.argv[2]
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


# ───────────── 1. 표지 ─────────────
s = new_slide()
shape(s, MSO_SHAPE.OVAL, 10.2, -2.4, 5.4, 5.4, TINT)
shape(s, MSO_SHAPE.OVAL, 11.6, 3.1, 3.6, 3.6, TINT2)
text(s, "컴퓨팅사고 · 12주차 · 1교시", 0.75, 1.55, 8, 0.4, size=16, color=GRAY)
text(s, "AI 프로젝트", 0.75, 2.05, 9, 1.3, size=54, bold=True)
text(s, [("내 불편을 AI 와 함께 푸는 프로젝트", {"color": TEAL_DK, "bold": True}), ("   ·   ", {"color": GRAY}),
         ("무엇을 · 누구와 · 어떻게", {"color": CORAL, "bold": True})], 0.75, 3.55, 10, 0.5, size=22)
text(s, "교양기초 (3학점)  ·  2026학년도 2학기  ·  연세대 미래캠퍼스", 0.75, 5.3, 10, 0.4, size=16)

# ───────────── 2. 지금까지와 앞으로 ─────────────
s = new_slide()
title_bar(s, "지금까지와 앞으로", "도구는 손에 들었습니다. 이제 쓰는 쪽을 바꿉니다")
y, h, w = 1.95, 4.5, 5.75
card(s, 0.72, y, w, h, LIGHT); card(s, 6.87, y, w, h, TINT)
text(s, "지금까지  (4 ~ 11주차)", 1.1, y + 0.35, 5, 0.5, size=20, bold=True, color=GRAY)
text(s, "앞으로  (12 ~ 15주차)", 7.25, y + 0.35, 5, 0.5, size=20, bold=True, color=TEAL_DK)
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
     "body": "어떤 문제를 풀 것인가 — 문제 정의.\n맞게 풀렸는가 — 검증.\n컴퓨팅 사고의 핵심(문제 정의 · 분해 · 입력과 출력)이 그대로 쓰입니다."},
    {"head": "문법을 배운 이유", "color": TEAL, "fill": TINT,
     "body": "AI 가 쓴 코드를 읽고, 고치고, 설명하기 위해서입니다.\n읽지 못하는 코드는 검증할 수 없습니다."},
], 2.0, 3.9)
text(s, "주도권은 여러분에게 — 교수는 팀을 짜 주고, 길을 잃을 때 묻는 사람입니다.", 0.72, 6.25, 11.9, 0.4, size=15, italic=True, color=GRAY)

# ───────────── 4. 섹션 01 ─────────────
section("01", "AI 응용 프로젝트의 뼈대", "여섯 단계  ·  오늘 수업과의 관계  ·  남은 일정")

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

# ───────────── 6. 축소판 ─────────────
s = new_slide()
title_bar(s, "오늘 2 · 3교시가 이 뼈대의 축소판", "뉴스 제목 분류기 — 여섯 단계를 한 번에 지나갑니다")
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
bullets(s, ["여섯 단계를 팀이 직접 밟습니다", "문제도, 데이터도, 도구도 팀이 고릅니다", "①② 에 시간을 가장 많이 씁니다"], 9.0, 2.9, 3.3, 3.3)

# ───────────── 7. 남은 일정 ─────────────
s = new_slide()
title_bar(s, "남은 일정", "수업계획서 기준 — 세부 날짜는 LearnUs 공지로")
weeks = [["12주", "오늘", "AI 프로젝트 개관\n인공지능 모델과 라이브러리", "팀 구성 설문", TEAL],
         ["13주", "", "언어모델이란 무엇인가\nAI 를 활용한 코딩과 디버깅", "팀 발표 · 문제 정의", TEAL],
         ["14주", "", "AI 를 활용하여 챗봇 만들기\nUI 설계 · 외부 API", "만들기 · 검증", TEAL],
         ["15주", "", "자율학습", "AI 응용 과제물 제출", CORAL],
         ["16주", "", "기말고사", "", GRAY]]
x0, gap = 0.72, 0.22; w = (11.9 - gap * 4) / 5; y = 2.0
for i, wk in enumerate(weeks):
    x = x0 + i * (w + gap); c = wk[4]
    badge(s, x + 0.05, y + 0.02, 0.56, c)
    text(s, wk[0], x + 0.7, y, 1.0, 0.6, size=20, bold=True, color=c, valign="middle")
    if wk[1]:
        text(s, wk[1], x + 1.75, y + 0.1, 0.6, 0.4, size=12, bold=True, color=WHITE, align="center", valign="middle", fill=CORAL)
    card(s, x, y + 0.85, w, 1.95, LIGHT)
    text(s, wk[2], x + 0.2, y + 1.05, w - 0.4, 1.6, size=14)
    if wk[3]:
        card(s, x, y + 3.0, w, 1.1, TINT2 if c == CORAL else TINT)
        text(s, wk[3], x + 0.2, y + 3.0, w - 0.4, 1.1, size=15, bold=True, color=CORAL if c == CORAL else TEAL_DK, valign="middle")
text(s, "회색 = 수업 내용,  색 = 프로젝트에서 할 일", 0.72, 6.45, 6, 0.35, size=12, color=GRAY)
card(s, 6.9, 6.3, 5.72, 0.75, AMBER_T)
text(s, "설문 마감 · 발표일 · 산출물 형식 · 평가 비율 · AI 도구 규칙은 LearnUs 공지로 알립니다", 7.1, 6.3, 5.4, 0.75, size=13, color=AMBER_DK, valign="middle")

# ───────────── 8. 섹션 02 ─────────────
section("02", "문제 정의", "불편에서 프로그램으로  ·  개인 → 공유 → 선택 → 정의")

# ───────────── 9. 4단계 ─────────────
s = new_slide()
title_bar(s, "팀에서 문제를 고르는 네 단계", "순서가 중요합니다 — 개인 먼저, 팀은 그 다음")
steps = [["개인", "각자 겪는 불편 3가지를 적는다\n(5 ~ 10분)", "대화 금지\n설문에 적은 것을 써도 됩니다"],
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

# ───────────── 10. 세 질문 ─────────────
s = new_slide()
title_bar(s, "다듬을 때 답할 세 질문", "세 질문에 답하지 못하면 아직 ‘문제’가 아닙니다")
three_cards(s, [
    {"head": "입력", "badge": "in", "color": TEAL, "fill": TINT, "body": "프로그램에 무엇을 넣는가?\n\n예) 듣고 싶은 과목 목록, 한 달 지출 내역, 팀원별 가능한 시간"},
    {"head": "출력", "badge": "out", "color": CORAL, "fill": TINT2, "body": "무엇이 나오면 불편이 해결된 것인가?\n\n예) 안 겹치는 시간표, 항목별 합계 그래프, 공통으로 비는 시간"},
    {"head": "범위", "badge": "≤", "color": TEAL, "fill": TINT, "body": "남은 수업 기간 안에 만들 수 있는 크기인가?\n\n‘계산이 끝나는가’까지 묻습니다. 과목 30개의 조합을 전부 따질 수 있나? 조건을 먼저 걸어 줄여야 하나?"},
], 2.0, 3.6)
card(s, 0.72, 5.9, 11.9, 0.85, AMBER_T)
text(s, "🤔  “불편” 말고 “궁금한 것”, “전공에서 반복되는 작업”까지 넓혀도 됩니다. 답이 안 나오는 불편은 다른 후보로 바꿉니다.", 0.95, 5.9, 11.5, 0.85, size=15, color=AMBER_DK, valign="middle")

# ───────────── 11. 예시 ─────────────
s = new_slide()
title_bar(s, "불편 → 문제, 이렇게 다듬는다", "적어낸 불편과 다듬은 문제의 예")
rows = [["시간표 짜기가 귀찮다", "과목 목록을 넣으면", "시간이 안 겹치는 조합"],
        ["용돈이 어디로 새는지 모르겠다", "지출 내역을 넣으면", "항목별 합계와 그래프"],
        ["조별과제 일정 잡기가 힘들다", "팀원별 가능한 시간을 넣으면", "공통으로 비는 시간"],
        ["25명을 조건에 맞게 8팀으로 나누기 어렵다", "설문 응답 파일을 넣으면", "조건을 만족하는 팀 배정표"]]
y0 = 2.0
text(s, "적어낸 불편", 0.72, y0, 4.3, 0.4, size=13, bold=True, color=GRAY)
text(s, "입력", 5.35, y0, 3.4, 0.4, size=13, bold=True, color=GRAY)
text(s, "출력", 9.3, y0, 3.3, 0.4, size=13, bold=True, color=GRAY)
for i, r in enumerate(rows):
    y = y0 + 0.5 + i * 0.95; last = i == len(rows) - 1
    card(s, 0.72, y, 4.3, 0.8, LIGHT); text(s, r[0], 0.95, y, 3.9, 0.8, size=15, valign="middle")
    text(s, "→", 5.02, y, 0.33, 0.8, size=18, color=CORAL, align="center", valign="middle")
    card(s, 5.35, y, 3.4, 0.8, TINT2 if last else TINT); text(s, r[1], 5.55, y, 3.05, 0.8, size=15, valign="middle")
    text(s, "→", 8.77, y, 0.5, 0.8, size=18, color=CORAL, align="center", valign="middle")
    card(s, 9.3, y, 3.32, 0.8, TINT2 if last else TINT); text(s, r[2], 9.5, y, 3.0, 0.8, size=15, bold=True, valign="middle")
text(s, "마지막 줄은 교수가 이번 팀 배정에 실제로 쓰는 프로그램입니다. 불편 → 입력 · 출력 → 코드로 가는 길을 교수도 똑같이 걸었습니다.", 0.72, 6.35, 11.9, 0.45, size=14, italic=True, color=GRAY)

# ───────────── 12. 활동 ─────────────
s = new_slide()
title_bar(s, "활동 — 내 불편 3가지를 입력 · 출력으로", "혼자서, 대화 없이  ·  약 6분")
card(s, 0.72, 1.95, 7.3, 4.6, WHITE, line=CORAL, line_w=2)
text(s, "✏️  적어 보세요", 1.05, 2.2, 6, 0.5, size=19, bold=True, color=CORAL)
for i in range(3):
    y = 2.9 + i * 1.15
    badge(s, 1.05, y + 0.05, 0.45, CORAL, str(i + 1), 13)
    text(s, "불편", 1.65, y, 0.7, 0.5, size=13, bold=True, color=GRAY, valign="middle")
    c = s.shapes.add_connector(1, Inches(2.35), Inches(y + 0.45), Inches(7.75), Inches(y + 0.45)); c.line.color.rgb = rgb(LINE); c.line.width = Pt(1)
    text(s, "입력", 1.65, y + 0.55, 0.7, 0.45, size=13, bold=True, color=GRAY, valign="middle")
    c = s.shapes.add_connector(1, Inches(2.35), Inches(y + 0.95), Inches(4.75), Inches(y + 0.95)); c.line.color.rgb = rgb(LINE); c.line.width = Pt(1)
    text(s, "출력", 4.95, y + 0.55, 0.7, 0.45, size=13, bold=True, color=GRAY, valign="middle")
    c = s.shapes.add_connector(1, Inches(5.65), Inches(y + 0.95), Inches(7.75), Inches(y + 0.95)); c.line.color.rgb = rgb(LINE); c.line.width = Pt(1)
card(s, 8.35, 1.95, 4.27, 4.6, TINT)
text(s, "요령", 8.7, 2.2, 3.5, 0.5, size=19, bold=True, color=TEAL_DK)
bullets(s, ["완벽하지 않아도 됩니다.\n떠오르는 대로 적으세요.",
            "입력 · 출력이 안 떠오르면\n‘아직 문제가 아니다’라는 뜻입니다.",
            "잠시 뒤 설문의 ‘불편 3가지’ 칸에\n그대로 쓰면 됩니다.",
            "팀 첫 모임의 ‘개인 단계’ 재료입니다."], 8.7, 2.85, 3.7, 3.5)

# ───────────── 13. 섹션 03 ─────────────
section("03", "팀", "구성 원칙  ·  매주 바뀌는 역할  ·  팀 규칙")

# ───────────── 14. 팀 구성 ─────────────
s = new_slide()
title_bar(s, "팀은 교수가 배정합니다", "주제는 팀이 고르고, 팀 구성만 교수가 정합니다")
card(s, 0.72, 1.95, 4.6, 4.6, TINT2)
text(s, "왜 자율 구성이 아닌가", 1.05, 2.2, 4, 0.5, size=19, bold=True, color=CORAL)
bullets(s, ["친한 사람끼리 모이면 실력이 한쪽으로 몰립니다", "한 사람이 다 하고 나머지는 구경하게 되기 쉽습니다", "다른 계열의 눈이 섞여야 불편도 해법도 다양해집니다"], 1.05, 2.85, 3.95, 2.3)
text(s, "인원", 1.05, 5.25, 1, 0.4, size=13, bold=True, color=GRAY)
text(s, [("3명", {"bold": True, "color": CORAL, "size": 28}), ("  기본  ·  남는 인원만 4명 팀", {"size": 15})], 1.05, 5.6, 4, 0.6, valign="middle")
card(s, 5.65, 1.95, 6.97, 4.6, TINT)
text(s, "배정 기준 — 중요한 순서", 6.0, 2.2, 6, 0.5, size=19, bold=True, color=TEAL_DK)
for i, c in enumerate([["계열", "팀 전원이 같은 계열이 되지 않게"], ["관심 주제", "팀원끼리 관심 주제가 겹치게"],
                       ["코딩 자신감", "평균이 팀마다 비슷하게"], ["AI 사용 경험", "팀마다 비슷하게"]]):
    y = 2.9 + i * 0.85
    badge(s, 6.0, y + 0.08, 0.45, TEAL, str(i + 1), 13)
    text(s, c[0], 6.6, y, 2.0, 0.6, size=16, bold=True, valign="middle")
    text(s, c[1], 8.6, y, 3.8, 0.6, size=15, valign="middle")
text(s, "이 기준의 재료가 잠시 뒤 할 설문입니다.", 6.0, 6.05, 6.3, 0.4, size=14, italic=True, color=GRAY)

# ───────────── 15. 역할 ─────────────
s = new_slide()
title_bar(s, "역할은 매주 바뀝니다", "한 사람이 코딩을 다 하는 팀은 그 사람만 배웁니다")
roles = [["문제 정의자", "누구의 어떤 불편인지, 입력 · 출력을 정리한다"], ["프롬프터", "AI 에게 요구사항을 전달하고 코드를 받아 온다"],
         ["검증자", "받은 코드를 여러 입력으로 돌려 보고 AI 의 오류를 찾는다"], ["기록 · 발표자", "과정과 시행착오를 기록하고 발표를 준비한다  (4명 팀)"]]
x0, gap = 0.72, 0.26; w = (11.9 - gap * 3) / 4; y, h = 2.0, 2.6
for i, r in enumerate(roles):
    x = x0 + i * (w + gap); g = i == 3
    card(s, x, y, w, h, LIGHT if g else TINT)
    badge(s, x + (w - 0.6) / 2, y + 0.3, 0.6, GRAY if g else TEAL)
    text(s, r[0], x + 0.15, y + 1.0, w - 0.3, 0.5, size=18, bold=True, color=GRAY if g else TEAL_DK, align="center", valign="middle")
    text(s, r[1], x + 0.3, y + 1.55, w - 0.6, 1.0, size=14, align="center")
    if i < 3:
        shape(s, MSO_SHAPE.RIGHT_ARROW, x + w - 0.05, y + 0.2, 0.36, 0.3, CORAL)
card(s, 0.72, 4.9, 11.9, 1.75, TINT2)
text(s, "팀이 첫 모임에서 할 세 가지", 1.05, 5.05, 6, 0.45, size=18, bold=True, color=CORAL)
text(s, [("①  팀 규칙 한 장", {"bold": True}), (" — 연락 방법 · 역할 순서 · 불참 시 처리를 팀이 직접 정해 제출\n", {}),
         ("②  문제 정의 네 단계", {"bold": True}), ("를 밟아 후보 하나를 고름\n", {}),
         ("③  다른 팀의 질문에 답할 준비", {"bold": True}), (" — “그게 정말 문제인가?”  “데이터는 어디서 구하나?”", {})], 1.05, 5.55, 11.3, 1.0, size=15)

# ───────────── 16. 약속 ─────────────
s = new_slide()
title_bar(s, "두 가지 약속", "AI 는 적극 쓰되, 설명할 수 있어야  ·  팀 점수에는 동료 평가")
card(s, 0.72, 1.95, 5.75, 4.4, TINT)
badge(s, 1.05, 2.3, 0.55, TEAL, "AI", 13)
text(s, "AI 는 권장합니다. 조건은 하나", 1.75, 2.28, 4.6, 0.6, size=19, bold=True, color=TEAL_DK, valign="middle")
bullets(s, ["프롬프터 역할이 있는 것처럼, AI 로 코드를 만드는 것은 권장입니다.", "팀원 누구든 그 코드가 무슨 일을 하는지 설명할 수 있어야 합니다.",
            "설명하지 못하는 코드는 검증자가 되돌려 보냅니다.", "쓸 AI 도구와 세부 규칙은 13주차에 안내합니다."], 1.05, 3.1, 5.1, 3.1)
card(s, 6.87, 1.95, 5.75, 4.4, TINT2)
badge(s, 7.2, 2.3, 0.55, CORAL, "팀", 13)
text(s, "팀 점수 + 동료 평가", 7.9, 2.28, 4.6, 0.6, size=19, bold=True, color=CORAL, valign="middle")
bullets(s, ["프로젝트 점수는 팀 점수에 개인 기여도(동료 평가)를 반영합니다.", "역할이 매주 바뀌므로 누구나 한 번씩 프롬프터와 검증자를 맡게 됩니다.",
            "비율과 방법은 LearnUs 공지로 알립니다."], 7.2, 3.1, 5.1, 3.1)

# ───────────── 17. 섹션 04 ─────────────
section("04", "팀 구성 설문", "지금 바로  ·  약 7분")

# ───────────── 18. 설문 ─────────────
s = new_slide()
title_bar(s, "팀 구성 설문 — 지금 바로", "휴대폰으로 QR 을 찍거나 링크를 열어 응답해 주세요  ·  문항 7개, 3분")
card(s, 0.72, 1.95, 4.9, 4.75, TINT)
text(s, "참여 방법", 1.05, 2.2, 4, 0.5, size=19, bold=True, color=TEAL_DK)
if os.path.exists(QR):
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 1.55, 2.8, 3.25, 3.25, WHITE, radius=0.06)
    pic = s.shapes.add_picture(QR, Inches(1.7), Inches(2.95), Inches(2.95), Inches(2.95)); pic.name = "설문 QR 코드"
text(s, "AI 프로젝트 팀 구성을 위한 설문 (Google Forms)", 1.05, 6.15, 4.3, 0.4, size=12, color=GRAY, align="center")
card(s, 5.95, 1.95, 6.67, 4.75, LIGHT)
text(s, "문항", 6.3, 2.2, 4, 0.5, size=19, bold=True)
for i, r in enumerate([["학번 · 이름", "학번은 숫자만. 같은 학번은 마지막 응답만 반영"],
                       ["계열", "인문 / 사회 · 경영 / 이공 / 보건의료.  전공 미정이면 앞으로 신청할 제1전공 기준"],
                       ["코딩 자신감", "1(혼자서는 어렵다) ~ 5(혼자서 짤 수 있다).  솔직하게"],
                       ["AI 사용 경험", "거의 안 씀 / 가끔 씀 / 매일 씀"],
                       ["관심 주제", "학교생활 · 돈과 소비 · 건강과 운동 · 취미와 여가 · 전공 공부 · 사회와 환경 중 정확히 2개"],
                       ["불편 3가지", "방금 적은 것을 그대로.  배정에는 쓰지 않고 팀 논의의 재료"]]):
    y = 2.8 + i * 0.63
    text(s, r[0], 6.3, y, 1.6, 0.58, size=14, bold=True, color=TEAL_DK, valign="middle")
    text(s, r[1], 7.95, y, 4.5, 0.58, size=13, valign="middle")

# ───────────── 19. 주의 ─────────────
s = new_slide()
title_bar(s, "설문 응답은 팀 배정에만 씁니다", "안심하고 솔직하게")
three_cards(s, [
    {"head": "비공개 · 성적 무관", "badge": "🔒", "color": TEAL, "fill": TINT, "body": "코딩 자신감 점수는 공개하지 않습니다.\n성적과 무관합니다.\n낮게 적어도 불이익이 없습니다."},
    {"head": "고치려면 다시 제출", "badge": "↻", "color": CORAL, "fill": TINT2, "body": "응답 수정 대신 다시 제출하면 됩니다.\n같은 학번은 마지막 응답만 반영됩니다."},
    {"head": "마감은 LearnUs 공지", "badge": "⏰", "color": TEAL, "fill": TINT, "body": "마감 시각은 LearnUs 공지에 있습니다.\n마감 뒤 응답하지 않은 사람에게는 개별로 연락합니다.\n응답이 모두 모여야 팀을 짤 수 있습니다."},
], 2.0, 3.7)
card(s, 0.72, 6.0, 11.9, 0.8, LIGHT)
text(s, "📎  팀 배정도 프로그램입니다 — 응답 CSV 를 읽어 무작위로 나눈 뒤, 두 사람을 맞바꿔 기준 점수가 나아지면 바꾸는 일을 수백 번 반복합니다 (10주차의 탐색).", 0.95, 6.0, 11.5, 0.8, size=13, color=GRAY, valign="middle")

# ───────────── 20. 정리 ─────────────
s = new_slide()
title_bar(s, "1교시 정리", "다섯 줄로")
for i, p in enumerate([["남은 수업은 팀이 스스로 정한 문제를 AI 와 함께 푸는 프로젝트", "사람의 몫은 문제 정의와 검증"],
                       ["AI 응용의 뼈대는 여섯 단계", "불편 → 문제(입력 · 출력 · 범위) → 데이터 · 도구 → 만들기 → 검증 → 발표.  오늘 2 · 3교시가 축소판"],
                       ["문제 정의는 개인 → 공유 → 선택 → 정의", "세 질문에 답하지 못하면 아직 문제가 아니다"],
                       ["팀은 교수가 배정 — 계열은 다르게, 관심은 겹치게", "역할은 매주 바뀌고, 팀 점수에 동료 평가 반영"],
                       ["설문에 지금 응답", "마감과 세부 일정은 LearnUs 공지"]]):
    y = 1.95 + i * 0.92; odd = i % 2 == 1
    card(s, 0.72, y, 11.9, 0.8, TINT2 if odd else TINT)
    badge(s, 1.0, y + 0.15, 0.5, CORAL if odd else TEAL, str(i + 1), 14)
    text(s, p[0], 1.7, y, 5.3, 0.8, size=16, bold=True, valign="middle")
    text(s, p[1], 7.1, y, 5.3, 0.8, size=14, valign="middle")
text(s, "다음: 2교시 — 인공지능 모델이란 (수업 사이트 노트북)", 0.72, 6.65, 11.9, 0.4, size=14, italic=True, color=GRAY)

# 쪽번호
N = len(slides)
for i, s in enumerate(slides):
    text(s, f"{i + 1}/{N}", 12.2, 7.05, 0.9, 0.3, size=10, color=GRAY, align="right", name="쪽번호")

prs.save(OUT)
print("saved", OUT, N, "slides")

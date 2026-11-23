# 컴퓨팅사고 13주차 1교시 — 언어모델(LM)이란 무엇이며 어떻게 쓰이고 있나 (python-pptx)
# build_w12_slides.py 를 복제해 작성. 사용: python tools/build_w13_slides.py <출력.pptx>
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


def line(s, x1, y1, x2, y2, color=CORAL, width=2.5):
    c = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = rgb(color); c.line.width = Pt(width)
    return c


# ───────────── 1. 표지 ─────────────
s = new_slide()
shape(s, MSO_SHAPE.OVAL, 10.2, -2.4, 5.4, 5.4, TINT)
shape(s, MSO_SHAPE.OVAL, 11.6, 3.1, 3.6, 3.6, TINT2)
text(s, "컴퓨팅사고 · 13주차 · 1교시", 0.75, 1.55, 8, 0.4, size=16, color=GRAY)
text(s, "언어모델이란 무엇인가", 0.75, 2.05, 10, 1.3, size=54, bold=True)
text(s, [("다음 단어 맞히기에서 챗봇까지", {"color": TEAL_DK, "bold": True}), ("   ·   ", {"color": GRAY}),
         ("지금 어디에 어떻게 쓰이고 있나", {"color": CORAL, "bold": True})], 0.75, 3.55, 11, 0.5, size=22)
text(s, "교양기초 (3학점)  ·  2026학년도 2학기  ·  연세대 미래캠퍼스", 0.75, 5.3, 10, 0.4, size=16)

# ───────────── 2. 오늘의 흐름 ─────────────
s = new_slide()
title_bar(s, "오늘의 흐름", "13주차 — 언어모델과 AI 프로젝트 시작. 오늘은 1 · 2교시, 목요일 3교시")
three_cards(s, [
    {"head": "언어모델이란", "badge": "1", "color": TEAL, "fill": TINT,
     "body": "다음 단어를 맞히는 프로그램이 어떻게 글을 쓰고 대화를 하게 되었나.\n지금 어디에 어떻게 쓰이고, 무엇을 못 하나.\n\n슬라이드 수업 · 짧은 활동 하나"},
    {"head": "AI 프로젝트 오리엔테이션", "badge": "2", "color": CORAL, "fill": TINT2,
     "body": "팀끼리 모여 앉습니다. 개요 · 일정 · 역할 · 평가(교수 15분) 뒤 팀원 인사 → 역할 정하기 → 문제 정하기.\n\n슬라이드 + 팀 활동"},
    {"head": "1회차 발표 (목요일 3교시)", "badge": "3", "color": TEAL, "fill": TINT,
     "body": "팀명 · 팀 규칙 한 장 · 문제 정의 마무리.\n팀마다 발표 3분 + 질문 2분 — 누구의 불편, 입력 · 출력 · 범위.\n\n발표자: 문제 정의자. 자료는 수요일 밤까지 공용 Slides 파일에"},
], 2.0, 3.9)
text(s, "1교시는 ‘무엇인가’, 2교시는 ‘어떻게 진행하나’와 ‘우리 문제 정하기’, 목요일은 ‘발표’ 입니다.", 0.72, 6.25, 11.9, 0.4, size=15, italic=True, color=GRAY)

# ───────────── 3. 활동 — 다음 단어 맞히기 ─────────────
s = new_slide()
title_bar(s, "활동 — 다음에 올 말은?", "빈칸에 들어갈 말을 하나씩 외쳐 보세요  ·  약 3분")
qs = [("연세대학교 미래캠퍼스는 강원도", "____ 에 있다"),
      ("오늘 점심은 학생식당에서", "____"),
      ("파이썬에서 리스트의 길이를 구하는 함수는", "____ 이다"),
      ("12주차에 만든 뉴스 제목 분류기는 스포츠 · 경제 · 날씨 ·", "____ 네 주제를 나눴다")]
for i, (a, b) in enumerate(qs):
    y = 2.0 + i * 0.9
    card(s, 0.72, y, 11.9, 0.75, TINT2 if i % 2 else TINT)
    badge(s, 1.0, y + 0.13, 0.5, CORAL if i % 2 else TEAL, str(i + 1), 14)
    text(s, [(a + " ", {}), (b, {"bold": True, "color": CORAL})], 1.7, y, 10.6, 0.75, size=18, valign="middle")
card(s, 0.72, 5.75, 11.9, 1.05, AMBER_T)
text(s, [("🤔  답이 하나로 정해진 문장도 있고, 여러 답이 가능한 문장도 있습니다. ", {"bold": True, "color": AMBER_DK}),
         ("1번은 거의 한 가지, 2번은 수십 가지. 여러분 머릿속에서도 ‘그럴 법한 정도’가 다릅니다. 이 ‘그럴 법한 정도’를 숫자로 매기는 것이 오늘 이야기의 전부입니다.", {"color": AMBER_DK})],
     0.95, 5.75, 11.5, 1.05, size=15, valign="middle")

# ───────────── 4. 섹션 01 ─────────────
section("01", "언어모델이란 무엇인가", "다음 토큰의 확률  ·  12주차와의 연결  ·  글이 되는 과정  ·  커지면 생기는 일")

# ───────────── 5. 정의 한 줄 ─────────────
s = new_slide()
title_bar(s, "언어모델 = 다음에 올 조각의 확률을 매기는 프로그램", "언어모델(language model, LM) — 정의는 이 한 줄이 전부입니다")
card(s, 0.72, 1.95, 6.6, 4.6, TINT)
text(s, "입력", 1.05, 2.2, 1.5, 0.4, size=13, bold=True, color=GRAY)
mono(s, "오늘 점심은 학생식당에서", 1.05, 2.55, 5.9, 0.6, size=16)
text(s, "출력 — 다음 조각마다 확률", 1.05, 3.35, 4, 0.4, size=13, bold=True, color=GRAY)
probs = [("먹었다", 0.31), ("김치찌개", 0.12), ("라면", 0.09), ("친구와", 0.07), ("…", None), ("미분방정식", 0.0001)]
for i, (w_, p) in enumerate(probs):
    y = 3.75 + i * 0.45
    text(s, w_, 1.05, y, 1.9, 0.4, size=15, bold=True, valign="middle", color=GRAY if p is None else DARK)
    if p is not None:
        bw = max(0.06, 3.3 * p / 0.31)
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 3.0, y + 0.08, bw, 0.26, CORAL if i == 0 else TEAL, radius=0.4)
        text(s, f"{p:.0%}" if p >= 0.01 else "0.01%", 3.1 + bw, y, 1.4, 0.4, size=13, color=GRAY, valign="middle")
card(s, 7.65, 1.95, 4.97, 4.6, TINT2)
text(s, "이미 매일 쓰고 있습니다", 8.0, 2.2, 4.3, 0.5, size=19, bold=True, color=CORAL)
bullets(s, ["휴대폰 자판 위에 뜨는 추천 단어 — 가장 작은 언어모델",
            "검색창의 자동완성",
            "맞춤법 검사기, 번역기",
            "ChatGPT · Claude · Gemini — 같은 일을 아주 크게 하는 것"], 8.0, 2.85, 4.3, 2.6)
text(s, "‘모델’은 12주차의 뜻 그대로입니다. 안에 숫자(매개변수)가 들어 있고, 데이터로 그 숫자를 정했습니다.", 8.0, 5.55, 4.3, 0.9, size=13, italic=True, color=GRAY)

# ───────────── 6. 12주차와 연결 ─────────────
s = new_slide()
title_bar(s, "12주차 분류기와 무엇이 같고 무엇이 다른가", "재료는 같습니다 — 토큰 · 번호의 열 · 손실을 줄이는 반복")
rows = [["입력", "제목 한 줄 → 번호의 열", "앞에 온 글 → 번호의 열", False],
        ["출력", "주제 4개 중 하나", "어휘 전체(수만 개) 중 다음 하나", False],
        ["정답", "사람이 붙인 라벨 160건", "글 자체가 정답 — 다음 단어가 정답지", True],
        ["데이터", "뉴스 제목 160건", "인터넷 글 · 책 · 코드 수조 토큰", True],
        ["모델", "RNN, 매개변수 약 2만 개", "트랜스포머, 수천억 개", False],
        ["학습", "손실이 줄도록 반복 (20 에포크, 몇 초)", "같은 반복 — GPU 수만 대로 몇 달", False]]
y0 = 1.95
text(s, "12주차 뉴스 분류기", 2.1, y0, 5, 0.4, size=14, bold=True, color=GRAY)
text(s, "언어모델", 7.5, y0, 5, 0.4, size=14, bold=True, color=TEAL_DK)
for i, r in enumerate(rows):
    y = y0 + 0.45 + i * 0.6
    text(s, r[0], 0.72, y, 1.3, 0.52, size=14, bold=True, color=GRAY, valign="middle")
    card(s, 2.1, y, 5.1, 0.52, LIGHT); text(s, r[1], 2.3, y, 4.8, 0.52, size=14, valign="middle")
    card(s, 7.5, y, 5.12, 0.52, TINT2 if r[3] else TINT); text(s, r[2], 7.7, y, 4.8, 0.52, size=14, bold=r[3], color=CORAL if r[3] else DARK, valign="middle")
card(s, 0.72, 6.05, 11.9, 0.8, AMBER_T)
text(s, "🔑  정답 라벨을 사람이 붙일 필요가 없다 — 이것이 열쇠입니다. 세상의 모든 글이 그대로 문제집이자 정답지라서, 데이터를 사람 손 없이 수조 토큰까지 늘릴 수 있었습니다.", 0.95, 6.05, 11.5, 0.8, size=14, color=AMBER_DK, valign="middle")

# ───────────── 7. 생성 루프 ─────────────
s = new_slide()
title_bar(s, "다음 조각 하나가 어떻게 긴 글이 되나", "한 조각 고르고, 붙이고, 다시 — 끝 표시가 나올 때까지")
bx, by = 0.72, 2.0
card(s, bx, by, 3.0, 1.0, LIGHT); text(s, "앞에 온 글\n(질문 + 지금까지 쓴 답)", bx, by, 3.0, 1.0, size=14, bold=True, align="center", valign="middle")
arrow_right(s, bx + 3.1, by + 0.35)
card(s, bx + 3.6, by, 2.2, 1.0, TEAL); text(s, "언어모델", bx + 3.6, by, 2.2, 1.0, size=18, bold=True, color=WHITE, align="center", valign="middle")
arrow_right(s, bx + 5.9, by + 0.35)
card(s, bx + 6.4, by, 2.6, 1.0, TINT); text(s, "다음 조각마다 확률\n먹었다 31% · 라면 9% …", bx + 6.4, by, 2.6, 1.0, size=13, align="center", valign="middle")
arrow_right(s, bx + 9.1, by + 0.35)
card(s, bx + 9.6, by, 2.3, 1.0, TINT2); text(s, "하나 고른다\n(주사위를 던져서)", bx + 9.6, by, 2.3, 1.0, size=14, bold=True, color=CORAL, align="center", valign="middle")
line(s, bx + 10.75, by + 1.0, bx + 10.75, by + 1.55)
line(s, bx + 10.75, by + 1.55, bx + 1.5, by + 1.55)
line(s, bx + 1.5, by + 1.55, bx + 1.5, by + 1.05)
shape(s, MSO_SHAPE.UP_ARROW, bx + 1.37, by + 1.0, 0.26, 0.22, CORAL)
text(s, "고른 조각을 글 끝에 붙이고 처음으로 — ‘끝’ 조각이 나올 때까지 반복", bx + 2.2, by + 1.62, 8, 0.4, size=14, bold=True, color=CORAL)
card(s, 0.72, 4.25, 7.3, 2.45, TINT)
text(s, "예 — 한 바퀴에 한 조각", 1.05, 4.45, 5, 0.4, size=16, bold=True, color=TEAL_DK)
mono(s, "오늘 점심은 학생식당에서\n오늘 점심은 학생식당에서 김치찌개\n오늘 점심은 학생식당에서 김치찌개 를\n오늘 점심은 학생식당에서 김치찌개 를 먹었다\n오늘 점심은 학생식당에서 김치찌개 를 먹었다 .  <끝>", 1.05, 4.95, 6.7, 1.6, size=13)
card(s, 8.35, 4.25, 4.27, 2.45, TINT2)
text(s, "그래서 생기는 일", 8.7, 4.45, 3.5, 0.4, size=16, bold=True, color=CORAL)
bullets(s, ["같은 질문에 답이 매번 조금 다릅니다 — 고를 때 주사위를 던지니까", "긴 답은 오래 걸립니다 — 조각 수만큼 모델을 돌립니다", "답이 한 글자씩 나타나는 화면은 이 반복을 그대로 보여 주는 것"], 8.7, 4.95, 3.7, 1.7, size=13, space=4)

# ───────────── 8. 토큰 ─────────────
s = new_slide()
title_bar(s, "조각 = 토큰", "글자도 단어도 아닌, 자주 함께 나오는 글자 묶음")
card(s, 0.72, 1.95, 6.9, 4.75, TINT)
text(s, "언어모델이 보는 글", 1.05, 2.2, 5, 0.45, size=19, bold=True, color=TEAL_DK)
toks = [("컴퓨", TEAL), ("팅", CORAL), ("사고", TEAL), ("는", CORAL), ("언어", TEAL), ("모델", CORAL), ("을", TEAL), ("배운다", CORAL)]
x = 1.05
for t_, c_ in toks:
    w_ = 0.27 * len(t_) + 0.24
    card(s, x, 2.85, w_, 0.55, WHITE, line=c_, line_w=1.5)
    text(s, t_, x, 2.85, w_, 0.55, size=14, bold=True, color=c_, align="center", valign="middle")
    x += w_ + 0.07
text(s, "(토큰으로 나뉘는 모양의 예 — 실제 경계는 모델마다 다릅니다)", 1.05, 3.5, 6.3, 0.35, size=12, italic=True, color=GRAY)
bullets(s, ["단어가 아니라 ‘자주 같이 나오는 글자 묶음’으로 나눕니다. 흔한 말은 한 토큰, 드문 말은 여러 토큰.",
            "12주차 <unk> 문제가 사라집니다 — 처음 보는 단어도 아는 조각들로 쪼개지니 ‘모르는 단어’가 없습니다.",
            "모델에는 조각 번호의 열이 들어갑니다 — 12주차 encode() 와 같은 일을 토큰 단위로 합니다."], 1.05, 4.0, 6.3, 2.6, size=14)
card(s, 7.95, 1.95, 4.67, 4.75, TINT2)
text(s, "한국어는 토큰을 더 씁니다", 8.3, 2.2, 4.1, 0.45, size=19, bold=True, color=CORAL)
for i, (lang, n) in enumerate([("영어 한 단어", "약 1 ~ 1.3 토큰"), ("한글 한 글자", "약 1 ~ 2 토큰")]):
    y = 2.85 + i * 0.7
    text(s, lang, 8.3, y, 1.8, 0.55, size=14, bold=True, valign="middle")
    card(s, 10.1, y, 2.3, 0.55, WHITE); text(s, n, 10.1, y, 2.3, 0.55, size=14, bold=True, color=CORAL, align="center", valign="middle")
bullets(s, ["같은 내용을 한국어로 쓰면 토큰이 더 들어 느리고 비쌉니다 (요금은 토큰 수로 매깁니다).",
            "한 번에 넣을 수 있는 길이(문맥 창)도 토큰 수로 정해집니다.",
            "14주차에 챗봇을 만들 때 이 숫자를 다시 봅니다."], 8.3, 4.35, 4.1, 2.3, size=13, space=4)

# ───────────── 9. 트랜스포머 ─────────────
s = new_slide()
title_bar(s, "RNN 에서 트랜스포머로", "앞 글 전체를 한꺼번에 돌아본다 — GPT 의 T")
card(s, 0.72, 1.95, 5.75, 3.6, LIGHT)
text(s, "RNN  (12주차)", 1.05, 2.2, 4, 0.5, size=19, bold=True, color=GRAY)
for i, t_ in enumerate(["손흥민", "두", "골", "폭발"]):
    x = 1.05 + i * 1.2
    card(s, x, 2.9, 0.95, 0.5, WHITE, line=GRAY); text(s, t_, x, 2.9, 0.95, 0.5, size=13, align="center", valign="middle")
    if i < 3: arrow_right(s, x + 1.0, 3.0, 0.17, 0.3, GRAY)
text(s, "메모 하나를 들고 한 단어씩 — 긴 글이면 앞부분이 흐려집니다", 1.05, 3.6, 5.1, 0.5, size=13, color=GRAY)
bullets(s, ["단어를 순서대로 처리해야 해서 한 번에 한 단어", "그래서 크게 키우기 어려웠습니다"], 1.05, 4.2, 5.1, 1.2, size=14, space=4)
card(s, 6.87, 1.95, 5.75, 3.6, TINT)
text(s, "트랜스포머  (transformer)", 7.2, 2.2, 5, 0.5, size=19, bold=True, color=TEAL_DK)
last_x = 7.2 + 3 * 1.2 + 0.47
for i in range(3):
    x = 7.2 + i * 1.2
    line(s, x + 0.47, 2.9, last_x, 2.62, TEAL, 1.5)
shape(s, MSO_SHAPE.DOWN_ARROW, last_x - 0.11, 2.62, 0.22, 0.26, TEAL)
for i, t_ in enumerate(["손흥민", "두", "골", "폭발"]):
    x = 7.2 + i * 1.2
    card(s, x, 2.9, 0.95, 0.5, WHITE, line=TEAL if i == 3 else LINE); text(s, t_, x, 2.9, 0.95, 0.5, size=13, bold=i == 3, align="center", valign="middle")
text(s, "각 단어가 앞 글 전체를 돌아보며 관련 있는 단어에 집중(어텐션)합니다", 7.2, 3.6, 5.1, 0.5, size=13, color=TEAL_DK)
bullets(s, ["순서대로 기다릴 필요가 없어 한꺼번에 계산 → GPU 에 딱 맞음", "2017년에 나왔고, 이후 수천억 개까지 커졌습니다"], 7.2, 4.2, 5.1, 1.2, size=14, space=4)
card(s, 0.72, 5.8, 11.9, 0.95, AMBER_T)
text(s, "📎  안에서 무슨 계산을 하는지는 이 수업 범위 밖입니다. 기억할 것은 하나 — 트랜스포머는 ‘앞 글 전체를 동시에 참고하는, 크게 키울 수 있는 모델’. ChatGPT 의 GPT 는 Generative Pre-trained Transformer 입니다.", 0.95, 5.8, 11.5, 0.95, size=13, color=AMBER_DK, valign="middle")

# ───────────── 10. 규모 ─────────────
s = new_slide()
title_bar(s, "작은 언어모델에서 거대언어모델(LLM)로", "방법은 그대로, 세 가지 숫자만 커졌습니다")
three_cards(s, [
    {"head": "매개변수", "badge": "①", "color": TEAL, "fill": TINT, "body": "12주차 RNN  약 2만 개\n→ 수천억 개 이상\n\n모델 안의 숫자가 그만큼 많습니다. 파일 크기로 수백 GB."},
    {"head": "데이터", "badge": "②", "color": CORAL, "fill": TINT2, "body": "뉴스 제목 160건\n→ 수조 토큰\n\n인터넷 글 · 책 · 위키 · 코드. 사람이 평생 읽는 양의 수만 배."},
    {"head": "계산", "badge": "③", "color": TEAL, "fill": TINT, "body": "브라우저에서 몇 초\n→ GPU 수만 대로 몇 달\n\n전기 요금만 수백억 원. 그래서 만드는 회사가 몇 안 됩니다."},
], 2.0, 3.3)
card(s, 0.72, 5.55, 11.9, 1.2, TINT)
text(s, [("🔑  놀라운 점 — ", {"bold": True, "color": TEAL_DK}),
         ("‘다음 토큰 맞히기’만 시켰는데, 크기를 키우자 가르치지 않은 일을 합니다. 번역 · 요약 · 코드 작성 · 수학 문제. 다음 토큰을 잘 맞히려면 결국 문법 · 사실 · 논리를 어느 정도 ‘알아야’ 하기 때문이라고 설명합니다. 거대언어모델(large language model, LLM)이라는 이름은 여기서 왔습니다.", {})],
     0.95, 5.55, 11.5, 1.2, size=14, valign="middle")

# ───────────── 11. 대화가 되기까지 ─────────────
s = new_slide()
title_bar(s, "이어 쓰기 기계가 어떻게 ‘대화’를 하게 되나", "사전학습 → 지시 학습 → 선호 학습, 세 단계")
steps = [["사전학습", "pre-training", "인터넷 글 수조 토큰으로 다음 토큰 맞히기.\n결과: 글을 잘 잇는 기계.", "“한국의 수도는?” 하고 물으면\n“일본의 수도는? 중국의 수도는?” 하고\n비슷한 질문을 이어 씁니다.", TEAL],
         ["지시 학습", "instruction tuning", "‘질문 → 좋은 답’ 예시 수만 개를 사람이 써서 추가 학습.\n결과: 질문에 답하는 기계.", "“한국의 수도는?” → “서울입니다.”\n질문이 오면 답을 잇는다는 것을 배웁니다.", CORAL],
         ["선호 학습", "RLHF", "답 두 개를 보여 주고 사람이 고른 쪽을 더 내도록 조정.\n결과: 친절하고 안전한 기계.", "거짓말 · 무례함 · 위험한 답을 덜 하고,\n모르면 모른다고 하도록.", TEAL]]
x0, gap = 0.72, 0.26; w = (11.9 - gap * 2) / 3; y, h = 2.0, 3.95
for i, st in enumerate(steps):
    x = x0 + i * (w + gap); c = st[4]
    card(s, x, y, w, h, TINT2 if c == CORAL else TINT)
    badge(s, x + 0.3, y + 0.32, 0.5, c, str(i + 1), 14)
    text(s, [(st[0], {"bold": True, "size": 19, "color": TEAL_DK if c == TEAL else CORAL}), ("  " + st[1], {"size": 12, "color": GRAY})], x + 0.95, y + 0.3, w - 1.1, 0.54, valign="middle")
    text(s, st[2], x + 0.32, y + 1.05, w - 0.64, 1.35, size=14)
    text(s, "예", x + 0.32, y + 2.45, 1, 0.3, size=12, bold=True, color=GRAY)
    text(s, st[3], x + 0.32, y + 2.75, w - 0.64, 1.15, size=13, italic=True)
    if i < 2: arrow_right(s, x + w - 0.02, y + 0.42, 0.3, 0.3)
card(s, 0.72, 6.15, 11.9, 0.65, LIGHT)
text(s, "ChatGPT · Claude · Gemini  =  언어모델  +  이 세 단계의 훈련  +  채팅 화면.  밑바탕은 여전히 ‘다음 토큰의 확률’ 입니다.", 0.95, 6.15, 11.5, 0.65, size=14, bold=True, valign="middle")

# ───────────── 12. 섹션 02 ─────────────
section("02", "지금 어떻게 쓰이고 있나", "활용 지도  ·  세 가지 모양  ·  프로그램 안의 언어모델  ·  한계와 사람의 몫")

# ───────────── 13. 활용 지도 ─────────────
s = new_slide()
title_bar(s, "활용 지도 — 여섯 갈래", "입력이 글이고 출력이 글이면 어디든 들어갑니다")
uses = [["글 다루기", "요약 · 번역 · 교정 · 초안 쓰기 · 말투 바꾸기", "메일 초안, 논문 요약, 외국어 회화 연습", TEAL],
        ["코드 다루기", "코드 생성 · 설명 · 오류 찾기 · 테스트 작성", "2교시 — AI 와 함께 코딩 · 디버깅", CORAL],
        ["묻고 답하기", "검색 대신 질문 · 내 문서를 넣고 그 안에서 찾기", "매뉴얼 · 규정 · 강의자료에 대해 묻기", TEAL],
        ["대화 서비스", "고객 상담 · 안내 · 예약 — 사람 대신 1차 응대", "14주차 — 챗봇 만들기", CORAL],
        ["데이터 다루기", "분류 · 정보 추출 · 표로 정리 · 감정 판단", "12주차 분류기를 학습 없이 질문 한 줄로", TEAL],
        ["에이전트", "도구(검색 · 계산 · 코드 실행)를 쓰며 여러 단계를 스스로", "코딩 에이전트, 여행 예약, 자료 조사", CORAL]]
x0, gap = 0.72, 0.26; w = (11.9 - gap * 2) / 3; h = 2.05
for i, u in enumerate(uses):
    x = x0 + (i % 3) * (w + gap); y = 1.95 + (i // 3) * (h + 0.22); c = u[3]
    card(s, x, y, w, h, TINT2 if c == CORAL else TINT)
    text(s, u[0], x + 0.3, y + 0.2, w - 0.6, 0.45, size=18, bold=True, color=CORAL if c == CORAL else TEAL_DK)
    text(s, u[1], x + 0.3, y + 0.7, w - 0.6, 0.75, size=13.5)
    text(s, "예) " + u[2], x + 0.3, y + 1.45, w - 0.6, 0.5, size=12.5, italic=True, color=GRAY)
text(s, "산호색 셋은 이 수업에서 직접 해 봅니다.", 0.72, 6.5, 11.9, 0.4, size=14, italic=True, color=GRAY)

# ───────────── 14. 세 가지 모양 ─────────────
s = new_slide()
title_bar(s, "언어모델을 만나는 세 가지 모양", "누가 쓰나 — 사람이, 프로그램이, 내 컴퓨터가")
three_cards(s, [
    {"head": "채팅 서비스", "badge": "💬", "color": TEAL, "fill": TINT,
     "body": "사람이 화면에서 직접 대화.\nChatGPT · Claude · Gemini …\n\n설치 없음 · 무료 또는 월 구독\n내 글이 회사 서버로 갑니다"},
    {"head": "API", "badge": "⚙", "color": CORAL, "fill": TINT2,
     "body": "내 프로그램이 함수 부르듯 모델을 부름.\n질문 문자열 → 답 문자열.\n\n토큰 수만큼 요금 · 인터넷 필요\n14주차 챗봇이 이 방식"},
    {"head": "오픈 모델", "badge": "⬇", "color": TEAL, "fill": TINT,
     "body": "모델 파일을 받아 내 컴퓨터에서 실행.\nLlama · Qwen · EXAONE …\n\n무료 · 데이터가 밖으로 안 나감\n성능은 작고 좋은 GPU 가 필요"},
], 2.0, 3.6)
card(s, 0.72, 5.9, 11.9, 0.85, AMBER_T)
text(s, "🤔  과제에 쓴 내 코드와 글이 어디로 가는지 생각해 보세요. 셋 중 어느 모양이냐에 따라 다릅니다. 회사의 비밀 자료나 개인정보는 ① 과 ② 에 넣기 전에 규칙을 확인해야 합니다.", 0.95, 5.9, 11.5, 0.85, size=14, color=AMBER_DK, valign="middle")

# ───────────── 15. 프로그램 안의 언어모델 ─────────────
s = new_slide()
title_bar(s, "프로그램 안에서는 함수 하나처럼 보입니다", "문자열을 넣으면 문자열이 나온다 — 12주차 분류기를 학습 없이")
mono(s, '# 12주차 — 160건으로 학습한 뒤\nmodel.fit(train_x, train_y)\nlabels[model.predict(encode("손흥민 두 골 폭발", vocab))]\n#  → \'스포츠\'', 0.72, 1.95, 5.75, 1.9, size=13)
mono(s, '# 언어모델 — 학습 없이 질문 한 줄\nanswer = ask_model(\n    "다음 뉴스 제목의 주제를 스포츠·경제·날씨·음식 "\n    "중 하나로만 답하세요: 손흥민 두 골 폭발")\nprint(answer)      # 스포츠', 6.87, 1.95, 5.75, 1.9, size=13, fill=TEAL_DK)
text(s, "ask_model 은 설명용 이름입니다. 실제 이름은 회사의 라이브러리마다 다르고, 14주차에 진짜 코드를 씁니다.", 0.72, 3.95, 11.9, 0.35, size=12, italic=True, color=GRAY)
card(s, 0.72, 4.45, 5.75, 2.3, TINT)
text(s, "좋아지는 것", 1.05, 4.65, 4, 0.45, size=18, bold=True, color=TEAL_DK)
bullets(s, ["데이터 모으기 · 라벨 붙이기 · 학습이 없습니다", "주제를 다섯 개로 늘리는 것도 문장 한 줄 고치기", "분류 말고 요약 · 번역 · 추출도 같은 함수"], 1.05, 5.15, 5.1, 1.6, size=14, space=4)
card(s, 6.87, 4.45, 5.75, 2.3, TINT2)
text(s, "대신 생기는 것", 7.2, 4.65, 4, 0.45, size=18, bold=True, color=CORAL)
bullets(s, ["부를 때마다 요금 · 인터넷 · 1 ~ 몇 초의 기다림", "답이 매번 같지 않습니다 — 형식을 못 지키면 코드가 깨짐", "내 데이터가 밖으로 나갑니다"], 7.2, 5.15, 5.1, 1.6, size=14, space=4)

# ───────────── 16. 없는 것 채우기 ─────────────
s = new_slide()
title_bar(s, "모델에게 없는 것을 채워 주는 두 가지 방법", "모르는 것은 넣어 주고, 못 하는 것은 도구를 쥐여 준다")
card(s, 0.72, 1.95, 5.75, 4.75, TINT)
badge(s, 1.05, 2.3, 0.55, TEAL, "📄", 14)
text(s, "문서를 질문과 함께 넣기", 1.75, 2.28, 4.6, 0.6, size=19, bold=True, color=TEAL_DK, valign="middle")
text(s, "검색 증강 생성 (retrieval-augmented generation, RAG)", 1.05, 2.95, 5.1, 0.35, size=12, color=GRAY)
bullets(s, ["모델은 학습 데이터 마감일 이후를 모르고, 내 문서는 본 적이 없습니다.",
            "그래서 질문과 관련 있는 문서 조각을 먼저 찾아, 질문 앞에 붙여 넣습니다.",
            "“아래 강의자료를 보고 답하세요: (자료) … 질문: 과제 마감은?”",
            "회사 규정 · 매뉴얼 · 논문 질의응답이 대부분 이 방식입니다."], 1.05, 3.4, 5.1, 3.2, size=14, space=5)
card(s, 6.87, 1.95, 5.75, 4.75, TINT2)
badge(s, 7.2, 2.3, 0.55, CORAL, "🔧", 14)
text(s, "도구를 쓰게 하기", 7.9, 2.28, 4.6, 0.6, size=19, bold=True, color=CORAL, valign="middle")
text(s, "도구 사용 (tool use) → 에이전트 (agent)", 7.2, 2.95, 5.1, 0.35, size=12, color=GRAY)
bullets(s, ["모델은 큰 수 계산 · 오늘 날씨 · 파일 열기를 못 합니다. 글만 쓰니까요.",
            "대신 “계산기를 써라”, “검색해라”, “이 코드를 실행해라” 하고 글로 요청하면, 프로그램이 그 일을 하고 결과를 다시 넣어 줍니다.",
            "이 주고받기를 스스로 여러 번 반복하는 것이 에이전트. 코딩 에이전트는 파일 읽기 → 코드 쓰기 → 테스트 실행 → 고치기를 돌립니다."], 7.2, 3.4, 5.1, 3.2, size=14, space=5)

# ───────────── 17. 한계 ─────────────
s = new_slide()
title_bar(s, "못 하는 것, 조심할 것", "확률로 다음 조각을 고르는 기계이기 때문에 생기는 일들")
lims = [["그럴듯한 거짓 — 환각", "hallucination", "없는 논문, 틀린 날짜, 존재하지 않는 함수를 자신 있게 씁니다. ‘모른다’보다 ‘그럴 법한 다음 조각’이 확률이 높으니까요.\n12주차에서 모르는 단어 네 개짜리 제목에도 자신 있게 답하던 그 현상입니다.", CORAL],
        ["시점과 상황을 모름", "knowledge cutoff", "학습 데이터 마감일 이후의 일, 내 수업 · 내 과제 · 내 파일은 모릅니다. 넣어 주지 않으면 지어냅니다.", TEAL],
        ["매번 같지 않음", "non-deterministic", "주사위를 던져 고르므로 같은 질문에 다른 답. 코드도 매번 조금 다르게 나옵니다. 검증 없이 믿을 수 없는 이유.", TEAL],
        ["편향 · 개인정보 · 저작권", "", "인터넷 글을 배웠으니 그 글의 편견도 배웠습니다. 입력한 글이 학습에 쓰일 수 있고, 출력이 남의 글과 비슷할 수 있습니다.", CORAL]]
x0, gap = 0.72, 0.26; w = (11.9 - gap) / 2; h = 2.1
for i, l in enumerate(lims):
    x = x0 + (i % 2) * (w + gap); y = 1.95 + (i // 2) * (h + 0.22); c = l[3]
    card(s, x, y, w, h, TINT2 if c == CORAL else TINT)
    text(s, [(l[0], {"bold": True, "size": 18, "color": CORAL if c == CORAL else TEAL_DK}), ("   " + l[1], {"size": 12, "color": GRAY})], x + 0.3, y + 0.2, w - 0.6, 0.5, valign="middle")
    text(s, l[2], x + 0.3, y + 0.75, w - 0.6, h - 0.9, size=13.5)
text(s, "이 가운데 어느 것도 ‘고장’이 아닙니다. 다음 조각의 확률을 매기는 기계가 원래 그렇게 동작합니다.", 0.72, 6.55, 11.9, 0.4, size=14, italic=True, color=GRAY)

# ───────────── 18. 사람의 몫 ─────────────
s = new_slide()
title_bar(s, "그래서 사람의 몫 — 잘 묻고, 반드시 검증한다", "12주차 ‘사람의 몫 두 가지’가 언어모델 시대에도 그대로")
card(s, 0.72, 1.95, 5.75, 4.75, TINT)
text(s, "잘 묻기 = 문제 정의", 1.05, 2.2, 5, 0.5, size=19, bold=True, color=TEAL_DK)
for i, r in enumerate([["입력", "무엇을 줄 것인가 — 데이터 · 예시 · 지금 코드"], ["출력", "무엇이 나와야 하나 — 형식까지 (표 · 코드만 · 세 줄)"],
                       ["범위", "어디까지 — 길이 · 언어 · 쓰면 안 되는 것"], ["맥락", "누구를 위해, 왜 — 수업 · 1학년 · Python"]]):
    y = 2.85 + i * 0.85
    badge(s, 1.05, y + 0.1, 0.45, TEAL, str(i + 1), 13)
    text(s, r[0], 1.65, y, 1.0, 0.65, size=15, bold=True, valign="middle")
    text(s, r[1], 2.65, y, 3.6, 0.65, size=13.5, valign="middle")
text(s, "12주차 ‘세 질문’에 맥락 하나를 더한 것입니다. 2교시에서 연습합니다.", 1.05, 6.25, 5.1, 0.4, size=12.5, italic=True, color=GRAY)
card(s, 6.87, 1.95, 5.75, 4.75, TINT2)
text(s, "검증하기", 7.2, 2.2, 5, 0.5, size=19, bold=True, color=CORAL)
bullets(s, ["코드는 돌려 본다 — 여러 입력, 특히 이상한 입력으로", "사실은 출처를 확인한다 — 논문 · 함수 이름 · 날짜",
            "설명을 요구한다 — “이 줄은 왜 필요한가?”", "두 번 물어본다 — 답이 크게 다르면 둘 다 의심"], 7.2, 2.85, 5.1, 2.6, size=14, space=5)
card(s, 7.2, 5.5, 5.1, 1.0, WHITE, line=CORAL, line_w=1.5)
text(s, "수업 규칙 — AI 가 쓴 코드를 그대로 제출하는 것은 금지. 제출한 코드는 팀원 누구나 설명할 수 있어야 합니다.", 7.4, 5.5, 4.7, 1.0, size=13, bold=True, color=CORAL, valign="middle")

# ───────────── 19. 정리 ─────────────
s = new_slide()
title_bar(s, "1교시 정리", "다섯 줄로")
for i, p in enumerate([["언어모델 = 앞 글을 보고 다음 토큰의 확률을 매기는 프로그램", "휴대폰 자판 추천어부터 ChatGPT 까지 같은 일"],
                       ["한 조각 고르고 붙이고 반복 → 글이 된다", "주사위로 고르니 답이 매번 다르고, 조각(토큰) 수만큼 시간과 요금"],
                       ["12주차와 재료는 같고 규모가 다르다", "글 자체가 정답이라 데이터를 무한히 늘릴 수 있었고, 트랜스포머로 크게 키웠다"],
                       ["사전학습 → 지시 학습 → 선호 학습을 거쳐 대화가 된다", "글 · 코드 · 질의응답 · 챗봇 · 데이터 · 에이전트에 쓰이고, 채팅 · API · 오픈 모델 세 모양"],
                       ["환각 · 시점 · 비결정성 · 편향은 고장이 아니라 성질", "그래서 사람의 몫 — 입력 · 출력 · 범위 · 맥락으로 잘 묻고, 반드시 검증"]]):
    y = 1.95 + i * 0.92; odd = i % 2 == 1
    card(s, 0.72, y, 11.9, 0.8, TINT2 if odd else TINT)
    badge(s, 1.0, y + 0.15, 0.5, CORAL if odd else TEAL, str(i + 1), 14)
    text(s, p[0], 1.7, y, 5.3, 0.8, size=15.5, bold=True, valign="middle")
    text(s, p[1], 7.1, y, 5.3, 0.8, size=13.5, valign="middle")
text(s, "다음: 2교시 — AI 프로젝트 오리엔테이션", 0.72, 6.65, 11.9, 0.4, size=14, italic=True, color=GRAY)

# 쪽번호
N = len(slides)
for i, s in enumerate(slides):
    text(s, f"{i + 1}/{N}", 12.2, 7.05, 0.9, 0.3, size=10, color=GRAY, align="right", name="쪽번호")

prs.save(OUT)
print("saved", OUT, N, "slides")

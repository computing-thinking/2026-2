# AI 프로젝트 팀 발표용 공용 슬라이드 템플릿 (python-pptx)
# 회차마다 파일 하나: 표지 1장 + 7팀 × 5장 = 36장. 교수가 Google 드라이브에 올려 Google Slides로 열고(변환) 링크를 LearnUs 에 공지한다.
# 팀 자리 5장: 1장은 팀명·팀원·발표자(공통), 2~5장은 회차마다 ROUNDS[n]["pages"] 로 지정한다.
#   {"kind": "fields", "head": 제목, "fields": [(칸 제목, 안내), ...]}  칸 2개면 좌우, 4개면 2×2
#   {"kind": "free", "head": 제목, "hint": 안내, "must": 꼭 채우는 장인지}
# 1회차 검토에서 배운 것: 안내문을 본문 상자 안에 두면 그림을 붙여도 안내문이 남는다 → 안내는 칸 제목 옆 작은 글씨로 두고, 본문에는 짧은 자리표시만 둔다.
# 사용: python tools/build_project_slides_template.py <출력폴더>   → 1회차 ~ 4회차 전부
#       python tools/build_project_slides_template.py <출력폴더> 2  → 2회차만
import os, sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

TEAL, TEAL_DK, CORAL, DARK, GRAY = "0EA5A4", "0B7C7B", "FF6B5A", "1F2937", "6B7280"
TINT, TINT2, AMBER_T, AMBER_DK, WHITE, LINE, LIGHT = "E6F7F6", "FFF0EE", "FFF7E6", "B45309", "FFFFFF", "BFE9E7", "F3F4F6"
FONT = "맑은 고딕"
TEAMS, PER = 7, 5
PLACE = "여기에 적습니다 — 이 글은 지우고 쓰세요"
PLACE_PIC = "여기에 화면 캡처나 그림을 붙입니다 — 이 글은 지우세요"

FREE = lambda must: {"kind": "free", "head": "자유" + ("" if must else " (있으면)"),
                     "hint": ("그림 · 화면 · 표 · 막힌 곳 — 이 장은 꼭 채웁니다. 글이면 세 줄 이내, 그림이면 한 장."
                              if must else "그림 · 화면 · 표 — 있으면 채우고, 없으면 이 장은 그대로 둡니다."), "must": must}

ROUNDS = {
    1: dict(title="1회차 발표 — 팀명 · 팀 규칙 · 문제 정의", when="13주 3교시 (목)", speaker="문제 정의자", due="수요일 밤",
            pages=[{"kind": "fields", "head": "문제 정의",
                    "fields": [("누구의 불편", "누가 · 언제 · 무엇이 불편한가 — 한 줄"), ("입력", "프로그램에 넣는 것"),
                               ("출력", "프로그램이 내놓는 것"), ("범위", "이번에 하는 것 / 하지 않는 것")]},
                   FREE(True), FREE(False), FREE(False)]),
    2: dict(title="2회차 발표 — 피드백 반영 · 데이터 · 첫 코드", when="14주 2교시 (12월 1일 화)", speaker="프롬프터", due="11월 30일 (월) 밤",
            note="1회차 발표 코멘트는 LearnUs 공지에 있습니다. 2장은 그 코멘트에 대한 답입니다 — 문제 정의를 꼭 바꿔야 하는 것은 아닙니다.",
            pages=[{"kind": "fields", "head": "1회차 피드백 반영 — 문제 정의",
                    "fields": [("문제 정의 (한 줄)", "누구의 · 입력 → 출력. 바뀐 부분은 굵게. 안 바뀌었으면 1회차 것을 그대로 적습니다"),
                               ("피드백에 대한 답", "교수 코멘트 · 다른 팀 질문에 어떻게 대응했는지. 바꾸지 않기로 했다면 그 이유도 좋은 답입니다")]},
                   {"kind": "fields", "head": "데이터 — 어디서, 어떻게 만들었나",
                    "fields": [("출처와 만드는 방법", "직접 입력 · csv 손으로 작성 · AI로 생성 · 모의 시스템 — 몇 건인지 숫자로"),
                               ("실제 예시 3줄", "지금 가진 데이터를 그대로 붙여넣기 (표 · 글 · 캡처)")]},
                   {"kind": "fields", "head": "도구와 첫 코드",
                    "fields": [("쓴 도구", "챗봇(어느 것) · 라이브러리 · 실행한 곳(수업 사이트 / Colab / VS Code)"),
                               ("돌아간 화면 한 장", "입력 → 출력이 보이는 캡처. 짧아도 됩니다 — 아직 안 돌면 오류 화면")], "pic": 1},
                   {"kind": "fields", "head": "막힌 곳 · 다음 발표(목)까지",
                    "fields": [("막힌 곳 — 질문 1 ~ 2개", "무엇을 시도했고 어디서 멈췄는지. 교수와 다른 팀이 답합니다"),
                               ("3회차(12월 3일 목)까지 할 일", "누가 · 무엇을")]}]),
    3: dict(title="3회차 발표 — 만들기 · 검증", when="14주 3교시 (12월 3일 목)", speaker="검증자", due="12월 2일 (수) 밤",
            pages=[{"kind": "fields", "head": "만들기 · 검증",
                    "fields": [("만든 것", "지금 동작하는 부분"), ("검증 방법", "무엇으로 맞는지 확인했나"),
                               ("검증 결과", "맞은 것 · 틀린 것"), ("남은 일", "제출(12월 8일 월)까지")]},
                   FREE(True), FREE(False), FREE(False)]),
    4: dict(title="최종 발표 — 시연 · 과정 기록", when="15주 1교시 (12월 8일 화)", speaker="기록자 (3명 팀은 공동)", due="12월 7일 (월) 밤",
            pages=[{"kind": "fields", "head": "결과물과 과정",
                    "fields": [("문제", "한 줄"), ("결과물", "시연 — 입력 → 출력"),
                               ("과정 기록", "막힌 곳과 넘은 방법 · AI와 나눈 것"), ("배운 것", "다음에 다르게 할 것")]},
                   FREE(True), FREE(False), FREE(False)]),
}


# 앞 회차 발표 자료에서 옮겨 적는 팀 구성 (1장 미리 채우기). 팀명이 없으면 None → 안내문 유지. 셋째 값(발표자)은 참고용이며 슬라이드에는 넣지 않는다.
# 출처: 1회차 학생 작성본(11/26) + 발표 진행 현황.xlsx(7팀 최주미 추가)
PREFILL = {
    2: {
        1: ("MEMO", ["김승열 — 문제 정의자", "이민규 — 프롬프터", "이하원 — 검증자", "전혜린 — 기록자"], "이민규"),
        2: (None, ["유정민 — 문제 정의자", "김신실 — 프롬프터", "조예찬 — 검증자", "다같이 — 기록자"], "김신실"),
        3: (None, ["김예은 — 문제 정의자 · 기록자", "김진현 — 프롬프터", "장아영 — 검증자"], "김진현"),
        4: ("알뜰배달단", ["문정윤 — 문제 정의자", "심민석 — 프롬프터", "김유나 — 검증자", "김태윤 — 기록자"], "심민석"),
        5: ("머니로그", ["지희수 — 문제 정의자", "권태우 — 프롬프터", "용태영 — 검증자", "김은지 — 기록자"], "권태우"),
        6: ("소비탐정단", ["권윤지 — 문제 정의자", "이하율 — 프롬프터", "이아인 — 검증자", "모두 — 기록자"], "이하율"),
        7: ("점메추", ["손가람 — 문제 정의자 · 검증자", "최연우 — 프롬프터", "오현서 — 기록자", "최주미 — (역할 적기)"], "최연우"),
    },
}


def rgb(h): return RGBColor.from_string(h)


def shape(s, kind, x, y, w, h, fill, line=None, line_w=None, radius=None):
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    if line: sh.line.color.rgb = rgb(line); sh.line.width = Pt(line_w or 1)
    else: sh.line.fill.background()
    sh.shadow.inherit = False
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def card(s, x, y, w, h, fill, line=None, line_w=None):
    return shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, line, line_w, radius=min(0.18 / min(w, h), 0.5))


def text(s, t, x, y, w, h, size=15, bold=False, color=DARK, align="left", valign="top", italic=False):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}[valign]
    al = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    for i, ln in enumerate(t.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = al
        r = p.add_run(); r.text = ln
        f = r.font; f.name = FONT; f.size = Pt(size); f.bold = bold; f.italic = italic; f.color.rgb = rgb(color)
        rPr = r._r.get_or_add_rPr(); rPr.set("lang", "ko-KR")
        for tag in ("ea", "cs"):
            el = rPr.makeelement(qn("a:" + tag), {"typeface": FONT}); rPr.append(el)
    return tb


def badge(s, x, y, d, color, label, size=14):
    shape(s, MSO_SHAPE.OVAL, x, y, d, d, color)
    text(s, label, x, y, d, d, size=size, bold=True, color=WHITE, align="center", valign="middle")


def field_card(s, x, y, w, h, hd, hint, fill, place):
    """칸: 제목(굵게) + 안내(작게, 회색) 를 위에 두고, 그 아래 본문 자리표시 글상자."""
    card(s, x, y, w, h, fill, line=LINE)
    text(s, hd, x + 0.3, y + 0.15, w - 0.6, 0.4, size=17, bold=True, color=TEAL_DK)
    text(s, hint, x + 0.3, y + 0.55, w - 0.6, 0.5, size=11.5, color=GRAY)
    text(s, place, x + 0.3, y + 1.1, w - 0.6, h - 1.3, size=18, color=GRAY, italic=True)


def build(rnd, out):
    R = ROUNDS[rnd]
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]
    slides = []

    def new_slide(bg=WHITE):
        s = prs.slides.add_slide(blank)
        f = s.background.fill; f.solid(); f.fore_color.rgb = rgb(bg)
        slides.append(s); return s

    # ── 표지 (교수) ──
    s = new_slide(TINT)
    shape(s, MSO_SHAPE.OVAL, 10.2, -0.6, 3.6, 3.6, WHITE)
    text(s, "컴퓨팅사고 · AI 프로젝트", 0.75, 0.55, 8, 0.5, size=18, bold=True, color=TEAL_DK)
    text(s, R["title"], 0.75, 1.05, 11.5, 0.9, size=34, bold=True)
    text(s, f"{R['when']}  ·  팀당 5분 (발표 3분 + 질문 2분)  ·  발표자: {R['speaker']}", 0.75, 1.95, 11.5, 0.45, size=16, color=GRAY)
    text(s, "우리 팀 자리", 0.75, 2.7, 4, 0.4, size=16, bold=True, color=CORAL)
    for i in range(TEAMS):
        x = 0.75 + i * 1.7
        a = 2 + i * PER
        card(s, x, 3.15, 1.55, 1.05, WHITE, line=LINE)
        text(s, f"{i + 1}팀", x, 3.22, 1.55, 0.45, size=18, bold=True, color=TEAL_DK, align="center")
        text(s, f"{a} ~ {a + PER - 1}장", x, 3.68, 1.55, 0.4, size=13, color=GRAY, align="center")
    # 5장 구성 한 줄
    heads = " → ".join(["1장 팀 · 발표자"] + [f"{k + 2}장 {p['head'].split(' — ')[0]}" for k, p in enumerate(R["pages"])])
    text(s, heads, 0.75, 4.3, 11.85, 0.4, size=13, color=TEAL_DK)
    card(s, 0.75, 4.8, 11.85, 2.15, AMBER_T)
    text(s, "규칙", 1.05, 4.92, 3, 0.4, size=16, bold=True, color=AMBER_DK)
    rules = [f"마감: {R['due']} — 마감 뒤 이 파일은 보기만 됩니다.",
             "자기 팀 자리 5장만 편집합니다. 회색 기울임 글은 안내이니 지우고 씁니다. 장을 늘리거나 지우지 않고, 쪽번호 · 제목은 그대로 둡니다.",
             "다른 팀 자리는 건드리지 않습니다. 실수로 지웠으면 바로 단톡방에 알립니다 — 되돌릴 수 있습니다.",
             "다른 팀 것을 참고했으면 ‘N팀 방식 참고’라고 적습니다. 글자 크기 18 이상 — 안 들어가면 줄이지 말고 내용을 줄입니다."]
    if R.get("note"): rules.insert(1, R["note"])
    tb = s.shapes.add_textbox(Inches(1.05), Inches(5.32), Inches(11.3), Inches(1.6))
    tf = tb.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, it in enumerate(rules):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(3)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(Inches(0.22))); pPr.set("indent", str(-Inches(0.22)))
        bu = pPr.makeelement(qn("a:buClr"), {}); bu.append(bu.makeelement(qn("a:srgbClr"), {"val": AMBER_DK})); pPr.append(bu)
        pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "•"}))
        r = p.add_run(); r.text = it
        f = r.font; f.name = FONT; f.size = Pt(13); f.color.rgb = rgb(DARK)
        rPr = r._r.get_or_add_rPr()
        for tag in ("ea", "cs"):
            rPr.append(rPr.makeelement(qn("a:" + tag), {"typeface": FONT}))

    # ── 팀 자리 ──
    short = R["title"].split(" — ")[0]
    for t in range(1, TEAMS + 1):
        for k in range(1, PER + 1):
            s = new_slide()
            shape(s, MSO_SHAPE.RECTANGLE, 0, 0, 13.333, 0.12, CORAL if k == 1 else TEAL)
            badge(s, 0.72, 0.42, 0.62, CORAL, f"{t}팀", 14)
            text(s, f"{k} / {PER}", 1.5, 0.42, 1.2, 0.62, size=13, color=GRAY, valign="middle")
            if k == 1:
                text(s, "팀명 · 팀원 · 이번 회차 발표자", 2.6, 0.42, 9.9, 0.62, size=26, bold=True, valign="middle")
                card(s, 0.72, 1.4, 11.9, 1.55, TINT2, line=CORAL, line_w=1.5)
                pf = PREFILL.get(rnd, {}).get(t)
                text(s, "팀명", 1.05, 1.55, 2, 0.4, size=14, bold=True, color=CORAL)
                if pf and pf[0]:
                    text(s, pf[0], 1.05, 1.95, 11.2, 0.85, size=32, bold=True)
                else:
                    text(s, "여기에 팀명 (한글 2 ~ 6자)" + (" — 이번에는 꼭 정합니다" if pf else ""), 1.05, 1.95, 11.2, 0.85, size=32, bold=True, color=GRAY, italic=True)
                card(s, 0.72, 3.2, 7.6, 3.5, TINT)
                text(s, "팀원과 역할" + (" — 앞 회차 자료에서 옮겨 적음. 바뀌었으면 고치세요" if pf else ""), 1.05, 3.35, 7, 0.4, size=14, bold=True, color=TEAL_DK)
                if pf:
                    text(s, "\n".join(pf[1]), 1.05, 3.85, 7, 2.7, size=20)
                else:
                    text(s, "이름 — 문제 정의자\n이름 — 프롬프터\n이름 — 검증자\n이름 — 기록자  (3명 팀은 한 사람이 둘)", 1.05, 3.85, 7, 2.7, size=20, color=GRAY, italic=True)
                card(s, 8.6, 3.2, 4.02, 3.5, LIGHT)
                text(s, "이번 회차 발표자", 8.9, 3.35, 3.5, 0.4, size=14, bold=True, color=TEAL_DK)
                # 발표자는 팀이 바꿀 수 있으므로 미리 채우지 않는다
                text(s, "이름", 8.9, 3.85, 3.4, 0.7, size=26, bold=True, color=GRAY, italic=True)
            else:
                P = R["pages"][k - 2]
                text(s, P["head"], 2.6, 0.42, 9.9, 0.62, size=26, bold=True, valign="middle")
                if P["kind"] == "fields":
                    fl = P["fields"]
                    if len(fl) == 2:
                        for i, (hd, hint) in enumerate(fl):
                            x = 0.72 + i * 6.05
                            place = PLACE_PIC if P.get("pic") == i else PLACE
                            field_card(s, x, 1.4, 5.85, 5.3, hd, hint, TINT if i == 0 else WHITE, place)
                    else:
                        for i, (hd, hint) in enumerate(fl):
                            col, row = i % 2, i // 2
                            x, y = 0.72 + col * 6.05, 1.4 + row * 2.75
                            field_card(s, x, y, 5.85, 2.55, hd, hint, TINT if (col + row) % 2 == 0 else WHITE, PLACE)
                else:
                    card(s, 0.72, 1.4, 11.9, 5.3, WHITE, line=LINE)
                    text(s, P["hint"], 1.05, 1.6, 11.2, 1.2, size=18, color=GRAY, italic=True)
            text(s, f"{t}팀 자리 · {short}", 0.72, 7.05, 6, 0.3, size=10, color=GRAY)

    N = len(slides)
    for i, s in enumerate(slides):
        text(s, f"{i + 1}/{N}", 12.2, 7.05, 0.9, 0.3, size=10, color=GRAY, align="right")
    prs.save(out)
    print("saved", out, N, "slides")


if __name__ == "__main__":
    folder = sys.argv[1]
    which = [int(sys.argv[2])] if len(sys.argv) > 2 else list(ROUNDS)
    for r in which:
        name = f"AI프로젝트_발표자료_{r}회차.pptx" if r < 4 else "AI프로젝트_발표자료_4회차_최종.pptx"
        build(r, os.path.join(folder, name))

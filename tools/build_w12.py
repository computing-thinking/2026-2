import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 12주차 노트북 생성 스크립트 — 수업용 노트북 한 파일(실습 정답은 접어 둠) + 과제 정답(교수용)
# 주제: 인공지능 라이브러리로 문서 분류 응용 만들기   — 2교시 분량
#   1교시: 인공지능 모델 개관(학습 · 추론 · 손실 · 에포크 · 과적합) · 문서를 숫자로 · 인공지능 라이브러리 지도와 가져다 쓰는 법
#   2교시: RNN 으로 뉴스 제목 분류기 만들기 (데이터 → 전처리 → 모델 → 학습 → 평가 → 추론)
# 수업 사이트(Pyodide)에는 PyTorch 가 없다. 그래서 RNN 은 numpy 로 만든 작은 모듈 minirnn.py 를 %%writefile 로 만들어
# 라이브러리처럼 import 해 쓰고, PyTorch 판은 접은 상자(Colab · PC 용)로 둔다.
# 사용: python build_w12.py           → 셀 구성만 점검(파일을 쓰지 않음)
#       python build_w12.py --write   → 강의자료 폴더에 .ipynb 저장 (이미 있으면 중단)
import base64, hashlib, html, json, os, sys
from site_common import INTRO_SITE

DEST = r"D:\AI융합과학원\학교강의\컴퓨팅사고\강의자료"
MAIN_NB = "컴퓨팅사고_12주차_문서분류.ipynb"
HW_SOL = "컴퓨팅사고_12주차_과제정답.ipynb"

# ───────────────────────── HTML 상자 (11주차 노트북과 같은 값) ─────────────────────────
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


def answer(label, title, code):
    """💡 실습 정답 — 접어 둔다"""
    return (f'<details style="background:#FFFFFF;color:#1F2937;border:1px dashed #FF6B5A;padding:10px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><summary style="cursor:pointer;color:#FF6B5A;font-weight:bold;">💡 {label} 정답 예시 — {title} (먼저 스스로 풀어 본 뒤 여세요)</summary>'
            f'<div style="margin-top:8px;">{code_block(code)}</div></details>')


def warn(title, body):
    return (f'<div style="background:#FFF0EE;color:#1F2937;border-left:6px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#FF6B5A;">⚠️ {fmt(title)}</b><br>{fmt(body)}</div>')


def think(title, body):
    """🧠 컴퓨팅 사고 상자 — 문제를 푸는 ‘생각의 단계’를 정리할 때"""
    return (f'<div style="background:#FFF7E6;color:#1F2937;border-left:6px solid #F59E0B;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#B45309;">🧠 {fmt(title)}</b><br>{fmt(body)}</div>')


def ponder(title, body):
    """🤔 생각해 보기 상자 — 학생이 스스로 답할 질문"""
    return (f'<div style="background:#FFF7E6;color:#1F2937;border-left:6px solid #F59E0B;padding:12px 18px;'
            f'border-radius:8px;margin:8px 0;line-height:1.7;{BOX}"><b style="color:#B45309;">🤔 {fmt(title)}</b><br>{fmt(body)}</div>')


def task_box(label, title, minutes, body):
    m = f' <span style="color:#6B7280;font-weight:normal;">({minutes})</span>' if minutes else ""
    return (f'<div style="background:#FFFFFF;color:#1F2937;border:2px solid #FF6B5A;padding:12px 18px;'
            f'border-radius:12px;margin:8px 0;line-height:1.7;{BOX}"><span style="background:#FF6B5A;color:#FFFFFF;'
            f'padding:2px 12px;border-radius:999px;font-weight:bold;">{label}</span>&nbsp; <b>{title}</b>{m}<br>{fmt(body)}</div>')


def code_block(code):
    return ('<pre style="background:#1F2937;color:#F9FAFB;padding:14px 16px;border-radius:10px;font-family:Consolas,monospace;'
            f'line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere;box-sizing:border-box;max-width:100%;">{html.escape(code.strip())}</pre>')


def img_fig(filename, caption, max_width=820):
    """강의자료 폴더의 PNG 를 base64 로 본문에 넣는다. 외부 파일 없이 어디서 열어도 보인다."""
    with open(os.path.join(DEST, filename), "rb") as f:
        data = base64.b64encode(f.read()).decode("ascii")
    return (f'<div style="text-align:center;margin:10px 0;{BOX}">'
            f'<img src="data:image/png;base64,{data}" alt="{html.escape(caption)}" '
            f'style="max-width:min(100%,{max_width}px);height:auto;background:#FFFFFF;border-radius:8px;padding:6px;">'
            f'<div style="color:#6B7280;font-size:0.9em;margin-top:4px;">{fmt(caption)}</div></div>')


def period(n, title, goals):
    lis = "".join(f"<li>{g}</li>" for g in goals)
    return (f'<div style="background:#0EA5A4;color:#FFFFFF;padding:20px 26px;border-radius:14px;{BOX}">'
            f'<span style="background:#FF6B5A;color:#FFFFFF;padding:3px 14px;border-radius:999px;font-weight:bold;">{n}교시</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.5em;font-weight:bold;">{title}</span>'
            f'<span style="float:right;opacity:0.9;">⏱ 약 50분</span>'
            f'<ul style="margin:10px 0 0 0;line-height:1.7;">{lis}</ul></div>')


def problem(title, question):
    """문제 표지 띠"""
    return (f'<div style="background:#1F2937;color:#F9FAFB;padding:14px 22px;border-radius:12px;margin:12px 0;{BOX}">'
            f'<span style="background:#F59E0B;color:#1F2937;padding:3px 14px;border-radius:999px;font-weight:bold;">오늘의 문제</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.3em;font-weight:bold;">{title}</span>'
            f'<div style="margin-top:8px;opacity:0.92;line-height:1.7;">{fmt(question)}</div></div>')


BREAK = '<div style="text-align:center;color:#6B7280;">☕ 쉬는 시간 — 10분</div>'
CHECK_HEAD = "# 🔍 자가 점검 — 수정하지 말고 실행만 하세요\n"

# ───────────────────────── 셀 모으기 ─────────────────────────
CELLS = []          # (type, source, metadata)
PRACTICES = []      # (이름, 정답 코드, 점검 셀 코드) — test_w12.py 가 사용


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


def practice(label, title, minutes, body, skeleton, test, solution, raises=True, heading=None, show_answer=True):
    """✏️ 상자 → 작성용 셀 → 🔍 점검 셀 → 💡 정답(접힘).  작성용 셀은 답을 쓰기 전엔 NameError 가 나므로 raises 태그를 붙인다"""
    box = task_box(label, title, minutes, body)
    md((heading + "\n\n" if heading else "") + box)
    code(skeleton, raises=raises)
    name = label.split(" ", 1)[1]
    chk = CHECK_HEAD + f'check("{name}", lambda: {test})'
    code(chk)
    if show_answer:
        md(answer(label, title, solution))
    PRACTICES.append((name, solution.strip("\n"), chk))


# ═════════════════════════ 데이터 — 뉴스 제목 160개 (4 주제 × 40) ═════════════════════════
NEWS = """text,label
손흥민 두 골 폭발 토트넘 역전승,스포츠
한국 야구 대표팀 결승 진출,스포츠
프로야구 개막전 만원 관중 열기,스포츠
김연아 피겨 갈라쇼 전석 매진,스포츠
월드컵 예선 한국 대표팀 승리,스포츠
프로축구 K리그 우승 경쟁 치열,스포츠
마라톤 대회 참가자 기록 경신,스포츠
농구 대표팀 역전승으로 결승 진출,스포츠
배구 여자 대표팀 올림픽 티켓 확보,스포츠
골프 박세리 은퇴 경기 감동,스포츠
올림픽 양궁 대표팀 금메달 획득,스포츠
축구 국가대표 평가전 무승부,스포츠
프로야구 홈런왕 경쟁 막판 스퍼트,스포츠
테니스 결승 접전 끝에 우승,스포츠
수영 대표팀 아시안게임 금메달 기록,스포츠
야구 한국시리즈 7차전 역전 우승,스포츠
축구 손흥민 리그 득점왕 등극,스포츠
농구 결승 연장 승부 끝 우승,스포츠
배구 리그 개막 첫 경기 승리,스포츠
올림픽 태권도 대표팀 금메달 추가,스포츠
스키 점프 대표팀 월드컵 출전,스포츠
핸드볼 결승 진출 메달 확보,스포츠
육상 100m 한국 기록 경신,스포츠
프로축구 득점왕 시즌 20호 골,스포츠
배드민턴 대표팀 결승 우승 확정,스포츠
야구 대표팀 평가전 역전승,스포츠
피겨 대표팀 올림픽 티켓 획득,스포츠
축구 결승 승부차기 끝 우승,스포츠
농구 리그 득점왕 경쟁 치열,스포츠
마라톤 금메달 한국 기록 경신,스포츠
야구 개막전 홈런 두 방 승리,스포츠
축구 대표팀 월드컵 본선 진출 확정,스포츠
골프 대회 우승 상금 기록 경신,스포츠
배구 결승 역전승 우승 감동,스포츠
올림픽 수영 금메달 한국 기록,스포츠
프로야구 관중 100만 돌파 열기,스포츠
테니스 대표팀 아시안게임 금메달,스포츠
농구 대표팀 월드컵 첫 승리,스포츠
양궁 결승 접전 끝 금메달 획득,스포츠
축구 리그 개막전 손흥민 골 승리,스포츠
코스피 사상 최고치 경신 마감,경제
금리 인상에 대출 이자 부담 증가,경제
환율 급등 수출 기업 실적 개선,경제
반도체 수출 호조 무역수지 흑자,경제
물가 상승률 3퍼센트 소비 위축,경제
은행 예금 금리 인하 전망,경제
부동산 거래 감소 집값 하락세,경제
중소기업 대출 연체율 상승 우려,경제
주식 시장 외국인 매수 증가,경제
원유 가격 급등 물가 상승 압박,경제
수출 증가로 경제 성장률 상향,경제
코스닥 급락 투자자 손실 확대,경제
기업 실적 발표 주가 상승,경제
환율 하락 수입 물가 안정,경제
금리 동결 결정 대출 시장 안도,경제
부동산 세금 개편 집값 영향,경제
소비 심리 회복 소매 판매 증가,경제
주식 배당 확대 투자자 관심,경제
은행 대출 심사 강화 소비자 불만,경제
무역 적자 전환 수출 감소 영향,경제
반도체 기업 투자 확대 고용 증가,경제
물가 안정 금리 인하 기대감,경제
환율 변동 기업 실적 불확실성,경제
코스피 외국인 매도에 하락 마감,경제
경제 성장률 전망치 하향 조정,경제
부동산 대출 규제 거래 위축,경제
수출 기업 환율 상승 수혜,경제
주가 급등 투자자 매수 행렬,경제
금리 인상 예금 상품 인기,경제
소비 회복 기업 매출 증가,경제
코스피 급등 외국인 매수 확대,경제
금리 인하 기대 주식 시장 상승,경제
반도체 수출 증가 경제 성장 견인,경제
부동산 집값 상승 대출 수요 증가,경제
물가 상승 소비 위축 기업 매출 감소,경제
은행 금리 인상 예금 증가,경제
환율 급등 수입 물가 상승 압박,경제
주식 투자자 손실 코스닥 하락,경제
수출 감소 경제 성장률 하향,경제
기업 고용 확대 소비 심리 회복,경제
전국 폭염 경보 낮 최고 36도,날씨
태풍 북상 남부 지방 강풍 주의,날씨
장마 시작 전국 흐리고 비,날씨
한파 경보 아침 기온 영하 15도,날씨
미세먼지 나쁨 외출 자제 권고,날씨
주말 전국 맑음 큰 일교차 주의,날씨
폭설 예보 강원 산간 30센티,날씨
황사 유입 전국 공기질 나쁨,날씨
집중호우 호우 경보 하천 범람 주의,날씨
열대야 지속 밤 기온 25도 이상,날씨
태풍 상륙 제주 항공편 결항,날씨
기온 급락 내일 아침 서리 주의,날씨
오후 소나기 우산 챙기세요,날씨
안개 주의 아침 출근길 시야 불량,날씨
폭염 지속 전력 수요 최고치,날씨
장마 소강 주말 맑고 더위,날씨
한파 지속 수도관 동파 주의,날씨
강풍 주의보 바다 높은 파도,날씨
미세먼지 좋음 맑은 하늘 전망,날씨
폭설 뒤 빙판길 교통 주의,날씨
내일 전국 비 기온 하락,날씨
태풍 영향 전국 강한 비바람,날씨
봄비 뒤 기온 상승 포근한 날씨,날씨
폭염 경보 확대 온열 질환 주의,날씨
황사 뒤 미세먼지 농도 상승,날씨
한파 영하 10도 출근길 주의,날씨
가을 맑은 하늘 큰 일교차,날씨
집중호우 산사태 경보 발령,날씨
주말 눈 예보 교통 혼잡 우려,날씨
장마 끝 폭염 시작 전망,날씨
내일 아침 기온 영하 한파 주의,날씨
태풍 북상 주말 전국 비 예보,날씨
폭염 경보 낮 기온 35도 전망,날씨
미세먼지 나쁨 내일 황사 유입,날씨
폭설 예보 내일 출근길 교통 주의,날씨
장마 지속 전국 비 하천 범람 주의,날씨
주말 맑음 기온 상승 나들이 날씨,날씨
강풍 주의보 내일 전국 비바람,날씨
한파 경보 전국 기온 급락,날씨
오후 소나기 뒤 맑은 하늘 전망,날씨
김치찌개 맛있게 끓이는 비법,음식
서울 맛집 추천 돼지갈비 명가,음식
집에서 만드는 바삭한 치킨 레시피,음식
제철 과일 딸기 디저트 만들기,음식
된장찌개 깊은 맛 내는 재료,음식
비빔밥 색깔 고운 나물 손질법,음식
맛집 투어 부산 돼지국밥 추천,음식
라면 더 맛있게 끓이는 비법,음식
불고기 양념 황금 레시피 공개,음식
떡볶이 매운맛 조절 방법,음식
냉면 육수 시원하게 만드는 비법,음식
빵집 추천 크루아상 맛있는 집,음식
삼겹살 굽는 법 맛있는 비결,음식
파스타 소스 집에서 만들기,음식
김밥 재료 손질 말기 요령,음식
전주 맛집 비빔밥 추천 명소,음식
카페 디저트 치즈케이크 레시피,음식
잡채 당면 삶는 시간 비법,음식
초밥 맛집 신선한 재료 추천,음식
부대찌개 맛있게 끓이는 레시피,음식
호떡 반죽 바삭하게 굽는 법,음식
닭갈비 양념 레시피 매운맛 비법,음식
빙수 디저트 집에서 만들기,음식
갈비탕 국물 진하게 끓이는 비법,음식
피자 도우 집에서 만드는 레시피,음식
칼국수 맛집 추천 진한 국물,음식
감자탕 맛있게 끓이는 재료 손질,음식
만두 속 재료 맛있는 비법,음식
토스트 레시피 아침 간단 요리,음식
순두부찌개 매운맛 레시피 추천,음식
김치찌개 레시피 맛집 비법 공개,음식
집에서 만드는 떡볶이 매운맛 레시피,음식
치킨 맛집 추천 바삭한 비결,음식
된장찌개 맛있게 끓이는 재료 비법,음식
디저트 카페 추천 딸기 케이크,음식
삼겹살 맛집 추천 양념 비법,음식
라면 레시피 집에서 맛있게 끓이는 법,음식
비빔밥 맛집 추천 나물 재료,음식
파스타 레시피 소스 맛있게 만들기,음식
국밥 맛집 추천 진한 국물 비법,음식"""

MINIRNN = '''
"""minirnn — 수업용 아주 작은 RNN 문서 분류 라이브러리 (numpy 만 사용)

사용법:
    model = RNNClassifier(vocab_size, num_classes)   # 모델 만들기
    history = model.fit(train_x, train_y, epochs=20) # 학습
    model.predict(ids)                               # 추론: 번호 열 → 주제 번호
    model.predict_proba(ids)                         # 추론: 주제별 확률
    model.score(x, y)                                # 정확도
"""
import numpy as np


def softmax(scores):
    """점수 묶음을 합이 1 인 확률로 바꾼다"""
    e = np.exp(scores - scores.max())
    return e / e.sum()


class RNNClassifier:
    def __init__(self, vocab_size, num_classes, embed_dim=32, hidden_dim=64, seed=0):
        rng = np.random.default_rng(seed)
        s = 0.1                                               # 처음에는 작은 무작위 숫자로 채운다
        self.E = rng.normal(0, s, (vocab_size, embed_dim))    # 단어 번호 → 단어 벡터 (임베딩)
        self.W_x = rng.normal(0, s, (embed_dim, hidden_dim))  # 단어 벡터 → 메모
        self.W_h = rng.normal(0, s, (hidden_dim, hidden_dim)) # 이전 메모 → 메모
        self.b_h = np.zeros(hidden_dim)
        self.W_o = rng.normal(0, s, (hidden_dim, num_classes))# 마지막 메모 → 주제 점수
        self.b_o = np.zeros(num_classes)
        self.hidden_dim = hidden_dim

    # ---------- 추론: 앞으로 계산 ----------
    def forward(self, ids):
        """단어를 한 개씩 읽으며 메모(h)를 갱신하고, 마지막 메모로 주제 확률을 낸다."""
        h = np.zeros(self.hidden_dim)                         # 처음 메모는 0
        hs, xs = [h], []
        for i in ids:
            x = self.E[i]                                     # 단어 번호 → 단어 벡터
            h = np.tanh(x @ self.W_x + h @ self.W_h + self.b_h)   # 새 메모 = f(단어, 이전 메모)
            xs.append(x); hs.append(h)
        probs = softmax(h @ self.W_o + self.b_o)              # 마지막 메모 → 주제 확률
        return probs, hs, xs

    def predict_proba(self, ids):
        return self.forward(ids)[0]

    def predict(self, ids):
        return int(np.argmax(self.predict_proba(ids)))

    # ---------- 학습: 틀린 만큼 되돌아가며 고치기 ----------
    def _step(self, ids, y, lr):
        probs, hs, xs = self.forward(ids)
        loss = -np.log(probs[y] + 1e-12)                      # 교차 엔트로피: 정답 확률이 낮을수록 큰 값
        d_out = probs.copy(); d_out[y] -= 1                   # 손실의 기울기 (softmax + 교차 엔트로피)
        gW_o = np.outer(hs[-1], d_out); gb_o = d_out
        gW_x = np.zeros_like(self.W_x); gW_h = np.zeros_like(self.W_h); gb_h = np.zeros_like(self.b_h)
        gE = {}
        dh = d_out @ self.W_o.T
        for t in range(len(ids) - 1, -1, -1):                 # 시간을 거슬러 올라간다 (BPTT)
            dz = dh * (1 - hs[t + 1] ** 2)                    # tanh 의 미분
            gW_x += np.outer(xs[t], dz); gW_h += np.outer(hs[t], dz); gb_h += dz
            gE[ids[t]] = gE.get(ids[t], 0) + dz @ self.W_x.T
            dh = dz @ self.W_h.T
        for g in (gW_x, gW_h, gb_h, gW_o, gb_o):
            np.clip(g, -5, 5, out=g)                          # 기울기가 너무 커지지 않게
        self.W_x -= lr * gW_x; self.W_h -= lr * gW_h; self.b_h -= lr * gb_h
        self.W_o -= lr * gW_o; self.b_o -= lr * gb_o
        for i, g in gE.items():
            self.E[i] -= lr * np.clip(g, -5, 5)
        return loss

    def fit(self, X, y, epochs=20, lr=0.05, seed=0, verbose=True):
        """훈련 데이터를 epochs 번 돌며 매개변수를 고친다. (손실, 정확도) 기록을 돌려준다."""
        rng = np.random.default_rng(seed)
        history = []
        order = np.arange(len(X))
        for ep in range(1, epochs + 1):
            rng.shuffle(order)                                # 에포크마다 순서를 섞는다
            total = 0.0
            for i in order:
                total += self._step(X[i], y[i], lr)
            loss = total / len(X)
            acc = self.score(X, y)
            history.append((loss, acc))
            if verbose and (ep == 1 or ep % 5 == 0 or ep == epochs):
                print(f"에포크 {ep:3d}   손실 {loss:.3f}   훈련 정확도 {acc:.2f}")
        return history

    def score(self, X, y):
        """정확도 = 맞힌 개수 / 전체 개수"""
        return sum(self.predict(ids) == t for ids, t in zip(X, y)) / len(X)
'''

# ═════════════════════════ 표지 · 안내 ═════════════════════════
md(f'''
<div style="background:#0EA5A4;color:#FFFFFF;padding:34px 36px;border-radius:18px;{BOX}">
<span style="background:#FF6B5A;color:#FFFFFF;padding:4px 16px;border-radius:999px;font-weight:bold;">컴퓨팅사고 · 12주차</span>
<div style="font-size:2.3em;font-weight:bold;margin-top:14px;">인공지능 라이브러리로 문서 분류 응용 만들기</div>
<div style="font-size:1.25em;margin-top:6px;">모델은 어떻게 배우고 답하나 &nbsp;·&nbsp; 라이브러리 가져다 쓰기 &nbsp;·&nbsp; RNN 으로 뉴스 제목 분류</div>
<div style="margin-top:18px;opacity:0.9;">연세대학교 미래캠퍼스 · RC융합대학 교양기초 &nbsp;|&nbsp; 실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>
</div>
''')

md('''
# 12주차 학습 안내

지난주까지 우리는 **사람이 규칙을 쓰는** 프로그램을 만들었습니다. 점수가 90 이상이면 A, 파일이 없으면 안내문. 그런데 “이 뉴스 제목은 스포츠 기사인가?” 같은 문제는 규칙을 쓰기가 어렵습니다. 단어가 너무 많고 예외도 너무 많습니다. 오늘은 **규칙을 쓰는 대신 데이터에서 배우게 하는** 방법, 곧 인공지능 모델을 배웁니다. 그리고 남이 만들어 둔 **인공지능 라이브러리**를 가져다 뉴스 제목 분류기를 직접 만듭니다.

| 교시 | 주제 | 만드는 것 |
|:---:|:---|:---|
| **1교시** | **인공지능 모델이란** — 학습과 추론 &nbsp;·&nbsp; 문서를 숫자로 &nbsp;·&nbsp; **인공지능 라이브러리 지도**와 가져다 쓰는 법 | 숫자 한 개짜리 모델을 손으로 학습시켜 보기 |
| **2교시** | **RNN 으로 뉴스 제목 분류기 만들기** — 데이터 → 전처리 → 모델 → 학습 → 평가 → 추론 | 뉴스 제목을 스포츠 · 경제 · 날씨 · 음식으로 나누는 프로그램 |

**오늘 수업을 마치면**

1. **모델 · 매개변수 · 학습 · 손실 · 에포크 · 추론 · 과적합**이 무슨 뜻인지 말로 설명할 수 있습니다.
2. 문서가 어떻게 **숫자의 열**로 바뀌어 모델에 들어가는지 압니다.
3. 인공지능 라이브러리가 어떤 것들이 있고, `import` 해서 **데이터 → 모델 → `fit` → `predict`** 순서로 쓴다는 공통 패턴을 압니다.
4. RNN 이 “단어를 한 개씩 읽으며 메모를 갱신하는 모델”임을 알고, 라이브러리로 문서 분류기를 학습시키고 새 문장을 분류할 수 있습니다.

''' + key("이 노트북을 읽는 법", "회색 코드 셀은 <b>직접 실행</b>하는 곳입니다. 실행하기 <b>전에 결과를 먼저 예상</b>해 보세요. 오늘은 셀을 <b>위에서부터 차례로</b> 실행해야 합니다. 뒤의 셀이 앞의 셀에서 만든 데이터와 모델을 쓰기 때문입니다.<br><b style='color:#FF6B5A;'>✏️ 실습</b> 상자가 나오면 직접 코드를 작성하고, 바로 아래 <b>🔍 자가 점검</b> 셀로 확인합니다. 정답 예시는 접혀 있습니다. <b>먼저 스스로 풀어 본 뒤</b> 여세요.<br>노트북 맨 끝에 <b style='color:#FF6B5A;'>📝 과제</b>가 있습니다."))

md('''
## 1-0. 시작 전에

''' + INTRO_SITE)

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
    if isinstance(ok, str):           # 아직 풀지 않은 상태 — test 가 안내 문구를 돌려준 경우
        print(f"⏳ {name}: {ok}")
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

# ═════════════════════════ 1교시 ═════════════════════════
md(period(1, "인공지능 모델이란 — 규칙을 쓰는 대신 데이터에서 배운다",
          ["<b>규칙 쓰기 vs 배우기</b> — 왜 스팸 판별 규칙은 자꾸 깨지는가",
           "<b>학습과 추론</b> — 모델 · 매개변수 · 손실 · 에포크 · 과적합을 한 번에",
           "숫자 한 개짜리 모델을 <b>직접 학습</b>시켜 손실이 줄어드는 것을 보기",
           "<b>문서를 숫자로</b> — 토큰화 · 어휘 사전 · 번호 열",
           "<b>인공지능 라이브러리 지도</b> — 어떤 것이 있고, 어떻게 가져다 쓰나"]))

md('''
## 1-1. 규칙 쓰기 vs 배우기

지금까지 만든 프로그램은 모두 **사람이 규칙을 적은** 것입니다. 문자 메시지가 스팸인지 가리는 프로그램을 그 방식으로 만들어 봅시다. “당첨”이나 “무료”가 들어 있으면 스팸이라고 하겠습니다.

**예상해 보기** — 네 문장 가운데 몇 개를 맞힐까요? 틀리는 문장은 왜 틀릴까요?
''')

code('''
def is_spam(text):
    for word in ["당첨", "무료", "클릭"]:
        if word in text:
            return True
    return False

messages = [
    ("축하합니다 1등 당첨 지금 클릭", True),
    ("내일 수업 10시로 바뀌었어", False),
    ("무료 쿠폰 받아 가세요", True),
    ("오늘 학식 무료 시식 행사래 같이 갈래?", False),   # 친구가 보낸 평범한 문자인데…
]
for text, answer in messages:
    print(is_spam(text) == answer, "|", text)
''')

md('''
마지막 문장이 틀립니다. “무료”가 있지만 스팸이 아닙니다. 그러면 “무료 시식”은 빼라는 규칙을 더합니다. 그러면 또 다른 예외가 나옵니다. 스팸 발송자가 “무료”를 “무.료”로 바꾸면 규칙이 또 깨집니다. **규칙은 사람이 미리 생각해 낸 경우만 다룹니다.** 경우가 수만 가지면 사람이 다 쓸 수 없습니다.

그래서 방향을 바꿉니다. 규칙을 쓰지 않고, **스팸 1,000통과 정상 문자 1,000통을 보여 주고 컴퓨터가 스스로 기준을 찾게** 합니다. 이것이 **기계 학습(machine learning)** 이고, 그렇게 찾은 기준을 담은 것이 **모델(model)** 입니다.

''' + key("모델이란", "모델은 <b>입력을 받아 출력을 돌려주는 함수</b>입니다. 7주차의 함수와 같습니다. 다른 점은 하나뿐입니다. 함수 안의 규칙(숫자들)을 <b>사람이 적지 않고 데이터로 정합니다.</b> 그 숫자들을 <b>매개변수(parameter)</b> 또는 <b>가중치(weight)</b> 라고 부릅니다. 오늘 만들 RNN 모델에는 매개변수가 약 2만 개 있고, 챗GPT 같은 거대 언어 모델에는 수천억 개가 있습니다. 개수가 다를 뿐 ‘데이터로 정한 숫자들’이라는 점은 같습니다."))

md('''
## 1-2. 학습과 추론 — 용어를 한 번에

모델을 쓰는 일은 두 단계로 나뉩니다. 먼저 데이터로 매개변수를 맞춰 가는 **학습(training)**, 그다음 다 배운 모델에 새 입력을 넣어 답을 받는 **추론(inference)** 입니다.

''' + img_fig("컴퓨팅사고_12주차_학습과추론.png", "학습은 ‘틀린 정도’를 보고 매개변수를 고치는 반복이고, 추론은 고친 매개변수를 그대로 쓰는 한 번의 계산입니다.") + '''

시험공부에 빗대면 이렇습니다.

| 용어 | 뜻 | 시험공부로 말하면 |
|:---|:---|:---|
| **데이터셋**(dataset) | 입력과 정답(**레이블**, label)의 묶음 | 문제집 — 문제와 해답 |
| **훈련셋 / 테스트셋**(train / test set) | 학습에 쓰는 데이터 / 실력을 재려고 **따로 떼어 둔** 데이터 | 공부용 문제집 / 모의고사 |
| **모델**(model) | 입력 → 출력 함수. 안에 매개변수가 있다 | 학생의 머릿속 |
| **매개변수**(parameter) | 학습으로 정해지는 숫자들 | 머릿속에 자리 잡은 지식 |
| **예측**(prediction) | 모델이 내놓은 답 | 학생이 쓴 답 |
| **손실**(loss) | 예측이 정답과 **얼마나 다른지**를 재는 숫자. 작을수록 좋다 | 틀린 문제 수 |
| **학습**(training) | 손실이 줄어드는 쪽으로 매개변수를 **조금씩** 고치는 반복 | 틀린 문제를 보고 고쳐 가는 공부 |
| **에포크**(epoch) | 훈련셋 전체를 한 바퀴 도는 것 | 문제집을 처음부터 끝까지 한 번 푸는 것 |
| **추론**(inference) | 학습이 끝난 모델에 새 입력을 넣어 답을 받는 것 | 실제 시험 |
| **정확도**(accuracy) | 맞힌 개수 ÷ 전체 개수 | 점수 |
| **과적합**(overfitting) | 훈련셋은 다 맞히는데 새 데이터는 못 맞히는 상태 | 문제집 답을 **외워** 버린 학생 |

''' + ponder("생각해 보기", "① 공부용 문제집으로 시험을 보면 점수가 높게 나옵니다. 그 점수를 믿을 수 있을까요? 그래서 테스트셋은 왜 <b>따로</b> 떼어 두어야 할까요?<br>② 문제집을 100바퀴 돌면(에포크 100) 항상 더 잘하게 될까요? 어떤 일이 생길 수 있을까요?"))

md('''
## 1-3. 학습을 눈으로 보기 — 숫자 한 개짜리 모델

말로만 들으면 추상적이니 **가장 작은 모델**을 직접 학습시켜 봅시다. 매개변수가 `w` 한 개뿐인 모델입니다.

> 예측 = `w` × 입력

어떤 비밀 규칙으로 만든 데이터 네 쌍이 있습니다. `(1, 2.5)`, `(2, 5.0)`, `(3, 7.5)`, `(4, 10.0)`. 사람은 한눈에 `w = 2.5` 임을 압니다. 컴퓨터는 모릅니다. `w = 0` 에서 출발해 **틀린 만큼 조금씩** 고치게 합니다.

```
for 에포크:
    for (x, y) in 데이터:
        예측 = w * x
        오차 = 예측 - y            # 양수면 너무 크게, 음수면 너무 작게 예측한 것
        w = w - 학습률 * 오차 * x   # 오차가 줄어드는 쪽으로 조금 움직인다
```

**예상해 보기** — `w` 는 에포크가 지날수록 어떻게 변할까요? 손실은요?
''')

code('''
data = [(1, 2.5), (2, 5.0), (3, 7.5), (4, 10.0)]    # (입력, 정답)
w = 0.0                 # 매개변수 — 아무것도 모르는 상태에서 출발
lr = 0.02               # 학습률(learning rate) — 한 번에 얼마나 고칠지

for epoch in range(1, 11):
    total_loss = 0
    for x, y in data:
        pred = w * x                    # 예측
        error = pred - y                # 오차
        w = w - lr * error * x          # 오차가 줄어드는 쪽으로 w 를 조금 고친다
        total_loss += error ** 2        # 손실: 오차의 제곱을 모은다 (부호를 없애려고 제곱)
    print(f"에포크 {epoch:2d}   w = {w:.4f}   손실 = {total_loss / len(data):.4f}")
''')

md('''
`w` 가 0 → 1.24 → 1.87 → 2.18 → … → 2.50 으로 다가가고, 손실은 32 → 8 → 2 → … → 0 으로 줄어듭니다. 이것이 **학습**입니다. 정답을 알려 준 적이 없는데 데이터만으로 `w = 2.5` 를 찾았습니다.

이제 **추론**입니다. 학습된 `w` 를 그대로 써서, 본 적 없는 입력 `10` 의 답을 구합니다.
''')

code('''
print("w =", round(w, 3))
print("입력 10 의 예측 =", round(w * 10, 2))       # 데이터에 없던 입력 — 추론
''')

md(key("학습 = 손실이 줄어드는 쪽으로 매개변수를 조금씩 고치는 반복", "① <b>손실(loss)</b> — 예측과 정답의 차이를 숫자 하나로. 여기서는 오차의 제곱.<br>② <b>학습률(learning rate)</b> — 한 번에 고치는 폭. 너무 크면 널뛰고 너무 작으면 느립니다. 사람이 정해 주는 값이라 <b>하이퍼파라미터(hyperparameter)</b> 라고 합니다. 에포크 수도 하이퍼파라미터입니다.<br>③ 매개변수가 한 개든 수천억 개든 <b>같은 반복</b>입니다. 라이브러리는 이 반복을 대신 돌려 주고, `오차 * x` 자리의 계산(기울기)을 자동으로 구해 줍니다.") +
   fold("왜 ‘오차 × x’ 만큼 고칠까 — 기울기(gradient)", "손실 = (w·x − y)² 을 w 에 대해 미분하면 2·(w·x − y)·x, 곧 <b>오차 × x</b> 에 비례합니다. 이것이 ‘손실이 가장 가파르게 커지는 방향’(기울기)이고, 그 <b>반대</b>로 움직이면 손실이 줄어듭니다. 이 방법을 <b>경사 하강법(gradient descent)</b> 이라고 합니다. 안개 낀 산에서 발밑의 경사만 보고 내려가는 것과 같습니다. 미분을 몰라도 됩니다. 라이브러리가 모든 매개변수의 기울기를 자동으로 계산해 줍니다(자동 미분, autograd). 교양 수업에서는 ‘틀린 만큼, 틀린 방향의 반대로’까지만 기억하면 충분합니다."))

practice("✏️ 실습 1-1", "학습률을 바꿔 보기", "약 4분",
         "위 학습 코드를 그대로 가져와 <b>학습률 `lr` 을 `0.005` 로</b>, 에포크를 `40` 으로 바꿔 돌려 보세요. 마지막 `w` 가 변수 `w` 에 남아 있어야 합니다.<br>예상해 보기: 학습률을 4분의 1로 줄이면 2.5 에 다가가는 속도는 어떻게 될까요? 10 에포크만 돌리면 어디쯤일까요?<br>(도전) `lr = 0.3` 과 `lr = 0.5` 로도 돌려 보세요. 무슨 일이 생기나요? — 0.3 은 2.5 를 사이에 두고 왔다 갔다 하고, 0.5 는 숫자가 폭발합니다. 이것이 ‘학습률이 너무 크면 널뛴다’입니다. (이 데이터에서는 `lr` 이 0.25 를 넘으면 널뛰기 시작합니다.)",
         '''
data = [(1, 2.5), (2, 5.0), (3, 7.5), (4, 10.0)]
w = 0.0
lr = 0.005           # 여기를 바꿨습니다

# 여기에 학습 반복을 쓰세요 (에포크 40번)


print("w =", round(w, 4))
''',
         '"아직 학습 반복을 쓰지 않았습니다 (w 가 처음 값 0.0 그대로입니다)" if w == 0.0 else abs(w - 2.5) < 0.05',
         '''
data = [(1, 2.5), (2, 5.0), (3, 7.5), (4, 10.0)]
w = 0.0
lr = 0.005

for epoch in range(1, 41):
    for x, y in data:
        pred = w * x
        error = pred - y
        w = w - lr * error * x

print("w =", round(w, 4))        # 2.49xx — 학습률이 작으니 더 많은 에포크가 필요합니다
''', raises=False)

md('''
## 1-4. 문서를 숫자로 — 토큰화와 어휘 사전

모델은 숫자만 계산합니다. 그런데 우리가 다룰 입력은 “손흥민 두 골 폭발 토트넘 역전승” 같은 **글**입니다. 글을 숫자로 바꾸는 단계가 필요합니다. 두 단계입니다.

1. **토큰화(tokenization)** — 글을 조각(토큰)으로 나눕니다. 오늘은 가장 단순하게 **띄어쓰기**로 나눕니다.
2. **어휘 사전(vocabulary)** — 토큰마다 **번호**를 매깁니다. 처음 보는 토큰이 나올 때마다 새 번호를 줍니다.

**예상해 보기** — 아래 세 문장에서 번호는 몇 개가 생길까요? “대표팀”은 몇 번일까요?
''')

code('''
sentences = ["한국 야구 대표팀 결승 진출", "축구 대표팀 평가전 승리", "농구 대표팀 결승 진출"]

vocab = {"<unk>": 0}                 # 0번은 ‘모르는 단어’ 자리로 비워 둡니다
for sentence in sentences:
    for word in sentence.split():        # 토큰화 — 띄어쓰기로 나눈다
        if word not in vocab:
            vocab[word] = len(vocab)     # 처음 보는 단어 → 다음 번호

print(vocab)
print("어휘 수:", len(vocab))
''')

md('''
이제 문장은 **번호의 열**이 됩니다. 사전에 없는 단어는 `<unk>`(unknown) 의 번호 0 으로 바꿉니다.
''')

code('''
def encode(sentence, vocab):
    return [vocab.get(word, 0) for word in sentence.split()]     # 없는 단어는 0

print(encode("한국 야구 대표팀 결승 진출", vocab))
print(encode("농구 대표팀 월드컵 승리", vocab))     # "월드컵" 은 사전에 없다 → 0
''')

md(key("문서 → 번호의 열", "① 토큰화로 나누고, 어휘 사전으로 번호를 매깁니다. 모델에는 이 <b>번호의 열</b>이 들어갑니다.<br>② 사전은 <b>훈련셋으로만</b> 만듭니다. 테스트셋 단어까지 넣으면 ‘모의고사 문제를 미리 본’ 셈이 됩니다.<br>③ 사전에 없는 단어는 모두 `<unk>` 입니다. 모델은 그 단어에 대해 <b>아무것도 모릅니다.</b> 2교시에서 이것이 실제로 어떤 문제를 일으키는지 봅니다.") +
   fold("실제 서비스의 토큰화는 더 정교합니다", "띄어쓰기 토큰화는 한국어에서 ‘대표팀’ · ‘대표팀이’ · ‘대표팀의’ 를 모두 다른 단어로 봅니다. 실제로는 조사를 떼는 <b>형태소 분석</b>(KoNLPy 등)이나, 자주 나오는 글자 조각으로 나누는 <b>서브워드 토큰화</b>(BPE, SentencePiece — 챗GPT 류가 쓰는 방식)를 씁니다. 그러면 처음 보는 단어도 아는 조각들로 쪼개져 `<unk>` 가 거의 없어집니다. 원리는 오늘 것과 같습니다. ‘조각으로 나누고 번호를 매긴다’."))

practice("✏️ 실습 1-2", "어휘 사전 만들기", "약 4분",
         "문장 리스트 `docs` 로 어휘 사전 `my_vocab` 을 만드세요. 위 셀과 같은 방식입니다(`<unk>` 가 0번, 처음 나온 순서대로 번호). 그리고 `\"금리 인하 주가 상승\"` 을 `encode()` 한 결과를 `ids` 에 넣으세요.<br>예상해 보기: `\"주가\"` 는 사전에 없습니다. `ids` 의 셋째 값은 무엇일까요?",
         '''
docs = ["금리 인상 대출 부담 증가", "환율 급등 수출 기업 실적", "금리 인하 전망 소비 회복"]

# 여기에 my_vocab 을 만드세요


ids = encode("금리 인하 주가 상승", my_vocab)
print(my_vocab)
print(ids)
''',
         'my_vocab["<unk>"] == 0 and my_vocab["금리"] == 1 and my_vocab["회복"] == 14 and len(my_vocab) == 15 and ids == [1, 11, 0, 0]',
         '''
docs = ["금리 인상 대출 부담 증가", "환율 급등 수출 기업 실적", "금리 인하 전망 소비 회복"]

my_vocab = {"<unk>": 0}
for doc in docs:
    for word in doc.split():
        if word not in my_vocab:
            my_vocab[word] = len(my_vocab)

ids = encode("금리 인하 주가 상승", my_vocab)
print(my_vocab)
print(ids)                  # [1, 11, 0, 0] — "주가" 와 "상승" 은 모르는 단어
''')

md('''
## 1-5. 인공지능 라이브러리 지도

1-3 의 반복을 매개변수 2만 개짜리 모델에 손으로 쓰려면 수백 줄이 됩니다. 그래서 **남이 만들어 둔 라이브러리**를 가져다 씁니다. 9주차에 배운 `pip install` → `import` 가 그대로입니다. 어떤 것이 있는지, 응용을 만드는 **단계별**로 정리합니다.

| 단계 | 라이브러리 | 하는 일 |
|:---|:---|:---|
| **① 데이터 수집** | `requests`, `BeautifulSoup`, `Scrapy`, `Selenium` | 웹 페이지를 내려받고(HTTP), HTML 에서 글을 뽑아낸다(스크래핑) |
| **② 데이터 다루기** | **`numpy`**, **`pandas`** | 배열 · 행렬 계산 / 표(CSV · 엑셀) 읽고 정리하기 |
| **③ 텍스트 · 이미지 전처리** | `KoNLPy`, `spaCy`, `NLTK` / `OpenCV`, `Pillow` | 토큰화 · 형태소 분석 / 이미지 크기 조절 · 자르기 |
| **④ 고전 기계 학습** | **`scikit-learn`** | 분류 · 회귀 · 군집. 몇 줄로 모델을 만들고 `fit` · `predict` |
| **⑤ 딥러닝** | **`PyTorch`**, **`TensorFlow`**(`Keras`) | 신경망 모델 정의 · 학습 · 추론. 기울기 자동 계산, GPU 사용 |
| **⑥ 사전 학습 모델** | **`transformers`**(Hugging Face) | 남이 미리 학습해 둔 큰 모델(BERT · GPT 류)을 내려받아 바로 쓰거나 조금 더 학습 |
| **⑦ 배포** | `FastAPI`, `Flask`, `Gradio`, `Streamlit` | 학습된 모델을 웹 서비스 · 데모 화면으로 내놓는다 |

굵은 것 다섯 개가 가장 자주 만나는 이름입니다. 전부 외울 필요는 없습니다. **단계마다 이름이 있다**는 것과, 어느 것이든 **쓰는 법이 비슷하다**는 것만 기억하세요.

''' + key("라이브러리를 가져다 쓰는 공통 패턴", "<b>① 설치</b> — `pip install 이름` (PC) / 수업 사이트에서는 `import` 하는 순간 자동으로 받아옵니다.<br><b>② 가져오기</b> — `import numpy as np`, `import torch`, `from sklearn.naive_bayes import MultinomialNB`<br><b>③ 문서 읽기</b> — 공식 문서의 ‘Quickstart’ · ‘Tutorial’ 과 `help(이름)`. 9주차에서 한 그대로입니다.<br><b>④ 같은 순서로 쓰기</b> — 데이터 준비 → <b>모델 만들기</b> → <b>`fit`(학습)</b> → <b>`predict`(추론)</b> → 점수 확인. scikit-learn 도, 오늘의 `minirnn` 도, PyTorch 도 이 순서입니다. 이름이 조금씩 다를 뿐입니다.") +
   fold("PC 에서 쓸 때 — 가상환경(virtual environment)", "프로젝트마다 필요한 라이브러리 <b>버전</b>이 다릅니다. A 프로젝트는 `torch 2.1`, B 프로젝트는 `torch 1.13` 이 필요하면 한 PC 에 둘 다 깔 수 없습니다. 그래서 프로젝트마다 <b>독립된 Python 방</b>을 만듭니다. 그것이 가상환경입니다.<br>" + code_block('''
python -m venv .venv            # 가상환경 만들기 (.venv 폴더)
.venv\\Scripts\\activate          # 들어가기 (Windows)   /   source .venv/bin/activate  (Mac · Linux)
(.venv) pip install torch       # 이 방에만 설치된다
(.venv) deactivate              # 나오기''') + "프롬프트 앞에 `(.venv)` 가 붙으면 그 방 안입니다. 방마다 다른 버전을 두면 충돌이 원천적으로 사라집니다. 수업 사이트는 브라우저 안의 독립된 Python 이라 가상환경이 필요 없습니다."))

md('''
### `numpy` 한 번 더 — 모델이 하는 계산

9주차에 `numpy` 를 맛보았습니다. 오늘은 **왜 인공지능 라이브러리가 모두 `numpy` 위에 서 있는지** 봅니다. 모델이 하는 계산은 대부분 **숫자 묶음끼리의 곱셈과 덧셈**입니다. 1-3 의 `w * x` 가 숫자 한 개였다면, 진짜 모델은 숫자 수천 개짜리 묶음을 한 번에 곱합니다. `numpy` 는 그것을 **한 줄**로, 그리고 C 로 짜여 있어 **빠르게** 합니다.

**예상해 보기** — `scores` 는 어떤 주제의 점수가 가장 클까요? 확률로 바꾸면 합은 얼마일까요?
''')

code('''
import numpy as np

labels = ["스포츠", "경제", "날씨", "음식"]
h = np.array([0.8, -0.2, 0.5])                 # 모델 안의 ‘메모’ (숫자 3개짜리 묶음이라고 하자)
W = np.array([[ 2.0, -1.0,  0.0, -1.0],        # 메모 → 주제 점수로 바꾸는 매개변수 (3 × 4)
              [ 0.5,  2.0, -1.0,  0.0],
              [-1.0,  0.0,  2.0,  1.0]])

scores = h @ W                                 # @ 는 행렬곱 — 반복문 없이 한 줄
print("점수:", scores.round(2))

probs = np.exp(scores) / np.exp(scores).sum()  # softmax — 점수를 ‘합이 1 인 확률’로
print("확률:", probs.round(2), " 합 =", probs.sum().round(2))
print("예측:", labels[np.argmax(probs)])       # 가장 큰 확률의 주제
''')

md(note("@ · softmax · argmax", "`h @ W` 는 메모 숫자들과 매개변수를 곱해 더한 것입니다. 반복문으로 쓰면 12번 곱하고 더해야 합니다. 실제 모델은 이 곱셈을 수백만 번 하므로 `numpy`(그리고 GPU)가 필수입니다.<br>`softmax` 는 점수를 <b>확률</b>로 바꿉니다. 큰 점수는 더 크게, 작은 점수는 0 에 가깝게. 합이 1 이 되어 “스포츠일 확률 0.7” 처럼 읽을 수 있습니다.<br>`np.argmax` 는 가장 큰 값의 <b>자리</b>(index)를 돌려줍니다. 그 자리의 이름이 예측 주제입니다."))

practice("✏️ 실습 1-3", "점수에서 주제 고르기", "약 3분",
         "모델이 네 주제에 준 점수가 `scores2` 입니다. ① `np.exp` 로 softmax 확률 `probs2` 를 만들고 ② `np.argmax` 로 예측 주제 이름을 `best` 에 넣으세요.<br>예상해 보기: `best` 는 무엇일까요?",
         '''
import numpy as np
labels = ["스포츠", "경제", "날씨", "음식"]
scores2 = np.array([0.3, -1.0, 2.2, 0.1])

# 여기에 probs2 와 best 를 만드세요


print(probs2.round(3), best)
''',
         'abs(probs2.sum() - 1) < 1e-6 and abs(probs2[2] - 0.7618) < 0.001 and best == "날씨"',
         '''
import numpy as np
labels = ["스포츠", "경제", "날씨", "음식"]
scores2 = np.array([0.3, -1.0, 2.2, 0.1])

probs2 = np.exp(scores2) / np.exp(scores2).sum()
best = labels[np.argmax(probs2)]

print(probs2.round(3), best)          # [0.114 0.031 0.762 0.093] 날씨
''')

md(key("1교시 정리", "① 규칙을 사람이 쓰는 대신, 데이터로 모델 안의 숫자(<b>매개변수</b>)를 정하는 것이 <b>기계 학습</b>입니다.<br>② <b>학습</b> = 손실이 줄어드는 쪽으로 매개변수를 조금씩 고치는 반복. <b>에포크</b>는 훈련셋 한 바퀴. <b>추론</b> = 학습된 모델에 새 입력을 넣어 답을 받는 것.<br>③ <b>테스트셋</b>은 따로 떼어 둡니다. 훈련셋만 잘 맞히는 것이 <b>과적합</b>.<br>④ 글은 <b>토큰화 → 어휘 사전 → 번호의 열</b>로 바꿔 넣습니다. 모르는 단어는 `<unk>`.<br>⑤ 라이브러리는 단계마다 있고(`numpy` · `pandas` · `scikit-learn` · `PyTorch` · `transformers`), 쓰는 순서는 <b>데이터 → 모델 → `fit` → `predict`</b> 로 같습니다."))

md(BREAK)

# ═════════════════════════ 2교시 ═════════════════════════
md(period(2, "RNN 으로 뉴스 제목 분류기 만들기",
          ["<b>RNN</b> — 단어를 한 개씩 읽으며 메모를 갱신하는 모델",
           "<b>데이터 → 훈련셋/테스트셋 → 전처리</b> — 1교시 도구를 그대로",
           "<b>라이브러리 가져오기</b> — `import minirnn` → 모델 만들기 → `fit` → `predict`",
           "<b>평가와 추론</b> — 테스트 정확도 · 과적합 · 모르는 단어 문제 · 새 문장 분류",
           "같은 일을 <b>PyTorch</b> 로 쓰면 (참고)"]))

md(problem("뉴스 제목을 네 주제로 나누기",
           "뉴스 제목 한 줄이 들어오면 <b>스포츠 · 경제 · 날씨 · 음식</b> 가운데 하나를 답하는 프로그램을 만듭니다.<br>" +
           "<b>요구사항</b> — ① 훈련 데이터는 CSV 파일로 주어진다(`text`, `label` 두 열). ② 데이터를 일정 비율로 훈련셋과 테스트셋으로 나눈다. ③ 모델은 RNN. 손실은 교차 엔트로피. ④ GPU 없이 브라우저 안에서 돌아야 한다.") +
   think("절차 설계 — 컴퓨팅 사고로 쪼개기", "이 문제는 한 번에 풀 수 없습니다. <b>분해</b>합니다.<br>① <b>데이터 준비</b> — CSV 를 읽어 (제목, 주제) 쌍을 만든다 (11주차 파일 입출력)<br>② <b>나누기</b> — 훈련셋 80% · 테스트셋 20%<br>③ <b>전처리</b> — 어휘 사전을 만들고 제목을 번호의 열로 (1-4)<br>④ <b>모델 정의</b> — 라이브러리에서 RNN 분류기를 가져온다<br>⑤ <b>학습</b> — `fit`. 손실이 줄어드는지 본다<br>⑥ <b>평가</b> — 테스트셋 정확도<br>⑦ <b>추론</b> — 새 제목을 넣어 본다<br>각 단계가 <b>함수 한두 개</b>입니다. 인공지능 응용은 대부분 이 일곱 단계의 변주입니다."))

md('''
## 2-1. RNN — 순서를 기억하는 모델

1-5 의 `h @ W` 에서 ‘메모’ `h` 는 그냥 주어졌습니다. 진짜 모델은 그 메모를 **문장을 읽으며** 만듭니다. **순환 신경망(RNN, recurrent neural network)** 은 단어를 **한 개씩 순서대로** 읽습니다. 단어 하나를 읽을 때마다 메모 `h` 를 고칩니다. 마지막 단어까지 읽고 난 메모가 그 문장의 요약이고, 그것으로 주제 점수를 냅니다.

''' + img_fig("컴퓨팅사고_12주차_RNN펼침.png", "같은 ‘RNN 칸’을 단어 수만큼 되풀이해 쓰므로 ‘순환’입니다. 그림은 그것을 시간 순서로 펼쳐 그린 것입니다.") + '''

코드로 쓰면 6주차의 `for` 문 하나입니다. 이것이 RNN 의 전부입니다.

```python
h = 0으로 채운 메모
for 단어 in 문장:
    h = tanh(단어벡터 @ W_x + h @ W_h + b)      # 새 메모 = (이번 단어, 이전 메모) 로 계산
주제확률 = softmax(h @ W_o + b_o)
```

''' + key("RNN 을 한 줄로", "<b>이전 메모와 이번 단어로 새 메모를 만드는 일을 단어 수만큼 반복한다.</b> 그래서 ‘순서’가 반영됩니다. 메모 `h` 를 <b>은닉 상태(hidden state)</b> 라고 부릅니다. 단어 번호를 숫자 묶음(벡터)으로 바꾸는 표 `E` 는 <b>임베딩(embedding)</b> 이라고 합니다. 매개변수는 `E`, `W_x`, `W_h`, `b`, `W_o`, `b_o` 여섯 묶음이고, 전부 1-3 처럼 학습으로 정해집니다.") +
   fold("LSTM · GRU · 트랜스포머는 무엇인가", "단순 RNN 은 문장이 길어지면 앞쪽 단어를 잊습니다(기울기 소실). 메모에 ‘문’을 달아 무엇을 기억하고 잊을지 조절하는 <b>LSTM</b>(1997) 과 <b>GRU</b>(2014) 가 그래서 나왔습니다. 2017년의 <b>트랜스포머(Transformer)</b> 는 단어를 하나씩 읽는 대신 모든 단어를 <b>한꺼번에</b> 보고 서로 얼마나 관련 있는지(어텐션)를 계산합니다. 챗GPT 의 T 가 그것입니다. 오늘 배우는 ‘단어를 숫자로 → 메모 → 점수 → softmax → 손실 → 학습’은 이들 모두에 그대로 들어 있습니다."))

md('''
## 2-2. 데이터 준비 — CSV 읽기

훈련 데이터는 뉴스 제목 160개입니다(주제별 40개). 수업용으로 만든 짧은 제목들입니다. 아래 셀을 실행하면 `news.csv` 파일이 만들어집니다.
''')

code("%%writefile news.csv\n" + NEWS)

md('''
11주차에 배운 파일 읽기입니다. 표준 라이브러리 `csv` 모듈이 쉼표로 나누고 첫 줄을 열 이름으로 씁니다.

**예상해 보기** — `rows[0]` 은 어떤 모양일까요? 리스트일까요, 딕셔너리일까요?
''')

code('''
import csv

with open("news.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))          # 한 줄 → {"text": ..., "label": ...}

print(len(rows), "건")
print(rows[0])
print(rows[-1])
''')

code('''
counts = {}
for row in rows:
    counts[row["label"]] = counts.get(row["label"], 0) + 1    # 6주차 딕셔너리 세기 패턴
print(counts)
''')

md('''
## 2-3. 훈련셋과 테스트셋 나누기

160건을 섞은 뒤 앞 80%(128건)를 훈련셋, 뒤 20%(32건)를 테스트셋으로 둡니다. **섞는 이유**: 파일이 주제별로 정렬돼 있어서, 안 섞으면 테스트셋이 전부 ‘음식’이 됩니다. `random.seed(0)` 은 누가 실행해도 같은 순서로 섞이게 합니다.
''')

code('''
import random

random.seed(0)
random.shuffle(rows)                       # 제자리에서 섞는다

n_train = int(len(rows) * 0.8)
train_rows = rows[:n_train]
test_rows = rows[n_train:]
print("훈련셋", len(train_rows), "건  /  테스트셋", len(test_rows), "건")
print("훈련셋 첫 줄:", train_rows[0])
''')

practice("✏️ 실습 2-1", "테스트셋의 주제 분포", "약 3분",
         "테스트셋 `test_rows` 에 주제가 몇 건씩 들어 있는지 세어 딕셔너리 `test_counts` 에 넣으세요. 2-2 의 세기 패턴 그대로입니다.<br>예상해 보기: 32건이 네 주제에 꼭 8건씩일까요? 섞었으니 조금 다를 수 있습니다.",
         '''
# 여기에 test_counts 를 만드세요


print(test_counts)
''',
         'sum(test_counts.values()) == 32 and set(test_counts) == {"스포츠", "경제", "날씨", "음식"} and test_counts == {r["label"]: sum(1 for t in test_rows if t["label"] == r["label"]) for r in test_rows}',
         '''
test_counts = {}
for row in test_rows:
    test_counts[row["label"]] = test_counts.get(row["label"], 0) + 1

print(test_counts)
''')

md('''
## 2-4. 전처리 — 번호의 열로

1-4 에서 만든 도구를 **훈련셋에** 적용합니다. 어휘 사전은 **훈련셋으로만** 만듭니다. 주제 이름도 번호로 바꿉니다(`labels.index`).

**예상해 보기** — 테스트셋 단어 가운데 사전에 없는 단어(`<unk>`)는 몇 퍼센트쯤일까요?
''')

code('''
labels = ["스포츠", "경제", "날씨", "음식"]

vocab = {"<unk>": 0}
for row in train_rows:                       # 훈련셋으로만!
    for word in row["text"].split():
        if word not in vocab:
            vocab[word] = len(vocab)
print("어휘 수:", len(vocab))

def encode(sentence, vocab):
    return [vocab.get(word, 0) for word in sentence.split()]

train_x = [encode(row["text"], vocab) for row in train_rows]     # 번호의 열들
train_y = [labels.index(row["label"]) for row in train_rows]     # 주제 번호들
test_x = [encode(row["text"], vocab) for row in test_rows]
test_y = [labels.index(row["label"]) for row in test_rows]

print(train_rows[0]["text"], "→", train_x[0], "/ 주제", train_y[0], labels[train_y[0]])
''')

code('''
total = sum(len(ids) for ids in test_x)
unknown = sum(ids.count(0) for ids in test_x)
print(f"테스트셋 단어 {total}개 가운데 모르는 단어 {unknown}개 ({unknown / total:.0%})")
''')

md(warn("모르는 단어가 이렇게 많다", "테스트셋 단어의 40% 가까이가 `<unk>` 입니다. 띄어쓰기 토큰화 때문에 ‘대표팀’과 ‘대표팀이’가 다른 단어가 되고, 160개짜리 작은 데이터라 처음 보는 단어가 많습니다. 모델은 `<unk>` 에 대해 아무것도 모릅니다. 그런데도 분류가 되는지, 어디서 틀리는지 곧 봅니다. <b>데이터가 많을수록, 토큰화가 좋을수록</b> 이 비율이 줄어듭니다."))

md('''
## 2-5. 라이브러리 가져오기 — `minirnn`

이제 모델입니다. 수업 사이트의 Python 은 브라우저 안에서 돌아서 PyTorch 를 쓸 수 없습니다. 그래서 오늘은 **`numpy` 만으로 만든 작은 RNN 라이브러리 `minirnn`** 을 씁니다. 아래 셀이 그 라이브러리입니다. 접혀 있지만 펼쳐 볼 수 있습니다. 2-1 의 `for` 문이 `forward()` 안에 그대로 있습니다. 학습(`_step`)은 1-3 의 ‘오차 × x’ 를 매개변수 여섯 묶음에 대해 하는 것입니다. 지금 다 읽을 필요는 없습니다. **쓰는 법만** 보면 됩니다.

실행하면 `minirnn.py` 파일이 만들어집니다. 9주차에 `shapes.py` 를 만든 것과 같습니다.
''')

code("%%writefile minirnn.py\n# 📦 minirnn.py — 수업용 작은 RNN 라이브러리 (실행하면 파일이 만들어집니다 · 접힌 셀은 펼쳐 볼 수 있음)" + MINIRNN, form=True)

md('''
외부 라이브러리를 처음 만났을 때 하는 일 두 가지입니다. `import` 하고, `help` 로 쓰는 법을 읽습니다.
''')

code('''
import numpy as np                  # minirnn 이 쓰는 numpy 를 먼저 불러옵니다 (수업 사이트는 이 순간 패키지를 받아옵니다)
import minirnn

help(minirnn)                       # 모듈 맨 위 독스트링 — 쓰는 법이 적혀 있습니다
''')

md('''
## 2-6. 모델 만들기와 학습

쓰는 법을 읽었으니 패턴대로 갑니다. **모델 만들기 → `fit`**. 어휘 수와 주제 수를 알려 주면 매개변수를 작은 무작위 숫자로 채워 둡니다.

**예상해 보기** — 학습 전의 모델은 네 주제 가운데 하나를 찍는 셈입니다. 훈련 정확도가 얼마쯤 나올까요?
''')

code('''
model = minirnn.RNNClassifier(vocab_size=len(vocab), num_classes=len(labels))

print("학습 전 훈련 정확도:", round(model.score(train_x, train_y), 2))     # 찍는 수준 — 0.25 근처
print("학습 전 첫 문장 확률:", model.predict_proba(train_x[0]).round(2))  # 네 주제가 거의 같다
''')

md('''
이제 학습입니다. 훈련셋 128건을 20바퀴(에포크) 돕니다. 바퀴마다 손실과 훈련 정확도를 찍습니다.

**예상해 보기** — 손실은 어떻게 변할까요? 1-3 과 같은 모양일까요?
''')

code('''
history = model.fit(train_x, train_y, epochs=20, lr=0.05)
''')

md('''
손실이 1.38 → 0.00x 로 떨어지고 훈련 정확도가 1.00 이 됩니다. 1.38 은 우연이 아닙니다. 네 주제를 똑같이 찍을 때의 손실 −log(1/4) = 1.386 입니다. 거기서 출발해 ‘틀린 만큼 되돌아가며 고치기’를 128 × 20 번 한 결과입니다. 그래프로 봅니다.
''')

code('''
import matplotlib.pyplot as plt

losses = [loss for loss, acc in history]
accs = [acc for loss, acc in history]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3))
ax1.plot(range(1, 21), losses, marker="o", color="#FF6B5A"); ax1.set_title("loss"); ax1.set_xlabel("epoch")
ax2.plot(range(1, 21), accs, marker="o", color="#0EA5A4"); ax2.set_title("train accuracy"); ax2.set_xlabel("epoch")
plt.tight_layout(); plt.show()
''')

md('''
## 2-7. 평가 — 테스트셋으로 실력 재기

훈련 정확도 1.00 은 **문제집 점수**입니다. 떼어 둔 테스트셋으로 **모의고사**를 봅니다.

**예상해 보기** — 테스트 정확도도 1.00 일까요? 모르는 단어가 40% 였습니다.
''')

code('''
print("훈련 정확도  :", round(model.score(train_x, train_y), 2))
print("테스트 정확도:", round(model.score(test_x, test_y), 2))
''')

code('''
print("틀린 것들:")
for ids, y, row in zip(test_x, test_y, test_rows):
    pred = model.predict(ids)
    if pred != y:
        unknown = [w for w in row["text"].split() if w not in vocab]
        print(f"  {row['text']!r:40s} 정답 {labels[y]} → 예측 {labels[pred]}   모르는 단어 {unknown}")
''')

md(key("훈련 1.00 vs 테스트 0.8x — 과적합과 모르는 단어", "① 훈련셋은 다 맞히고 테스트셋은 일부 틀립니다. 모델이 훈련 제목을 <b>외운</b> 부분이 있다는 뜻입니다. 이것이 <b>과적합</b>입니다. 손실이 0.00x 까지 떨어진 것이 그 신호입니다.<br>② 틀린 제목을 보면 <b>모르는 단어</b>가 많습니다. 모델은 본 적 있는 것만 압니다. 모르는 단어가 없는데도 틀리는 제목이 있다면, 그 단어들의 <b>조합</b>을 훈련셋에서 충분히 보지 못한 것입니다. 데이터 160건의 한계입니다.<br>③ 그래도 160건으로 80% 안팎을 맞힙니다. 규칙을 한 줄도 쓰지 않았는데 말입니다. 실제 서비스는 데이터가 수만 ~ 수백만 건이라 훨씬 정확합니다.<br>④ <b>테스트 정확도가 진짜 점수</b>입니다. 훈련 정확도만 보고하는 것은 문제집 점수를 성적표에 적는 것과 같습니다."))

md('''
## 2-8. 추론 — 새 제목 분류하기

마지막 단계입니다. 데이터에 없던 새 제목을 넣어 봅니다. `predict_proba` 는 네 주제의 확률을, `predict` 는 가장 큰 것의 번호를 돌려줍니다.

**예상해 보기** — 네 번째 “학교 축제 공연 성황”은 어떻게 될까요? 네 단어 모두 사전에 없습니다.
''')

code('''
new_titles = ["손흥민 결승 골 우승", "금리 인하 주가 상승", "내일 폭염 주의", "김치찌개 레시피 추천",
              "학교 축제 공연 성황"]

for title in new_titles:
    ids = encode(title, vocab)
    probs = model.predict_proba(ids)
    print(f"{title:18s} → {labels[model.predict(ids)]:4s}  확률 {probs.round(2)}   번호 {ids}")
''')

md(ponder("생각해 보기", "“학교 축제 공연 성황”은 번호가 `[0, 0, 0, 0]` 입니다. 모델에게는 ‘모르는 단어 네 개’입니다. 그런데도 어떤 주제를 <b>자신 있게</b> 답합니다. 왜 그럴까요? 이 답을 믿어도 될까요?<br>실제 서비스라면 어떻게 해야 할까요? (힌트: 확률이 고르게 퍼져 있거나 모르는 단어가 대부분이면 ‘판단 보류’를 답하게 할 수 있습니다.)"))

practice("✏️ 실습 2-2", "새 제목 분류하기", "약 4분",
         "제목 `\"야구 대표팀 결승 역전승\"` 을 `encode` → `model.predict` 로 분류해, 예측 주제 <b>이름</b>을 `pred_label` 에, 네 주제의 확률을 `pred_probs` 에 넣으세요.<br>그리고 직접 제목을 하나 지어 분류해 보세요. 사전에 있는 단어를 쓰면 잘 맞히고, 없는 단어를 쓰면 엉뚱해집니다.",
         '''
title = "야구 대표팀 결승 역전승"

# 여기에 pred_label 과 pred_probs 를 만드세요


print(pred_label, pred_probs.round(2))
''',
         'pred_label == "스포츠" and pred_label == labels[model.predict(encode("야구 대표팀 결승 역전승", vocab))] and abs(pred_probs.sum() - 1) < 1e-6 and pred_probs.argmax() == 0',
         '''
title = "야구 대표팀 결승 역전승"

ids = encode(title, vocab)
pred_label = labels[model.predict(ids)]
pred_probs = model.predict_proba(ids)

print(pred_label, pred_probs.round(2))      # 스포츠 [0.99 ...]
''')

practice("✏️ 실습 2-3", "에포크를 줄이면", "약 5분",
         "새 모델 `model_short` 를 만들어 <b>에포크 5</b>로만 학습시키고, 테스트 정확도를 `acc_short` 에 넣으세요. (`minirnn.RNNClassifier(...)` 로 새로 만들어야 합니다. `model` 을 다시 `fit` 하면 이어서 학습됩니다.)<br>예상해 보기: 20 에포크짜리 `model` 보다 테스트 정확도가 높을까요, 낮을까요? 훈련 정확도는요? 결과를 보고 ‘에포크를 늘리면 항상 좋은가’에 답해 보세요.",
         '''
# 여기에 model_short 를 만들고 5 에포크 학습시킨 뒤 acc_short 를 구하세요


print("5 에포크 테스트 정확도:", round(acc_short, 2))
''',
         'isinstance(model_short, minirnn.RNNClassifier) and abs(acc_short - model_short.score(test_x, test_y)) < 1e-9 and 0 < acc_short <= 1',
         '''
model_short = minirnn.RNNClassifier(vocab_size=len(vocab), num_classes=len(labels))
model_short.fit(train_x, train_y, epochs=5, lr=0.05)
acc_short = model_short.score(test_x, test_y)

print("5 에포크 테스트 정확도:", round(acc_short, 2))
# 훈련 정확도가 아직 1.00 이 아닌데도 테스트 정확도는 20 에포크와 비슷하거나 더 높을 수 있습니다.
# 에포크를 늘리면 훈련 손실은 계속 줄지만 테스트 정확도는 어느 순간부터 좋아지지 않습니다 — 과적합.
''')

md('''
## 2-9. 같은 일을 PyTorch 로 쓰면 (참고)

오늘 `minirnn` 으로 한 일을 실제 현장에서는 **PyTorch** 로 합니다. 아래는 같은 문제를 PyTorch 로 쓴 것입니다. 수업 사이트에서는 돌지 않습니다(PyTorch 는 브라우저용 빌드가 없습니다). PC 나 Google Colab 에서 `pip install torch` 뒤에 실행할 수 있습니다. **모양이 같다**는 것만 보세요. 모델 만들기 → 손실 → 에포크 반복 → 평가.

''' + fold("PyTorch 판 — 모델 정의 · 학습 · 평가 (PC · Colab 용)", code_block('''
import torch, torch.nn as nn

class RNNClassifier(nn.Module):                       # 9주차 상속 — nn.Module 을 물려받는다
    def __init__(self, vocab_size, num_classes, embed_dim=32, hidden_dim=64):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)   # minirnn 의 E
        self.rnn = nn.RNN(embed_dim, hidden_dim, batch_first=True)  # W_x · W_h · b 가 안에 있다
        self.fc = nn.Linear(hidden_dim, num_classes)           # W_o · b_o

    def forward(self, ids):                            # minirnn 의 forward 와 같은 일
        x = self.embedding(ids)                        # 번호 → 단어 벡터
        _, h = self.rnn(x)                             # 단어를 차례로 읽은 마지막 메모
        return self.fc(h[-1])                          # 메모 → 주제 점수 (softmax 는 손실 함수 안에서)

model = RNNClassifier(len(vocab), len(labels))
loss_fn = nn.CrossEntropyLoss()                        # 교차 엔트로피
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)   # ‘기울기 반대로 조금씩’을 대신 해 준다

for epoch in range(20):                                # 에포크
    total = 0
    for ids, y in zip(train_x, train_y):
        scores = model(torch.tensor([ids]))            # 예측
        loss = loss_fn(scores, torch.tensor([y]))      # 손실
        optimizer.zero_grad(); loss.backward()         # 기울기 자동 계산 (autograd)
        optimizer.step()                               # 매개변수 고치기
        total += loss.item()
    print(f"에포크 {epoch + 1}  손실 {total / len(train_x):.3f}")

with torch.no_grad():                                  # 추론 — 기울기 계산 끄기
    correct = sum(model(torch.tensor([ids])).argmax().item() == y for ids, y in zip(test_x, test_y))
print("테스트 정확도", correct / len(test_x))''') +
        "`loss.backward()` 한 줄이 `minirnn._step` 의 기울기 계산 전부를 대신합니다. `nn.RNN` 을 `nn.LSTM` 이나 `nn.GRU` 로 바꾸면 더 좋은 모델이 됩니다. 참고 교재(Python for AI apps 9강)는 `torchtext` 와 LSTM 을 쓴 판입니다.") +
   fold("scikit-learn 판 — RNN 없이 세 줄", code_block('''
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

vectorizer = CountVectorizer()                                   # 단어 세기 (bag of words)
clf = MultinomialNB().fit(vectorizer.fit_transform(train_texts), train_labels)   # 모델 만들기 + fit
print(clf.predict(vectorizer.transform(["손흥민 결승 골 우승"])))               # predict''') +
        "순서를 무시하고 ‘어떤 단어가 몇 번 나왔나’만 세는 고전 방법입니다. 짧은 제목 분류는 이것으로도 충분히 잘 됩니다. 단계와 쓰는 법(`fit` · `predict`)이 같다는 점을 보세요."))

md(key("2교시 정리", "① <b>RNN</b> = 이전 메모와 이번 단어로 새 메모를 만드는 일을 단어 수만큼 반복. 마지막 메모로 주제 점수.<br>② 응용은 일곱 단계 — <b>데이터 → 나누기 → 전처리 → 모델 → 학습 → 평가 → 추론</b>. 각 단계는 함수 한두 개.<br>③ 라이브러리는 <b>`import` → 모델 만들기 → `fit` → `predict`</b>. `minirnn` 도 PyTorch 도 scikit-learn 도 같은 모양.<br>④ 훈련 정확도가 아니라 <b>테스트 정확도</b>가 실력. 손실이 0 에 가까운데 테스트가 안 오르면 <b>과적합</b>.<br>⑤ 모델은 <b>본 적 있는 것만</b> 압니다. 모르는 단어가 많은 입력에는 자신 있게 틀립니다. 데이터의 양과 질이 모델의 한계를 정합니다."))

# ═════════════════════════ 주차 정리 ═════════════════════════
md('''
# 12주차 정리

| 용어 | 한 줄 | 오늘 코드에서 |
|:---|:---|:---|
| 모델 · 매개변수 | 입력 → 출력 함수. 안의 숫자를 데이터로 정한다 | `w`, `minirnn.RNNClassifier(...)` |
| 학습 · 손실 · 에포크 | 손실이 줄어드는 쪽으로 조금씩 고치는 반복. 한 바퀴 = 에포크 | `w -= lr * error * x`, `model.fit(..., epochs=20)` |
| 추론 | 학습된 모델에 새 입력을 넣어 답을 받는다 | `w * 10`, `model.predict(ids)` |
| 훈련셋 · 테스트셋 · 과적합 | 떼어 둔 테스트셋 점수가 진짜 실력 | `rows[:n_train]`, `model.score(test_x, test_y)` |
| 토큰화 · 어휘 사전 · `<unk>` | 글 → 조각 → 번호의 열 | `split()`, `vocab`, `encode()` |
| RNN · 은닉 상태 · 임베딩 | 단어를 한 개씩 읽으며 메모를 갱신 | `forward()` 의 `for` 문 |
| 라이브러리 패턴 | `import` → 모델 → `fit` → `predict` | `import minirnn`, PyTorch, scikit-learn |

''' + note("오늘 쓴 것과 실제 현장의 거리", "오늘 모델은 매개변수 약 2만 개, 데이터 160건, 브라우저에서 몇 초 학습입니다. 현장의 문서 분류 모델은 매개변수 수억 개, 데이터 수백만 건, GPU 로 몇 시간입니다. 그러나 <b>단계는 같고 코드의 모양도 같습니다.</b> 1교시 표의 라이브러리 이름과 `fit` · `predict` 패턴을 기억하면, 공식 문서의 Quickstart 를 읽고 따라 할 수 있습니다. 그것이 ‘라이브러리를 가져다 쓸 줄 안다’는 뜻입니다."))

# ═════════════════════════ 과제 ═════════════════════════
FIRST_HW_CELL = len(CELLS)
md('''
# 📝 12주차 과제

''' + note("과제를 풀기 전에", "① 각 문제의 <b>🔍 자가 점검</b> 셀로 답을 스스로 확인할 수 있습니다. 과제에는 정답 예시가 없습니다.<br>② 주어진 함수 · 변수 이름을 바꾸지 마세요. 점검 셀이 그 이름으로 부릅니다.<br>③ 과제 4 · 5 는 2교시의 `vocab` · `encode` · `train_x` 등이 있어야 합니다. 맨 위부터 차례로 실행한 뒤 푸세요.<br>④ 문법을 찾아보거나 생각을 정리하는 데 AI 도구를 쓸 수 있습니다. 다만 <b>AI가 작성한 코드를 그대로 제출하는 것은 금지</b>입니다(수업계획서). 제출한 코드는 스스로 설명할 수 있어야 합니다."))

practice("📝 과제 1", "토큰화 함수", "",
         "`tokenize(text)` — 문장을 띄어쓰기로 나누되, 각 조각 끝의 문장 부호 `.` `,` `!` `?` 를 떼고, 빈 조각은 버린 리스트를 돌려줍니다.<br>힌트: `word.strip(\".,!?\")`. 떼고 나서 빈 문자열이면 넣지 않습니다.<br>`tokenize(\"손흥민 두 골, 토트넘 역전승!\")` → `[\"손흥민\", \"두\", \"골\", \"토트넘\", \"역전승\"]`",
         '''
# 여기에 함수를 정의하세요


print(tokenize("손흥민 두 골, 토트넘 역전승!"))
print(tokenize("내일  비 ... 기온 하락?"))
''',
         'tokenize("손흥민 두 골, 토트넘 역전승!") == ["손흥민", "두", "골", "토트넘", "역전승"] and tokenize("내일  비 ... 기온 하락?") == ["내일", "비", "기온", "하락"] and tokenize("") == [] and tokenize("a, b. c!") == ["a", "b", "c"]',
         '''
def tokenize(text):
    tokens = []
    for word in text.split():
        word = word.strip(".,!?")
        if word:                        # "..." 처럼 부호만 있던 조각은 빈 문자열이 된다 → 버림
            tokens.append(word)
    return tokens

print(tokenize("손흥민 두 골, 토트넘 역전승!"))
print(tokenize("내일  비 ... 기온 하락?"))
''', raises=True, show_answer=False)

practice("📝 과제 2", "어휘 사전 함수", "",
         "`build_vocab(sentences)` — 문장 리스트로 어휘 사전 딕셔너리를 만들어 돌려줍니다. `\"<unk>\"` 가 0번, 나머지는 **처음 나온 순서대로** 1, 2, 3, …. 토큰화는 과제 1 의 `tokenize` 를 쓰세요.<br>`build_vocab([\"금리 인상, 대출 부담\", \"금리 인하!\"])` → `{\"<unk>\": 0, \"금리\": 1, \"인상\": 2, \"대출\": 3, \"부담\": 4, \"인하\": 5}`",
         '''
# 여기에 함수를 정의하세요


print(build_vocab(["금리 인상, 대출 부담", "금리 인하!"]))
''',
         'build_vocab(["금리 인상, 대출 부담", "금리 인하!"]) == {"<unk>": 0, "금리": 1, "인상": 2, "대출": 3, "부담": 4, "인하": 5} and build_vocab([]) == {"<unk>": 0} and len(build_vocab(["a a a", "b."])) == 3',
         '''
def build_vocab(sentences):
    vocab = {"<unk>": 0}
    for sentence in sentences:
        for word in tokenize(sentence):
            if word not in vocab:
                vocab[word] = len(vocab)
    return vocab

print(build_vocab(["금리 인상, 대출 부담", "금리 인하!"]))
''', raises=True, show_answer=False)

practice("📝 과제 3", "정확도 함수", "",
         "`accuracy(predictions, answers)` — 예측 리스트와 정답 리스트를 받아 **맞힌 비율**을 실수로 돌려줍니다. 두 리스트 길이는 같습니다. 빈 리스트면 `0.0`.<br>힌트: `zip` 으로 짝지어 같은 것을 셉니다. 6주차 세기 패턴.<br>`accuracy([0, 1, 2, 2], [0, 1, 1, 2])` → `0.75`",
         '''
# 여기에 함수를 정의하세요


print(accuracy([0, 1, 2, 2], [0, 1, 1, 2]))
''',
         'abs(accuracy([0, 1, 2, 2], [0, 1, 1, 2]) - 0.75) < 1e-9 and accuracy([], []) == 0.0 and abs(accuracy(["a", "b"], ["a", "b"]) - 1.0) < 1e-9 and abs(accuracy([1, 1, 1], [0, 0, 1]) - 1 / 3) < 1e-9',
         '''
def accuracy(predictions, answers):
    if not predictions:
        return 0.0
    correct = 0
    for p, a in zip(predictions, answers):
        if p == a:
            correct += 1
    return correct / len(predictions)

print(accuracy([0, 1, 2, 2], [0, 1, 1, 2]))      # 0.75
''', raises=True, show_answer=False)

practice("📝 과제 4", "테스트셋 예측 모아 보기", "",
         "2교시의 `model` 로 테스트셋 `test_x` 전체를 예측한 번호 리스트를 `test_preds` 에 넣고, 과제 3 의 `accuracy` 로 `test_y` 와 비교한 값을 `test_acc` 에 넣으세요.<br>`test_acc` 는 2-7 의 `model.score(test_x, test_y)` 와 같은 값이어야 합니다. 라이브러리의 `score` 가 안에서 하는 일을 직접 해 보는 것입니다.",
         '''
# 여기에 test_preds 와 test_acc 를 만드세요


print(test_preds)
print(round(test_acc, 3))
''',
         'test_preds == [model.predict(ids) for ids in test_x] and abs(test_acc - model.score(test_x, test_y)) < 1e-9',
         '''
test_preds = [model.predict(ids) for ids in test_x]
test_acc = accuracy(test_preds, test_y)

print(test_preds)
print(round(test_acc, 3))
''', raises=True, show_answer=False)

practice("📝 과제 5", "다섯 번째 주제 추가하기 (도전)", "",
         "‘과학’ 주제의 뉴스 제목을 **10개 이상** 직접 지어 2교시 데이터에 더하고, 다섯 주제짜리 모델을 새로 학습시키세요. 제목은 짧게(단어 4 ~ 6개), 과학 느낌의 단어(우주 · 로켓 · 실험 · 연구 · 발견 · 유전자 · 백신 …)가 서로 겹치게 지으세요.<br>만들 것: ① `labels5` — 다섯 주제 이름 리스트(`labels + [\"과학\"]`). ② `rows5` — 2교시 `rows` 에 `{\"text\": ..., \"label\": \"과학\"}` 10개 이상을 더한 리스트. ③ `rows5` 전체로 어휘 사전 `vocab5` 와 번호 열 `x5`, 주제 번호 `y5` 를 만들고 ④ `model5` 를 `minirnn.RNNClassifier(len(vocab5), 5)` 로 만들어 20 에포크 학습. ⑤ 과학 제목을 하나 지어 `model5.predict` 가 `4`(과학)를 내는지 확인.<br>점검 기준: 과학 제목 10개 이상, 주제 5개, 훈련 정확도 0.9 이상.",
         '''
labels5 = labels + ["과학"]
science = [
    # 여기에 과학 제목 10개 이상을 문자열로 쓰세요
]

# 여기에 rows5, vocab5, x5, y5, model5 를 만들고 학습시키세요


print("과학 제목 수:", len(science), " 훈련 정확도:", round(model5.score(x5, y5), 2))
''',
         'len(science) >= 10 and len(labels5) == 5 and len(rows5) == len(rows) + len(science) and isinstance(model5, minirnn.RNNClassifier) and model5.W_o.shape[1] == 5 and model5.score(x5, y5) >= 0.9',
         '''
labels5 = labels + ["과학"]
science = [
    "로켓 발사 성공 우주 탐사 시작", "화성 탐사선 착륙 성공 연구", "유전자 연구 새 치료법 발견",
    "백신 임상 실험 결과 발표", "우주 망원경 새 은하 발견", "연구팀 신약 실험 성공 발표",
    "달 탐사 로켓 발사 연구 성공", "유전자 실험 질병 원인 발견", "우주 정거장 실험 결과 공개",
    "백신 연구 새 기술 발견 발표", "로켓 재사용 실험 성공 우주", "연구팀 유전자 치료 임상 시작",
]
rows5 = rows + [{"text": t, "label": "과학"} for t in science]

vocab5 = {"<unk>": 0}
for row in rows5:
    for word in row["text"].split():
        if word not in vocab5:
            vocab5[word] = len(vocab5)
x5 = [encode(row["text"], vocab5) for row in rows5]
y5 = [labels5.index(row["label"]) for row in rows5]

model5 = minirnn.RNNClassifier(len(vocab5), 5)
model5.fit(x5, y5, epochs=20, lr=0.05)
print(labels5[model5.predict(encode("우주 로켓 실험 성공", vocab5))])     # 과학

print("과학 제목 수:", len(science), " 훈련 정확도:", round(model5.score(x5, y5), 2))
''', raises=True, show_answer=False)

md(key("제출 전 확인", "① 맨 위 `▶ 먼저 실행하세요` 셀부터 과제 셀까지 <b>위에서부터 차례로</b> 실행해, 과제 1 ~ 5 의 자가 점검이 모두 ✅ 인지 확인합니다.<br>② 메뉴에서 `File → Download` 로 노트북 파일(`.ipynb`)을 내려받습니다.<br>③ 내려받은 파일을 LearnUs 공지에 따라 제출합니다."))


# ───────────────────────── 노트북 조립 ─────────────────────────
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
    cells = [("markdown", "# 컴퓨팅사고 12주차 과제 — 정답 예시 (교수용)\n\n**학생에게 배포하지 않는 파일입니다.** 수업용 노트북 `" + MAIN_NB + "` 맨 끝 ‘12주차 과제’의 정답 예시입니다. 과제 4 · 5 는 2교시의 데이터 · 사전 · 모델이 있어야 하므로, 아래 첫 코드 셀들에 2교시 흐름을 복사해 두었습니다. (`minirnn.py` 와 `news.csv` 는 수업 노트북의 셀로 먼저 만들어 두거나 같은 폴더에 두세요.)", {})]
    cells.append(("code", '''
import csv, random
import minirnn

with open("news.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
random.seed(0); random.shuffle(rows)
n_train = int(len(rows) * 0.8)
train_rows, test_rows = rows[:n_train], rows[n_train:]
labels = ["스포츠", "경제", "날씨", "음식"]
vocab = {"<unk>": 0}
for row in train_rows:
    for word in row["text"].split():
        if word not in vocab:
            vocab[word] = len(vocab)
def encode(sentence, vocab):
    return [vocab.get(word, 0) for word in sentence.split()]
train_x = [encode(r["text"], vocab) for r in train_rows]; train_y = [labels.index(r["label"]) for r in train_rows]
test_x = [encode(r["text"], vocab) for r in test_rows]; test_y = [labels.index(r["label"]) for r in test_rows]
model = minirnn.RNNClassifier(vocab_size=len(vocab), num_classes=len(labels))
history = model.fit(train_x, train_y, epochs=20, lr=0.05)
print("테스트 정확도:", model.score(test_x, test_y))
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
        save(to_nb(CELLS, "w12"), os.path.join(DEST, MAIN_NB))
        save(to_nb(hw_solution_cells(), "w12h"), os.path.join(DEST, HW_SOL))
        print("saved:", MAIN_NB, "/", HW_SOL)

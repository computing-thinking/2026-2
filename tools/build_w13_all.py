# 컴퓨팅사고 13주차 — 1교시(언어모델) + 2교시(AI 프로젝트 오리엔테이션) 합본 슬라이드
# build_w13_slides.py 와 build_w13_orient_slides.py 를 한 프레젠테이션에 차례로 실행하고 쪽번호를 다시 매긴다.
# 두 스크립트는 그대로 두고(각각 단독 실행 가능), 이 파일이 둘을 읽어 합친다.
# 사용: python tools/build_w13_all.py <출력.pptx>
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
PARTS = ["build_w13_slides.py", "build_w13_orient_slides.py"]


def body(path, first):
    """스크립트에서 슬라이드를 만드는 부분만 남긴다.
    첫 파일: 끝의 '쪽번호 + 저장' 블록만 뗀다.
    둘째 파일: prs 를 새로 만드는 줄들(prs = ... ~ slides = [])도 떼어 같은 prs 를 쓰게 한다."""
    src = open(path, encoding="utf-8").read()
    src = src[:src.index("# 쪽번호")]
    if not first:
        a = src.index("prs = Presentation()")
        b = src.index("slides = []", a) + len("slides = []")
        src = src[:a] + src[b:]
    return src.replace("OUT = sys.argv[1]", "")


ns = {"__name__": "__w13_all__"}
for i, name in enumerate(PARTS):
    code = body(os.path.join(HERE, name), first=(i == 0))
    exec(compile(code, name, "exec"), ns)
    print(name, "→", len(ns["slides"]), "장까지")

prs, slides, text, GRAY = ns["prs"], ns["slides"], ns["text"], ns["GRAY"]
N = len(slides)
for i, s in enumerate(slides):
    text(s, f"{i + 1}/{N}", 12.2, 7.05, 0.9, 0.3, size=10, color=GRAY, align="right", name="쪽번호")
prs.save(OUT)
print("saved", OUT, N, "slides")

"""10주차 풀이판에서 3교시(문제 4·5) 풀이를 뺀 판을 만든다.

수업 진도에 맞춰 1·2교시 풀이만 먼저 공개할 때 쓴다. 생성 파일 이름은 원본과 같고
content/sol/ 에 덮어쓴다. 3교시까지 공개할 때는 강의자료 폴더의 원본을 다시 복사하면 된다.

    python tools/strip_w10_p3.py
"""
import hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "컴퓨팅사고_10주차_알고리듬_풀이.ipynb")
DST = os.path.join(HERE, "..", "content", "sol", "컴퓨팅사고_10주차_알고리듬_풀이.ipynb")

NOTE = (
    '<div style="background:#F3F4F6;color:#1F2937;border-left:6px solid #6B7280;padding:12px 18px;'
    'border-radius:8px;margin:8px 0;line-height:1.7;box-sizing:border-box;max-width:100%;overflow-wrap:anywhere;width:auto;">'
    '<b style="color:#6B7280;">📎 3교시(문제 4 · 5) 풀이는 아직 없습니다</b><br>'
    '쾨니히스베르크의 다리와 미로 최단 경로는 수업에서 다룬 뒤 이 노트북에 추가됩니다. '
    '그때까지는 수업용 노트북의 🤔 상자를 보며 직접 생각해 보세요.</div>'
)

with open(SRC, encoding="utf-8") as f:
    nb = json.load(f)
cells = nb["cells"]
src = lambda c: "".join(c["source"])

start = next(i for i, c in enumerate(cells) if src(c).startswith("# 3교시"))
end = next(i for i, c in enumerate(cells) if src(c).startswith("# 10주차 정리"))
assert start < end and "실습 3-3" in src(cells[end - 1])

note = {"cell_type": "markdown", "id": hashlib.md5(NOTE.encode()).hexdigest()[:8],
        "metadata": {}, "source": NOTE}
nb["cells"] = cells[:start] + [note] + cells[end:]

# 주차 정리에서 3교시 답을 드러내는 줄을 뺀다
summary = nb["cells"][-1]
s = src(summary)
drops = [
    r"\| \*\*그래프 모델링\*\*[^\n]*\n",
    r"\| \*\*그래프\*\*[^\n]*\n",
    r"\| \*\*오일러 경로\*\*[^\n]*\n",
    r"\| \*\*BFS\*\*[^\n]*\n",
    r"\| `KeyError`[^\n]*\n",
]
for d in drops:
    s, k = re.subn(d, "", s)
    assert k == 1, d
for old, new in [
    ("생각의 틀은 넷입니다", "생각의 틀은 넷입니다(그래프 모델링은 3교시 풀이와 함께)"),
    (" · `visited` 없는 그래프 탐색", ""),
    ("`neighbors` 에서 범위 검사 누락 · ", ""),
]:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
summary["source"] = s

guide = nb["cells"][1]
g = src(guide)
assert "다섯 문제에 대해" in g
guide["source"] = g.replace("다섯 문제에 대해", "다섯 문제 가운데 1 · 2교시의 세 문제에 대해")

text = json.dumps(nb, ensure_ascii=False, indent=1).replace("\r\n", "\n").replace("\n", "\r\n") + "\r\n"
with open(DST, "w", encoding="utf-8", newline="") as f:
    f.write(text)
print(f"{len(cells)} → {len(nb['cells'])} 셀, 저장: {os.path.normpath(DST)}")

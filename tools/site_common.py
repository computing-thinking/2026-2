# 수업 사이트(JupyterLite)용 노트북 변환에 공통으로 쓰는 문구와 함수
import hashlib, json, os

SITE = "https://computing-thinking.github.io/2026-2"

INTRO_SITE = """**① 수업 사이트에서 열기** — 이 노트북은 LearnUs에 올린 **수업 사이트 링크**로 엽니다. 설치도 로그인도 필요 없습니다. 다른 곳(Google Colab 등)에서 열면 자가 점검 도구가 동작하지 않습니다.

**② 작업 내용은 이 브라우저에만 저장됩니다** — 다른 기기나 다른 브라우저에서는 보이지 않고, 브라우저 데이터를 지우면 사라집니다. 수업이 끝나면 메뉴에서 `File → Download` 로 파일을 내려받으세요. **파일이 내 손에 있어야 저장된 것입니다.** (PC: 다운로드 폴더, 아이패드: ‘파일’ 앱)

**③ 처음 상태로 되돌리기** — `File → Open…` 으로 파일 목록을 열어 이 노트북을 삭제한 뒤 새로고침하면 원본을 다시 받아 옵니다. 삭제 전에 ②로 내려받아 두세요.

**④ 아이패드** — Safari 일반 탭에서 여세요(사생활 보호 탭에서는 저장이 안 됩니다). 셀 실행은 툴바의 **▶** 버튼, 들여쓰기는 **스페이스 4칸**입니다."""

CHECK_PREFIX = '''#@title ▶ 먼저 실행하세요 — 자가 점검 도구 준비
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
'''

OLD_CHECK_HEAD = '''#@title ▶ 먼저 실행하세요 — 자가 점검 도구 준비
def check(name, test):
    """실습 답을 확인하는 도구입니다. 수정하지 마세요."""
    try:
        ok = test()
'''

BANNER_OLD = "Google Colab 실습 노트북</div>"
BANNER_NEW = "실습 노트북 — 수업 사이트(JupyterLite)에서 엽니다</div>"


def load(path):
    with open(path, encoding="utf-8", newline="") as f:
        return json.loads(f.read())


def save(nb, path):
    text = json.dumps(nb, ensure_ascii=False, indent=1) + "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\n", "\r\n"))


def src(cell):
    return "".join(cell["source"])


def set_src(cell, text):
    lines = text.split("\n")
    cell["source"] = [ln + "\n" for ln in lines[:-1]] + [lines[-1]]


def replace_once(nb, old, new, where=None):
    """노트북 전체에서 old 가 정확히 한 번 나오는지 확인하고 바꾼다."""
    hits = [c for c in nb["cells"] if old in src(c)]
    assert len(hits) == 1, f"{len(hits)}번 발견: {old[:50]!r}"
    c = hits[0]
    assert src(c).count(old) == 1
    set_src(c, src(c).replace(old, new))


def finalize(nb):
    nb["metadata"]["kernelspec"] = {"display_name": "Python 3", "name": "python"}
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            c["outputs"] = []
            c["execution_count"] = None
            if src(c).startswith("#@title ▶ 먼저 실행하세요"):
                c["metadata"].setdefault("jupyter", {})["source_hidden"] = True
    return nb


def new_id(seed):
    return hashlib.md5(seed.encode("utf-8")).hexdigest()[:8]

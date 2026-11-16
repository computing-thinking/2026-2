import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 12주차 노트북 검증 — 두 번 실행한다 (파일을 만드는 셀이 있으므로 임시 폴더로 옮겨서)
#   (1) 배포 상태 그대로: 자가 점검이 전부 ⏳(아직 변수 없음)이어야 한다
#   (2) 정답을 넣고: 자가 점검이 전부 ✅ 이어야 한다
# %%writefile 셀은 임시 폴더에 파일을 쓰고 거기서 import 한다. -v 로 각 셀의 출력도 표시.
import contextlib, importlib, io, random, sys, tempfile, time
import matplotlib
matplotlib.use("Agg")
import build_w12 as B

sys.stdout.reconfigure(encoding="utf-8")
check_names = {chk: name for name, sol, chk in B.PRACTICES}
solutions = {chk: sol for name, sol, chk in B.PRACTICES}
VERBOSE = "-v" in sys.argv
WORK = tempfile.mkdtemp(prefix="w12_")


def writefile(src):
    first, body = src.split("\n", 1)
    name = first.split()[1]
    with open(os.path.join(WORK, name), "w", encoding="utf-8") as f:
        f.write(body)
    return f"Writing {name}"


def run(cells, with_solutions):
    for m in ["minirnn"]:
        sys.modules.pop(m, None)
    ns = {}
    results, problems = {}, []
    for i, (ctype, src, meta) in enumerate(cells):
        if ctype != "code":
            continue
        nxt = cells[i + 1][1] if i + 1 < len(cells) else ""         # 작성용 셀 바로 뒤에 점검 셀이 온다
        if with_solutions and nxt in solutions:
            src = solutions[nxt]
        buf, err = io.StringIO(), None
        t0 = time.time()
        with contextlib.redirect_stdout(buf):
            try:
                if src.startswith("%%writefile"):
                    print(writefile(src))
                    importlib.invalidate_caches()
                else:
                    exec(compile(src, f"cell{i}", "exec"), ns)
            except BaseException as e:
                err = f"{type(e).__name__}: {e}"
        out = buf.getvalue()
        expected_err = "raises-exception" in meta.get("tags", [])
        if err and not expected_err:
            problems.append(f"cell {i}: 예상하지 못한 오류 {err}")
        if expected_err and not err and not with_solutions and "정의하세요" not in src and "만드세요" not in src:
            problems.append(f"cell {i}: 오류가 나야 하는 셀인데 나지 않음")
        if src in check_names:
            results[check_names[src]] = out.strip()
        if VERBOSE or (time.time() - t0 > 1):
            print(f"--- cell {i}" + (" [raises]" if expected_err else "") + f"  ({time.time() - t0:.2f}s)")
            if VERBOSE:
                print(out.rstrip()[:1500])
            if err:
                print("  !!", err)
    return results, problems


random.seed(0)
os.chdir(WORK)
sys.path.insert(0, WORK)
print("작업 폴더:", WORK)

print("================ 1) 배포 상태 그대로 ================")
res, prob = run(B.CELLS, False)
for k, v in res.items():
    print("  ", v)
    if "✅" in v:                     # 빈 답안은 ⏳(변수 없음) 또는 ❌(앞 셀의 같은 이름 변수) 여야 한다
        prob.append(f"{k}: 빈 답안인데 ✅")
assert len(res) == len(B.PRACTICES)
print("문제:", prob or "없음")

print("\n================ 2) 정답을 넣었을 때 ================")
res2, prob2 = run(B.CELLS, True)
for k, v in res2.items():
    print("  ", v)
    if "✅" not in v:
        prob2.append(f"{k}: 정답인데 통과하지 못함")
assert len(res2) == len(B.PRACTICES)
print("문제:", prob2 or "없음")

if prob or prob2:
    sys.exit(1)

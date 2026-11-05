import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 11주차 노트북 검증 — 세 번 실행한다 (파일을 만드는 셀이 많으므로 임시 폴더로 옮겨서)
#   (1) 생각하기 판을 배포 상태 그대로: 자가 점검이 전부 ⏳(아직 변수 없음)이어야 한다
#   (2) 생각하기 판에 정답을 넣고: 자가 점검이 전부 ✅ 이어야 한다
#   (3) 풀이판의 코드 셀을 위에서부터: 오류 없이(raises-exception 태그 셀 제외) 끝나야 한다
# 입력을 받는 셀과 %%writefile 셀은 없다. -v 로 각 셀의 출력도 표시.
import contextlib, io, random, sys, tempfile
import build_w11 as B

sys.stdout.reconfigure(encoding="utf-8")
check_names = {chk: name for name, sol, chk in B.PRACTICES}
solutions = {chk: sol for name, sol, chk in B.PRACTICES}
VERBOSE = "-v" in sys.argv


def run(cells, with_solutions):
    ns = {}
    results, problems = {}, []
    for i, (ctype, src, meta) in enumerate(cells):
        if ctype != "code":
            continue
        nxt = cells[i + 1][1] if i + 1 < len(cells) else ""         # 작성용 셀 바로 뒤에 점검 셀이 온다
        if with_solutions and nxt in solutions:
            src = solutions[nxt]
        buf, err = io.StringIO(), None
        with contextlib.redirect_stdout(buf):
            try:
                exec(compile(src, f"cell{i}", "exec"), ns)
            except BaseException as e:
                err = f"{type(e).__name__}: {e}"
        out = buf.getvalue()
        expected_err = "raises-exception" in meta.get("tags", [])
        if err and not expected_err:
            problems.append(f"cell {i}: 예상하지 못한 오류 {err}")
        if expected_err and not err and not with_solutions and "정의하세요" not in src:
            problems.append(f"cell {i}: 오류가 나야 하는 셀인데 나지 않음")
        if src in check_names:
            results[check_names[src]] = out.strip()
        if VERBOSE:
            print(f"--- cell {i}" + (" [raises]" if expected_err else ""))
            print(out.rstrip())
            if err:
                print("  !!", err)
    return results, problems


random.seed(0)
work = tempfile.mkdtemp(prefix="w11_")
os.chdir(work)
print("작업 폴더:", work)

print("================ 1) 생각하기 판 — 배포 상태 그대로 ================")
res, prob = run(B.THINK_CELLS, False)
for k, v in res.items():
    print("  ", v)
    if "⏳" not in v:
        prob.append(f"{k}: 빈 답안인데 ⏳ 가 아님")
assert len(res) == len(B.PRACTICES)
print("문제:", prob or "없음")

print("\n================ 2) 생각하기 판 — 정답을 넣었을 때 ================")
res2, prob2 = run(B.THINK_CELLS, True)
for k, v in res2.items():
    print("  ", v)
    if "✅" not in v:
        prob2.append(f"{k}: 정답인데 통과하지 못함")
assert len(res2) == len(B.PRACTICES)
print("문제:", prob2 or "없음")

print("\n================ 3) 풀이판 — 코드 셀 전부 실행 ================")
res3, prob3 = run(B.SOLVE_CELLS, False)
print("문제:", prob3 or "없음")

if prob or prob2 or prob3:
    sys.exit(1)

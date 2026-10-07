import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 6주차 노트북 검증: (1) 배포 상태 그대로 실행  (2) 정답을 넣고 실행해 자가 점검 통과 확인
import builtins, contextlib, io, random, sys, traceback
import build_w6 as B

sys.stdout.reconfigure(encoding="utf-8")
INPUTS = ["hello", "컴퓨팅사고", "q", "70", "30", "50"]
check_names = {chk: name for name, sol, chk in B.PRACTICES}
solutions = {chk: sol for name, sol, chk in B.PRACTICES}


def run(with_solutions, verbose):
    feed = iter(INPUTS)
    ns = {"input": lambda prompt="": next(feed)}
    real_randint = random.randint
    random.randint = lambda a, b: 50
    results, problems = {}, []
    cells = B.CELLS
    try:
        for i, (ctype, src, meta) in enumerate(cells):
            if ctype != "code":
                continue
            nxt = cells[i + 1][1] if i + 1 < len(cells) else ""
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
            if expected_err and not err and not with_solutions and "작성하세요" not in src:
                problems.append(f"cell {i}: 오류가 나야 하는 셀인데 나지 않음")
            if src in check_names:
                results[check_names[src]] = out.strip()
            if verbose:
                print(f"--- cell {i}" + (" [raises]" if expected_err else ""))
                print(out.rstrip())
                if err:
                    print("  !!", err)
    finally:
        random.randint = real_randint
    return results, problems


print("================ 1) 배포 상태 그대로 ================")
res, prob = run(False, True)
print("\n[자가 점검 — 아무것도 작성하지 않았을 때]")
for k, v in res.items():
    print("  ", v)
    if "✅" in v:
        prob.append(f"{k}: 빈 답안인데 통과함")
print("문제:", prob or "없음")

print("\n================ 2) 정답을 넣었을 때 ================")
res2, prob2 = run(True, False)
for k, v in res2.items():
    print("  ", v)
    if "✅" not in v:
        prob2.append(f"{k}: 정답인데 통과하지 못함")
assert len(res2) == len(B.PRACTICES)
print("문제:", prob2 or "없음")

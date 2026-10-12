import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 7주차 노트북 검증: (1) 배포 상태 그대로 실행  (2) 정답을 넣고 실행해 자가 점검 통과 확인
# %%writefile 셀은 임시 폴더에 파일을 쓰고, 그 폴더에서 import 한다.
import builtins, contextlib, importlib, io, random, sys, tempfile, traceback
import build_w7 as B

sys.stdout.reconfigure(encoding="utf-8")
INPUTS = ["50"]           # play_game(): random.randint 를 50 으로 고정하므로 한 번에 정답
MODULES = ["calc_area", "noisy", "my_utils", "text_tools"]
check_names = {chk: name for name, sol, chk in B.PRACTICES}
solutions = {chk: sol for name, sol, chk in B.PRACTICES}
WORK = tempfile.mkdtemp(prefix="w7_")
os.chdir(WORK)
sys.path.insert(0, WORK)


def writefile(src):
    first, body = src.split("\n", 1)
    name = first.split()[1]
    with open(os.path.join(WORK, name), "w", encoding="utf-8") as f:
        f.write(body)
    return f"Writing {name}"


def run(with_solutions, verbose):
    for m in MODULES:
        sys.modules.pop(m, None)
        p = os.path.join(WORK, m + ".py")
        if os.path.exists(p):
            os.remove(p)
    importlib.invalidate_caches()
    feed = iter(INPUTS)
    ns = {"input": lambda prompt="": next(feed)}
    real_randint = random.randint
    counter = iter(range(10 ** 6))
    # 게임(1~100)은 50 으로 고정해 한 번에 맞히고, 주사위(1~6)는 1 ~ 6 을 돌아가며 낸다
    random.randint = lambda a, b: 50 if b >= 50 else a + next(counter) % (b - a + 1)
    results, problems = {}, []
    cells = B.CELLS
    try:
        for i, (ctype, src, meta) in enumerate(cells):
            if ctype != "code":
                continue
            # 작성용 셀 바로 뒤에 (추가 셀 →) 점검 셀이 온다
            nxt = cells[i + 1][1] if i + 1 < len(cells) else ""
            nxt2 = cells[i + 2][1] if i + 2 < len(cells) else ""
            is_extra = src.startswith("import importlib")      # 모듈 실습의 고정 import 셀은 바꾸지 않는다
            if with_solutions and nxt in solutions and not is_extra:
                src = solutions[nxt]
            elif with_solutions and nxt2 in solutions and cells[i + 1][0] == "code" and nxt not in check_names \
                    and src.startswith("%%writefile"):
                src = solutions[nxt2]
            buf, err = io.StringIO(), None
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
            if expected_err and not err and not with_solutions and "작성하세요" not in src and "정의하세요" not in src:
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
res2, prob2 = run(True, "-v" in sys.argv)
for k, v in res2.items():
    print("  ", v)
    if "✅" not in v:
        prob2.append(f"{k}: 정답인데 통과하지 못함")
assert len(res2) == len(B.PRACTICES)
print("문제:", prob2 or "없음")

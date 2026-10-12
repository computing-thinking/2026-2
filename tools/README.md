# tools — 노트북 생성·변환 스크립트

실행은 `강의자료` 폴더 어디서든 `python tools/<스크립트>` 로 합니다. 경로는 스크립트 안에 절대 경로로 적혀 있습니다.

| 스크립트 | 역할 |
|:---|:---|
| `site_common.py` | 사이트용 공통 문구(1-0 안내 `INTRO_SITE`, Colab 감지 `CHECK_PREFIX`)와 노트북 저장 함수. 다른 스크립트가 import |
| `build_w6.py` | 6주차 노트북 + 교수용 과제 정답 생성. `--write` 로 저장(이미 있으면 중단) |
| `test_w6.py` | 6주차 코드 셀 전체 실행 + 실습·과제 15개를 빈 답안/정답으로 점검 |
| `build_w7.py` | 7주차(함수 · 모듈) 노트북 + 과제 정답 생성. `build_w6.py` 를 복제해 작성. 다음 주차는 이 파일을 복제 |
| `test_w7.py` | 7주차 검증. `%%writefile` 셀은 임시 폴더에 파일을 쓰고 거기서 import 한다. `-v` 로 정답 실행 출력도 표시 |
| `site_convert_w45.py` | 4·5주차 Colab용 원본 → 사이트용 사본으로 변환해 `content/` 에 저장 |
| `build_root.py` | `content/컴퓨팅사고_시작하기.ipynb` 생성. 새 주차는 `WEEKS` 목록에 추가 |

과제 정답은 `강의자료` 폴더에만 두고 `content/` 에는 넣지 않습니다.

## 사용자 정의 모듈(`%%writefile` → `import`) 주의

수업 사이트(JupyterLite)에서는 `%%writefile` 로 만든 `.py` 파일을 `import` 가 바로 찾지 못한다(경로 `''` 의 파일 목록 캐시가 갱신되지 않음). `importlib.invalidate_caches()` 뒤에는 찾는다.
7주차부터 `▶ 먼저 실행하세요` 셀에 import 때마다 캐시를 비우는 `_RefreshFinder` 를 `sys.meta_path` 앞에 끼워 두어 학생 코드는 평범한 `import 모듈` 로 동작한다. 파일을 고친 뒤에는 `importlib.reload(모듈)` 이 필요하다(일반 Python 과 같음). 2026-10 사이트에서 직접 확인.

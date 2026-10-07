# tools — 노트북 생성·변환 스크립트

실행은 `강의자료` 폴더 어디서든 `python tools/<스크립트>` 로 합니다. 경로는 스크립트 안에 절대 경로로 적혀 있습니다.

| 스크립트 | 역할 |
|:---|:---|
| `site_common.py` | 사이트용 공통 문구(1-0 안내 `INTRO_SITE`, Colab 감지 `CHECK_PREFIX`)와 노트북 저장 함수. 다른 스크립트가 import |
| `build_w6.py` | 6주차 노트북 + 교수용 과제 정답 생성. `--write` 로 저장(이미 있으면 중단). 7주차는 이 파일을 복제해 작성 |
| `test_w6.py` | 6주차 코드 셀 전체 실행 + 실습·과제 15개를 빈 답안/정답으로 점검 |
| `site_convert_w45.py` | 4·5주차 Colab용 원본 → 사이트용 사본으로 변환해 `content/` 에 저장 |
| `build_root.py` | `content/컴퓨팅사고_시작하기.ipynb` 생성. 새 주차는 `WEEKS` 목록에 추가 |

과제 정답은 `강의자료` 폴더에만 두고 `content/` 에는 넣지 않습니다.

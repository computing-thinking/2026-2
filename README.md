# 컴퓨팅사고 2026-2 실습 사이트

연세대학교 미래캠퍼스 교양 **컴퓨팅사고** 수업의 실습 노트북을 브라우저에서 바로 실행하는 사이트입니다.
설치와 로그인 없이 링크만 열면 됩니다. Python 은 브라우저 안에서 실행됩니다 (JupyterLite + Pyodide).

- 사이트: https://computing-thinking.github.io/2026-2/
- **학생용 시작 페이지**: https://computing-thinking.github.io/2026-2/notebooks/index.html?path=컴퓨팅사고_시작하기.ipynb
- 노트북 직접 열기: `https://computing-thinking.github.io/2026-2/notebooks/index.html?path=<노트북 파일명>` (Notebook 화면, PC · 아이패드 공용)

## 노트북 목록

| 주차 | 파일 |
|:---:|:---|
| 안내 | `컴퓨팅사고_시작하기.ipynb` |
| 4 | `컴퓨팅사고_4주차_Python기본문법1.ipynb` |
| 5 | `컴퓨팅사고_5주차_Python기본문법2.ipynb` |
| 6 | `컴퓨팅사고_6주차_Python반복문.ipynb` |

## 폴더

| 경로 | 내용 |
|:---|:---|
| `content/` | 학생에게 배포하는 노트북 (`.ipynb`) |
| `jupyter_lite_config.json`, `jupyter-lite.json`, `overrides.json` | JupyterLite 빌드 설정 |
| `.github/workflows/deploy.yml` | `main` 에 push 하면 자동으로 빌드 · 배포 |

## 노트북 갱신

1. 고친 노트북을 `content/` 에 복사
2. `git add`, `git commit`, `git push`
3. 1 ~ 2분 뒤 사이트에 반영 (Actions 탭에서 진행 상황 확인)

작성한 내용은 각자의 브라우저 안에만 저장됩니다. 보관하려면 `File → Download` 로 내려받으세요.

### 주의 — 같은 파일명으로 다시 올릴 때

학생 브라우저는 한 번 연 노트북의 사본을 저장해 두고 그것만 엽니다. 같은 파일명으로 수정본을 올려도 이미 연 학생에게는 보이지 않습니다.
수업 중 수정본을 배포할 때는 `_v2` 처럼 **파일명을 바꿔** 올리고, `컴퓨팅사고_시작하기.ipynb` 의 링크도 함께 고칩니다.

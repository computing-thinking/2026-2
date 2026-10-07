# 컴퓨팅사고 2026-2 실습 사이트

연세대학교 미래캠퍼스 교양 **컴퓨팅사고** 수업의 실습 노트북을 브라우저에서 바로 실행하는 사이트입니다.
설치와 로그인 없이 링크만 열면 됩니다. Python 은 브라우저 안에서 실행됩니다 (JupyterLite + Pyodide).

- 사이트: https://computing-thinking.github.io/2026-2/
- 노트북 열기: `https://computing-thinking.github.io/2026-2/lab/index.html?path=<노트북 파일명>`

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

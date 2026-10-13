# 뉴스레이다 · 재경부·국가데이터처판

CBS노컷뉴스 경제정책팀 김승모 기자용 보고 준비 페이지.
원본 [tolibre/news-monitor](https://github.com/tolibre/news-monitor)(김광일 기자 출입처판)에서 출입처만 바꿔 만든 판이다.

- 페이지: https://tolibre.github.io/newsradar-moef/ (→ `/live/`)
- 출입처: 재정경제부(재경부) · 국가데이터처(데이터처)
- 맨 끝 섹션: 김승모 기자 본인 기사(노컷 원문 author 메타로 판별) — 보고 양식에서 `<기처리>`로 분리
- 보고: 업무일 09:00 · 14:00 (원본과 같은 구간·화면 전환 시각)

## 코드를 직접 고치지 말 것

`news_monitor.py`·`render_page.py`·`merge_db.py`·`retitle.py`는 **`tools/make_variant.py`가 원본에서 생성**한다.
원본이 바뀌어 이쪽도 맞추려면:

```
git clone --depth 1 https://github.com/tolibre/news-monitor /tmp/nm
python tools/make_variant.py /tmp/nm .
```

생성기는 치환마다 원본에서 나와야 하는 횟수를 검사하고, 다르면 아무 파일도 쓰지 않고 멈춘다.
출입처·기자 이름·저장키를 바꾸려면 생성기의 설정값·치환 목록을 고친다.

## 원본과 다른 점

| | 원본 | 이 판 |
|---|---|---|
| 검색어 | 공정위·방미통위·과기정통부·우주항공청·CBS 등 | 재정경제부·재경부·국가데이터처·데이터처 |
| 당직·임시 키워드 | 있음 | 없음 |
| 본인 기사 섹션 | 김광일 기자 | 김승모 기자 |
| 브라우저 저장키 | `nm-live-*` | `nm-moef-*` (같은 출처 `tolibre.github.io`라 반드시 달라야 함) |
| 기기 연동(gist) | 있음 | 버튼 숨김 — GitHub 계정이 없는 사용자라 PC·폰이 따로 기억 |
| 텔레그램 실시간 알림 | 있음 | 꺼짐(비밀값 미등록 — 로그로만). 켜기 전에 소관 어휘 보강 필요 |
| digest | 하루 5회, 페이지·보존본 | 06:00 한 번 — DB 정리(90일)용, 페이지 없음 |
| 체크 기록 수확 | 있음 | 없음 |

## 운영 (cron-job.org → workflow_dispatch)

URL `https://api.github.com/repos/tolibre/newsradar-moef/actions/workflows/newsradar-moef.yml/dispatches`, POST,
헤더는 원본 잡과 같음(PAT는 이 저장소에도 Actions 읽기·쓰기 권한이 있어야 함), 시간대 Asia/Seoul.

| 잡 | 스케줄 | body |
|---|---|---|
| moef-check | `0 5-22 * * *` | `{"ref":"main","inputs":{"mode":"check"}}` |
| moef-check-precut | `25 8,13 * * 1-5` | 위와 같음 |
| moef-digest-night | `0 6 * * *` | `{"ref":"main","inputs":{"mode":"digest"}}` |
| moef-retitle | `15 */2 * * *` | `{"ref":"main","inputs":{"mode":"retitle","apply":"1","limit":"100"}}` |

Secrets: `NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`(원본과 같은 값 가능). Pages: main / docs.

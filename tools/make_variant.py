#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""뉴스레이다 재경부·국가데이터처판(김승모 기자용) 생성기.

원본(tolibre/news-monitor — 김광일 기자 출입처판)의 파일을 그대로 가져와
'출입처·바이라인·브라우저 저장키' 같은 설정만 바꿔 이 저장소에 쓴다.
코드를 손으로 갈라 두면(포크) 원본의 수정이 이쪽에 안 따라오고 두 판이 조금씩
어긋난다. 그래서 바꿀 곳을 이 파일 한 곳에 '치환 목록'으로 모았다.

  python tools/make_variant.py <원본 저장소 경로> [<출력 경로, 기본=이 저장소>]

- 치환마다 '원본에서 정확히 몇 번 나와야 하는지'를 적어 두고, 다르면 아무 파일도
  쓰지 않고 멈춘다. 원본이 바뀌어 기준 문자열이 사라졌는데 조용히 넘어가면,
  김광일 기자 설정이 섞인 판이 배포될 수 있어서다.
- 원본 쪽 파일은 읽기만 한다.
- 생성 뒤 '김광일'·'nm-live-' 같은 원본 고유 문자열이 사용자에게 보이는 자리에
  남았는지 검사한다(주석은 허용).
"""
import hashlib, os, re, shutil, sys

# ---------------------------------------------------------------- 설정값 ---
REPORTER = "김승모"                       # 노컷 원문 author 메타: 'CBS노컷뉴스 김승모 기자'
BEATS_TITLE = "재경부·기획예산처·국가데이터처·관세청"
STORE_PREFIX = "nm-moef-"                 # 브라우저 저장키 — 원본('nm-live-')과 같은 출처
                                          # (tolibre.github.io)라 반드시 달라야 한다
REPORT_ORDER_JS = "['재경부','기획예산처','국가데이터처','관세청']"

NEW_BASE_KEYWORDS = '''BASE_KEYWORDS = [
    # 뉴스레이다 재경부·국가데이터처판(tools/make_variant.py가 생성 — 직접 고치지 말 것).
    # 그룹명은 원본 당직 모드 매핑(DUTY_KEYWORD_GROUPS)을 그대로 쓴다:
    # 재정경제부·재경부 → '재경부', 기획예산처·예산처 → '기획예산처', 국가데이터처·데이터처 → '국가데이터처'.
    # 관세청은 원본에 없어 아래 KEYWORD_GROUPS 줄에서 매핑을 더한다(2026-10-14 추가).
    "재정경제부", "재경부",
    "기획예산처", "예산처",
    "국가데이터처", "데이터처",
    "관세청",
]
'''

# 관세청을 KEYWORD_GROUPS에 넣는다 — 그래야 클러스터링의 '출입처명 토큰'(CLUSTER_AGENCY_TOKENS,
# KEYWORD_GROUPS에서 유도)에 들어가 '관세청' 한 단어로 서로 다른 사안이 묶이지 않는다.
NEW_GROUPS_LINE = ("KEYWORD_GROUPS.update(DUTY_KEYWORD_GROUPS)\n"
                   "KEYWORD_GROUPS.update({'관세청': '관세청'})   # 재경부판(생성기)\n")

# (파일, 찾을 문자열 또는 정규식, 바꿀 문자열, 원본에서 나와야 하는 횟수, 정규식 여부)
NM = "news_monitor.py"
RP = "render_page.py"

REPLACEMENTS = [
    # ---- news_monitor.py: 원본 0-35(주체 출입처 배정·'전체' 탭 주체 가점·매체 가점)는 아직 끈다 ----
    # 사용자 결정(2026-10-15): 김광일판에서 먼저 써 보고 괜찮으면 재경부판에도 켠다. 켤 땐 이 세 줄을 지울 것.
    (NM, "ACTOR_ASSIGN = True\n", "ACTOR_ASSIGN = False   # 재경부판(생성기) — 김광일판 확인 뒤 켤 예정\n", 1, False),
    (NM, "LIVE_ACTOR_BONUS = 2.0\n", "LIVE_ACTOR_BONUS = 0   # 재경부판(생성기)\n", 1, False),
    (NM, 'LIVE_MEDIA_BOOST = {"*": [(LIVE_MEDIA_MAJOR, 1.0)]}\n', "LIVE_MEDIA_BOOST = {}   # 재경부판(생성기)\n", 1, False),
    # 원본 0-37(사진 설명형 제목 추가 거르기)도 김승모 기자 판 반영 때 함께 켠다.
    (NM, r"CAPTION_EXTRA = \[\n(?:    .*\n)*?\]\n", "CAPTION_EXTRA = []   # 재경부판(생성기) — 김승모판 반영 때 켤 예정\n", 1, True),
    # ---- news_monitor.py: 출입처 ----
    (NM, r"DUTY_DATES = \{\n(?:    .*\n)*?\}\n",
         "DUTY_DATES = {}   # 재경부판은 당직 모드를 쓰지 않는다(출입처가 곧 기본 검색어)\n", 1, True),
    (NM, r"BASE_KEYWORDS = \[\n(?:.*\n)*?\]\n", NEW_BASE_KEYWORDS, 1, True),
    (NM, 'TEMP_KEYWORDS = {\n    "대미투자": "2026-09-23",\n}\n',
         "TEMP_KEYWORDS = {}\n", 1, False),
    (NM, "KEYWORD_GROUPS.update(DUTY_KEYWORD_GROUPS)\n", NEW_GROUPS_LINE, 1, False),
    # ---- news_monitor.py: 바이라인(본인 기사 섹션) ----
    (NM, 'BYLINE_NAME = "김광일"', f'BYLINE_NAME = "{REPORTER}"', 1, False),
    (NM, 'BYLINE_SECTION = "김광일 기자"', f'BYLINE_SECTION = "{REPORTER} 기자"', 1, False),

    # ---- render_page.py: 보고 양식 순서 ----
    (RP, "var REPORT_ORDER = ['방미통위','공정위','과기정통부','우주항공청'];",
         f"var REPORT_ORDER = {REPORT_ORDER_JS};", 2, False),
    (RP, "출입처 순서(방미통위 → 공정위 → 과기정통부 → 우주청 → 2진)",
         "출입처 순서(재경부 → 기획예산처 → 국가데이터처 → 관세청)", 2, False),
    # ---- render_page.py: 브라우저 저장키(같은 출처의 원본 페이지와 섞이지 않게) ----
    (RP, "'nm-live-", f"'{STORE_PREFIX}", 6, False),
    # ---- render_page.py: 출입처 식별색 ----
    (RP, '[data-g="공정위"], [data-b="공정위"]', '[data-g="재경부"], [data-b="재경부"]', 1, False),
    (RP, '[data-g="과기정통부"], [data-b="과기정통부"]',
         '[data-g="국가데이터처"], [data-b="국가데이터처"]', 1, False),
    (RP, '[data-g="방미통위"], [data-b="방미통위"]', '[data-g="기획예산처"], [data-b="기획예산처"]', 1, False),
    (RP, '[data-g="우주항공청"], [data-b="우주항공청"]', '[data-g="관세청"], [data-b="관세청"]', 1, False),
    (RP, '[data-g="김광일 기자"], [data-b="김광일 기자"]',
         f'[data-g="{REPORTER} 기자"], [data-b="{REPORTER} 기자"]', 1, False),
    # ---- render_page.py: 기기 연동 숨김 ----
    # 연동은 사용자 GitHub 계정의 gist + 기기별 토큰이라 GitHub 계정이 없는 기자는 못 쓴다.
    # 버튼만 숨긴다(스크립트가 이 요소를 찾으므로 지우면 안 됨). 토큰이 없으면
    # 페이지는 api.github.com에 요청을 하나도 보내지 않는다(원본 0-26 설계).
    (RP, '<button type="button" id="sync" class="sync off"',
         '<button type="button" id="sync" class="sync off" style="display:none"', 1, False),
    # ---- render_page.py: 화면 문구 ----
    (RP, "<title>뉴스레이다</title>", f"<title>뉴스레이다 · {BEATS_TITLE}</title>", 1, False),
    (RP, "document.title = '뉴스레이다 · ' + r.title;",
         "document.title = '뉴스레이다(재경) · ' + r.title;", 1, False),
    (RP, "맨 끝 ‘김광일 기자’는", f"맨 끝 ‘{REPORTER} 기자’는", 1, False),
    (RP, "체크한 기사와 ‘여기까지 확인’은 이 기기에 저장되고, 머리줄 <b>기기 연동</b>을 켜면 다른 기기와 맞춰집니다(내 GitHub 비공개 gist). · <a href=\"../\">최신 다이제스트</a> · <a href=\"../archive/\">지난 다이제스트</a></p>",
         "체크한 기사와 ‘여기까지 확인’은 이 기기(브라우저)에만 저장됩니다 — PC와 폰은 따로 기억합니다.</p>", 1, False),
]

# 원본에서 그대로 가져오는 파일(치환 없음)
COPY_AS_IS = ["merge_db.py", "retitle.py"]

# 페이지에 남아 있으면 안 되는 문자열 — 주석(# / //)이 아닌 줄에서만 검사한다.
# (news_monitor.py는 문자열 대신 아래 EXPECT로 '실제로 import했을 때의 값'을 검사한다.
#  원본의 우주항공청·CBS 매핑·소관 어휘는 남아 있어도 검색어가 아니면 무해하다.)
FORBIDDEN = {
    RP: ["nm-live-", "김광일 기자\"", "기기 연동</b>", "방미통위 → 공정위"],
}
# 생성한 news_monitor.py를 별도 프로세스로 import해 확인할 값(당직·임시 키워드가 꺼진 날짜 기준).
EXPECT = {
    "KEYWORDS": ["재정경제부", "재경부", "기획예산처", "예산처", "국가데이터처", "데이터처", "관세청"],
    "GROUP_ORDER": ["재경부", "기획예산처", "국가데이터처", "관세청"],
    "BYLINE_NAME": REPORTER,
    "BYLINE_SECTION": f"{REPORTER} 기자",
    "ACTOR_ASSIGN": False,
    "LIVE_ACTOR_BONUS": 0,
}


def md5(b):
    return hashlib.md5(b).hexdigest()


def apply(src_dir):
    out = {}
    for fname in {r[0] for r in REPLACEMENTS}:
        with open(os.path.join(src_dir, fname), encoding="utf-8") as f:
            out[fname] = f.read()
    errors = []
    for fname, old, new, count, is_re in REPLACEMENTS:
        text = out[fname]
        found = len(re.findall(old, text)) if is_re else text.count(old)
        if found != count:
            errors.append(f"{fname}: {old[:60]!r} — {count}번이어야 하는데 {found}번")
            continue
        out[fname] = re.sub(old, lambda m: new, text) if is_re else text.replace(old, new)
    if errors:
        raise SystemExit("원본이 예상과 달라 생성을 멈춥니다(아무 파일도 쓰지 않음):\n  "
                         + "\n  ".join(errors))
    leftovers = []
    for fname, pats in FORBIDDEN.items():
        for i, line in enumerate(out[fname].splitlines(), 1):
            s = line.strip()
            if s.startswith("#") or s.startswith("//"):
                continue
            for p in pats:
                if p in line:
                    leftovers.append(f"{fname}:{i}: {p!r} — {s[:80]}")
    if leftovers:
        raise SystemExit("원본 고유 문자열이 남았습니다:\n  " + "\n  ".join(leftovers))
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = os.path.abspath(sys.argv[1])
    dst = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else
                          os.path.join(os.path.dirname(__file__), ".."))
    out = apply(src)
    # 먼저 임시 폴더에 써서 import 검사를 통과한 뒤에만 실제 위치로 옮긴다.
    import json, subprocess, tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for fname, text in out.items():
            with open(os.path.join(tmp, fname), "w", encoding="utf-8") as f:
                f.write(text)
        probe = ("import json, news_monitor as m; print(json.dumps({k: getattr(m, k) for k in %r}, "
                 "ensure_ascii=False))" % list(EXPECT))
        env = dict(os.environ, DUTY_MODE="")
        r = subprocess.run([sys.executable, "-c", probe], cwd=tmp, env=env,
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("생성본 import 실패:\n" + r.stderr[-2000:])
        got = json.loads(r.stdout.strip().splitlines()[-1])
        bad = {k: (got.get(k), v) for k, v in EXPECT.items() if got.get(k) != v}
        if bad:
            raise SystemExit(f"생성본 설정값이 예상과 다릅니다: {bad}")
    for fname, text in sorted(out.items()):
        with open(os.path.join(dst, fname), "w", encoding="utf-8") as f:
            f.write(text)
    for fname in COPY_AS_IS:
        shutil.copyfile(os.path.join(src, fname), os.path.join(dst, fname))
    for fname in sorted(list(out) + COPY_AS_IS):
        with open(os.path.join(src, fname), "rb") as a, open(os.path.join(dst, fname), "rb") as b:
            print(f"{fname:18s} 원본 {md5(a.read())} → 생성 {md5(b.read())}")


if __name__ == "__main__":
    main()

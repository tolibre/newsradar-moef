# -*- coding: utf-8 -*-
"""경제정책팀 휴일 특근(당직) 묶음 — 뉴스레이다 경제정책팀 변형판 공용 설정(0-73).

사용자(2026-10-23 01:56): "경제정책팀은 김승모 팀장과 함께 김광일, 서민선, 이승훈, 최창민 등 5명이야."
(01:59) "최창민: 국토교통부 / 이승훈: 기획예산처, 농식품부 / 김승모, 서민선, 최창민, 이승훈 판 휴일 특근에 김광일 출입처도 들어가야지."

원본(tolibre/news-monitor = 김광일판)의 당직 묶음(DUTY_KEYWORDS)은 경제정책팀 8곳(재경부·국가데이터처·기획예산처·국토부·
산업부·중기부·개인정보위·농식품부)이고 김광일 출입처는 원본의 본 섹션이라 들어 있지 않다. 변형판은 생성기가 그 자리를
이 파일의 팀 묶음(다섯 명 출입처 합침)으로 바꾼다. 각 판은 묶음 중 **자기 섹션이 아닌 그룹만** 당직으로 모은다
(원본 규칙 DUTY_ONLY_GROUPS = 당직 그룹 - GROUP_ORDER) — 그룹 이름이 각 판 섹션 이름·원본 매핑과 같아야 한다.

**이 파일은 경제정책팀 변형판 저장소마다 똑같은 사본이 있다**(newsradar-moef·newsradar-industry·newsradar-land·newsradar-budget-agri).
고치면 네 사본을 같게 바꾸고 네 생성기를 다시 돌릴 것. 원본(김광일판) 당직 묶음은 원본 news_monitor.py의 DUTY_KEYWORDS다.
"""

# (기자, [(검색어, 그룹), ...]) — 순서 = 당직 섹션 순서(사용자가 말한 순서). 검색어·그룹은 원본 매핑과 같게.
# 김광일: 'CBS'·'나이영'은 회사 기사라 빼고, '누리호'는 우주항공청 사안어(원본 0-28)라 넣는다.
# 서민선: '대미투자'는 사안어(하루 400~1,400건)라 당직 묶음에 넣지 않는다 — 산업부 검색으로 대부분 들어온다.
# 이승훈의 기획예산처는 김승모와 겹쳐 한 번만(김승모 줄).
MEMBERS = [
    ("김승모", [("재정경제부", "재경부"), ("재경부", "재경부"),
              ("국가데이터처", "국가데이터처"), ("데이터처", "국가데이터처"),
              ("기획예산처", "기획예산처"), ("예산처", "기획예산처"),
              ("관세청", "관세청")]),
    ("김광일", [("공정거래위원회", "공정위"), ("공정위", "공정위"),
              ("방송미디어통신위원회", "방미통위"), ("방미통위", "방미통위"),
              ("과학기술정보통신부", "과기정통부"), ("과기정통부", "과기정통부"), ("과기부", "과기정통부"),
              ("우주항공청", "우주항공청"), ("누리호", "우주항공청")]),
    ("서민선", [("산업통상부", "산업부"), ("산업부", "산업부"),
              ("중소벤처기업부", "중기부"), ("중기부", "중기부"),
              ("개인정보보호위원회", "개인정보위"), ("개인정보위", "개인정보위"), ("개보위", "개인정보위")]),
    ("이승훈", [("농림축산식품부", "농식품부"), ("농식품부", "농식품부")]),
    ("최창민", [("국토교통부", "국토부"), ("국토부", "국토부")]),
]

DUTY_KEYWORDS = [k for _, kws in MEMBERS for k, _g in kws]
DUTY_GROUPS = {k: g for _, kws in MEMBERS for k, g in kws}
ALL_GROUPS = []
for _k in DUTY_KEYWORDS:
    if DUTY_GROUPS[_k] not in ALL_GROUPS:
        ALL_GROUPS.append(DUTY_GROUPS[_k])


def duty_only(own_groups):
    """이 판에서 당직으로만 모을 그룹(원본 DUTY_ONLY_GROUPS 계산과 같은 순서)."""
    return [g for g in ALL_GROUPS if g not in own_groups]


def duty_keywords_block():
    body = "".join(f"    # {name}\n    " + ", ".join(f'"{k}"' for k, _ in kws) + ",\n" for name, kws in MEMBERS)
    return ("DUTY_KEYWORDS = [\n"
            "    # 경제정책팀 휴일 특근 묶음(tools/econ_team.py — 생성기가 원본 묶음 자리에 넣는다. 김광일 출입처 포함, 0-73)\n"
            + body + "]\n")


def duty_groups_block():
    body = "".join("    " + ", ".join(f'"{k}": "{g}"' for k, g in kws) + ",\n" for _, kws in MEMBERS)
    return "DUTY_KEYWORD_GROUPS = {\n" + body + "}\n"


def replacements(NM, RP):
    """경제정책팀 생성기가 REPLACEMENTS 앞에 붙이는 치환(원본 기준 문자열·횟수).
    원본 EXCLUDE_TERMS(대한체육회·스포츠공정위·모의공정위)는 그대로 둔다 — 당직으로 '공정위'를 검색하게 됐다(0-46 끔을 0-73에서 되돌림)."""
    return [
        (NM, r"DUTY_KEYWORDS = \[\n(?:.*\n)*?\]\n", duty_keywords_block(), 1, True),
        (NM, r"DUTY_KEYWORD_GROUPS = \{\n(?:.*\n)*?\}\n", duty_groups_block(), 1, True),
    ]

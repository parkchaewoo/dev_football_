"""팀 간 전술 공유 기능 통합 테스트.

테스트 시나리오:
1. 유저 2명, 팀 2개 생성
2. 팀A에 전술 저장 (공개)
3. 팀B 유저가 공개 전술 조회 → 가져오기
4. 가져온 전술이 팀B에 저장되었는지 확인
5. 예시 전술 시드 동작 확인
6. 시드 중복 실행 방지 확인
"""
import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Firebase 없이 로컬 모드로 테스트
os.environ.pop("FIREBASE_SERVICE_ACCOUNT_KEY", None)
os.environ.pop("FIREBASE_SERVICE_ACCOUNT_JSON", None)

import json
import shutil
from pathlib import Path

from services import local_store
from services.auth_service import create_or_get_user
from services.team_service import create_team, join_team_by_code, get_my_teams
from services.strategy_service import (
    save_strategy,
    get_team_strategies,
    get_public_strategies,
    get_my_strategies,
)
from services.seed_examples import seed_example_strategies
from utils.models import (
    create_default_strategy,
    strategy_to_json,
    strategy_from_json,
    strategy_from_firestore,
)


# ===== 테스트용 데이터 디렉토리 격리 =====
_TEST_DATA_DIR = Path(__file__).resolve().parent / "_test_data"


def setup():
    """테스트 전 데이터 초기화."""
    if _TEST_DATA_DIR.exists():
        shutil.rmtree(_TEST_DATA_DIR)
    _TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    # local_store의 데이터 디렉토리를 테스트용으로 교체
    local_store._DATA_DIR = _TEST_DATA_DIR


def teardown():
    """테스트 후 정리."""
    if _TEST_DATA_DIR.exists():
        shutil.rmtree(_TEST_DATA_DIR)


def test_1_create_users_and_teams():
    """유저 2명, 팀 2개 생성."""
    print("\n=== 테스트 1: 유저 & 팀 생성 ===")

    user_a = create_or_get_user("코치A")
    user_b = create_or_get_user("코치B")
    assert user_a["uid"] != user_b["uid"], "유저 UID가 달라야 함"
    print(f"  ✅ 유저A: {user_a['displayName']} (uid={user_a['uid'][:8]}...)")
    print(f"  ✅ 유저B: {user_b['displayName']} (uid={user_b['uid'][:8]}...)")

    team_a = create_team("FC알파", "테스트 팀A", user_a["uid"])
    team_b = create_team("FC베타", "테스트 팀B", user_b["uid"])
    assert team_a["id"] != team_b["id"], "팀 ID가 달라야 함"
    assert team_a.get("inviteCode"), "초대코드가 있어야 함"
    print(f"  ✅ 팀A: {team_a['name']} (code={team_a['inviteCode']})")
    print(f"  ✅ 팀B: {team_b['name']} (code={team_b['inviteCode']})")

    return user_a, user_b, team_a, team_b


def test_2_save_public_strategy(user_a, team_a):
    """팀A에 공개 전술 저장."""
    print("\n=== 테스트 2: 팀A에 공개 전술 저장 ===")

    strategy = create_default_strategy()
    strategy.name = "4-0 로테이션"
    strategy.description = "풋살 4-0 로테이션 공격 전술"
    strategy_dict = json.loads(strategy_to_json(strategy))

    sid = save_strategy(
        strategy_dict,
        user_a["uid"],
        user_a["displayName"],
        team_a["id"],
        team_a["name"],
        "public",
    )
    assert sid, "전략 ID가 반환되어야 함"
    print(f"  ✅ 전술 저장: '{strategy.name}' (id={sid[:8]}...)")

    # 팀 전술에서 확인
    team_strats = get_team_strategies(team_a["id"])
    assert len(team_strats) == 1, f"팀A에 1개 전술이 있어야 함 (실제: {len(team_strats)})"
    print(f"  ✅ 팀A 전술 수: {len(team_strats)}")

    # 공개 전술에서 확인
    pub_strats = get_public_strategies()
    assert any(s["id"] == sid for s in pub_strats), "공개 전술에 나와야 함"
    print(f"  ✅ 공개 전술에서 확인됨")

    return sid


def test_3_import_to_other_team(user_b, team_b, original_sid):
    """팀B 유저가 공개 전술을 자기 팀에 가져오기."""
    print("\n=== 테스트 3: 팀B로 전술 가져오기 (원클릭 임포트 시뮬레이션) ===")

    # 공개 전술 목록에서 원본 찾기
    pub_strats = get_public_strategies()
    original = next((s for s in pub_strats if s["id"] == original_sid), None)
    assert original, "공개 전술에서 원본을 찾아야 함"
    print(f"  ✅ 공개 전술에서 원본 발견: '{original['name']}'")

    # "⚡ 우리 팀에 가져오기" 시뮬레이션
    loaded = strategy_from_firestore(original)
    strategy_dict = json.loads(strategy_to_json(loaded))
    strategy_dict["name"] = original["name"]  # 원본 이름 유지

    new_id = save_strategy(
        strategy_dict,
        user_b["uid"],
        user_b["displayName"],
        team_b["id"],
        team_b["name"],
        "team",
    )
    assert new_id, "새 전략 ID가 반환되어야 함"
    assert new_id != original_sid, "새 ID는 원본과 달라야 함"
    print(f"  ✅ 팀B에 저장됨 (new_id={new_id[:8]}...)")

    # 팀B에서 확인
    team_b_strats = get_team_strategies(team_b["id"])
    assert len(team_b_strats) == 1, f"팀B에 1개 전술이 있어야 함 (실제: {len(team_b_strats)})"
    imported = team_b_strats[0]
    assert imported["name"] == "4-0 로테이션", "이름이 원본과 같아야 함"
    assert imported["authorName"] == user_b["displayName"], "작성자가 팀B 유저여야 함"
    assert imported["teamId"] == team_b["id"], "팀ID가 팀B여야 함"
    assert imported["visibility"] == "team", "공개범위가 team이어야 함"
    print(f"  ✅ 가져온 전술 확인:")
    print(f"     이름: {imported['name']}")
    print(f"     작성자: {imported['authorName']}")
    print(f"     팀: {imported['teamName']}")
    print(f"     공개범위: {imported['visibility']}")

    # 원본은 여전히 존재
    team_a_strats_after = get_public_strategies()
    assert any(s["id"] == original_sid for s in team_a_strats_after), "원본이 유지되어야 함"
    print(f"  ✅ 원본 전술은 그대로 유지됨")

    return new_id


def test_4_strategy_data_integrity(original_sid, imported_id):
    """가져온 전술의 포메이션 데이터가 원본과 동일한지 확인."""
    print("\n=== 테스트 4: 전술 데이터 무결성 ===")

    pub_strats = get_public_strategies()
    original = next(s for s in pub_strats if s["id"] == original_sid)
    orig_strategy = strategy_from_firestore(original)

    all_strats = local_store.get_all_docs("strategies")
    imported_doc = next(s for s in all_strats if s["id"] == imported_id)
    imp_strategy = strategy_from_firestore(imported_doc)

    # 단계 수 비교
    assert len(orig_strategy.phases) == len(imp_strategy.phases), "단계 수가 같아야 함"
    print(f"  ✅ 단계 수 일치: {len(orig_strategy.phases)}")

    # 프레임 & 선수 위치 비교
    for pi, (op, ip) in enumerate(zip(orig_strategy.phases, imp_strategy.phases)):
        assert len(op.frames) == len(ip.frames), f"단계 {pi}: 프레임 수가 같아야 함"
        for fi, (of, ifr) in enumerate(zip(op.frames, ip.frames)):
            assert len(of.players) == len(ifr.players), f"프레임 {fi}: 선수 수가 같아야 함"
            for pli, (opl, ipl) in enumerate(zip(of.players, ifr.players)):
                assert opl.position.x == ipl.position.x, f"선수 {pli}: x좌표 불일치"
                assert opl.position.z == ipl.position.z, f"선수 {pli}: z좌표 불일치"
    print(f"  ✅ 모든 선수 위치 데이터 일치")


def test_5_seed_examples():
    """예시 전술 시드 동작 확인."""
    print("\n=== 테스트 5: 예시 전술 시드 ===")

    count = seed_example_strategies()
    assert count == 5, f"5개 예시가 생성되어야 함 (실제: {count})"
    print(f"  ✅ 예시 전술 {count}개 생성됨")

    pub_strats = get_public_strategies()
    seed_strats = [s for s in pub_strats if s.get("authorId") == "__seed__"]
    assert len(seed_strats) == 5, f"공개 전술에 5개 예시가 있어야 함 (실제: {len(seed_strats)})"
    print(f"  ✅ 공개 전술에서 예시 {len(seed_strats)}개 확인")

    for s in seed_strats:
        phases = s.get("phases", [])
        frame_count = sum(len(p.get("frames", [])) for p in phases)
        print(f"     📋 {s['name']} — {len(phases)}단계 {frame_count}프레임")

    # 중복 실행 방지
    count2 = seed_example_strategies()
    assert count2 == 0, "이미 있으면 0 반환"
    print(f"  ✅ 중복 실행 시 0개 생성 (정상)")

    # 프레임 수 검증 (최소 3프레임/단계)
    for s in seed_strats:
        phases = s.get("phases", [])
        for p in phases:
            fcount = len(p.get("frames", []))
            assert fcount >= 3, f"'{s['name']}' 단계 '{p.get('name','')}': 프레임 {fcount}개 < 3개"
    print(f"  ✅ 모든 예시 전술: 단계당 최소 3프레임 확인")

    # seedVersion 확인
    assert seed_strats[0].get("seedVersion", 0) >= 2, "seedVersion이 2 이상이어야 함"
    print(f"  ✅ seedVersion: {seed_strats[0].get('seedVersion')}")


def test_6_seed_import_to_team(user_b, team_b):
    """예시 전술을 팀B로 가져오기."""
    print("\n=== 테스트 6: 예시 전술 팀 가져오기 ===")

    pub_strats = get_public_strategies()
    seed_strats = [s for s in pub_strats if s.get("authorId") == "__seed__"]

    imported_count = 0
    for s in seed_strats[:3]:  # 3개만 가져오기
        loaded = strategy_from_firestore(s)
        strategy_dict = json.loads(strategy_to_json(loaded))
        strategy_dict["name"] = s["name"]
        new_id = save_strategy(
            strategy_dict,
            user_b["uid"],
            user_b["displayName"],
            team_b["id"],
            team_b["name"],
            "team",
        )
        if new_id:
            imported_count += 1
            print(f"  ✅ 가져오기: '{s['name']}' → 팀B (id={new_id[:8]}...)")

    assert imported_count == 3, f"3개를 가져와야 함 (실제: {imported_count})"

    team_b_strats = get_team_strategies(team_b["id"])
    # 이전 테스트에서 1개 + 지금 3개 = 4개
    assert len(team_b_strats) >= 4, f"팀B에 4개 이상이어야 함 (실제: {len(team_b_strats)})"
    print(f"  ✅ 팀B 총 전술: {len(team_b_strats)}개")


def test_7_my_strategies(user_b):
    """내 전술 목록 확인."""
    print("\n=== 테스트 7: 내 전술 목록 ===")

    my = get_my_strategies(user_b["uid"])
    assert len(my) >= 4, f"코치B의 전술이 4개 이상이어야 함 (실제: {len(my)})"
    print(f"  ✅ 코치B의 전술: {len(my)}개")
    for s in my:
        print(f"     📋 {s['name']} ({s['teamName']}, {s['visibility']})")


# ===== 실행 =====
if __name__ == "__main__":
    setup()
    try:
        user_a, user_b, team_a, team_b = test_1_create_users_and_teams()
        original_sid = test_2_save_public_strategy(user_a, team_a)
        imported_id = test_3_import_to_other_team(user_b, team_b, original_sid)
        test_4_strategy_data_integrity(original_sid, imported_id)
        test_5_seed_examples()
        test_6_seed_import_to_team(user_b, team_b)
        test_7_my_strategies(user_b)

        print("\n" + "=" * 50)
        print("🎉 모든 테스트 통과!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        raise
    finally:
        teardown()

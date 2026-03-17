"""예시 전술 데이터 시드 — 처음 시작할 때 공개 예시 전술을 생성."""
from __future__ import annotations

import time
from services import local_store


_SEED_AUTHOR = "풋살코치"
_SEED_TEAM = "예시팀"

# 좌표계: x 좌우(-20~20), y 높이, z 상하(-13~13)
# home = 왼쪽 팀, away = 오른쪽 팀


def _pos(x: float, z: float, y: float = 0.0) -> dict:
    return {"x": x, "y": y, "z": z}


def _player(pid: str, team: str, number: int, x: float, z: float) -> dict:
    return {"id": pid, "team": team, "number": number, "position": _pos(x, z)}


def _frame(players: list, bx: float = 0.0, bz: float = 0.0) -> dict:
    return {
        "id": f"f{int(time.time()*1000) % 100000}_{len(players)}",
        "players": players,
        "ball_position": _pos(bx, bz, 0.22),
        "ball_peak_height": 0.0,
        "ball_trajectory": "linear",
    }


def _home_away_base():
    """기본 상대팀 (away) 1-2-1 배치."""
    return [
        _player("a1", "away", 1, 19, 0),
        _player("a2", "away", 2, 12, -6),
        _player("a3", "away", 3, 12, 6),
        _player("a4", "away", 4, 8, -2),
        _player("a5", "away", 5, 8, 2),
    ]


# ============================================================
# 전술 1: 1-2-1 기본 포메이션 & 빌드업
# ============================================================
def _strategy_121_buildup() -> dict:
    now = int(time.time() * 1000)
    away = _home_away_base()

    phase1_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -12, -6),
            _player("h3", "home", 3, -12, 6),
            _player("h4", "home", 4, -6, -2),
            _player("h5", "home", 5, -6, 2),
        ] + away, -19, 0),
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -10, -7),
            _player("h3", "home", 3, -10, 7),
            _player("h4", "home", 4, -4, -3),
            _player("h5", "home", 5, -4, 3),
        ] + away, -10, -7),
    ]

    phase2_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -6, -8),
            _player("h3", "home", 3, -8, 5),
            _player("h4", "home", 4, 0, -2),
            _player("h5", "home", 5, -2, 4),
        ] + away, -6, -8),
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -4, -6),
            _player("h3", "home", 3, -6, 4),
            _player("h4", "home", 4, 2, 0),
            _player("h5", "home", 5, 0, 5),
        ] + away, 2, 0),
    ]

    return {
        "name": "1-2-1 빌드업",
        "description": "기본 1-2-1 포메이션에서 GK → 윙 → 피벗으로 이어지는 빌드업 패턴",
        "phases": [
            {"id": "p1", "name": "1단계: GK 시작", "description": "골키퍼가 윙에게 배급", "frames": phase1_frames, "order": 0},
            {"id": "p2", "name": "2단계: 전진 패스", "description": "윙이 피벗에게 전진 패스", "frames": phase2_frames, "order": 1},
        ],
        "visibility": "public",
        "authorId": "__seed__",
        "authorName": _SEED_AUTHOR,
        "teamId": "__seed_team__",
        "teamName": _SEED_TEAM,
        "createdAt": now,
        "updatedAt": now,
        "likesCount": 3,
    }


# ============================================================
# 전술 2: 파워플레이 (GK 공격 참여)
# ============================================================
def _strategy_powerplay() -> dict:
    now = int(time.time() * 1000)
    away = _home_away_base()

    phase1_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -8, -7),
            _player("h3", "home", 3, -8, 7),
            _player("h4", "home", 4, -2, -3),
            _player("h5", "home", 5, -2, 3),
        ] + away, -8, -7),
        _frame([
            _player("h1", "home", 1, -10, 0),   # GK 전진!
            _player("h2", "home", 2, -4, -8),
            _player("h3", "home", 3, -4, 8),
            _player("h4", "home", 4, 2, -4),
            _player("h5", "home", 5, 2, 4),
        ] + away, -10, 0),
    ]

    phase2_frames = [
        _frame([
            _player("h1", "home", 1, -6, 0),    # GK 더 전진
            _player("h2", "home", 2, 0, -8),
            _player("h3", "home", 3, 0, 8),
            _player("h4", "home", 4, 6, -3),
            _player("h5", "home", 5, 6, 3),
        ] + away, -6, 0),
        _frame([
            _player("h1", "home", 1, -4, 0),
            _player("h2", "home", 2, 4, -6),
            _player("h3", "home", 3, 4, 6),
            _player("h4", "home", 4, 10, -2),
            _player("h5", "home", 5, 10, 2),
        ] + away, 10, -2),
    ]

    return {
        "name": "파워플레이 (5vs4)",
        "description": "GK가 필드 플레이어로 올라와 수적 우위를 만드는 전술. 동점 또는 역전이 필요할 때 사용",
        "phases": [
            {"id": "p1", "name": "1단계: GK 전진", "description": "골키퍼가 하프라인까지 올라옴", "frames": phase1_frames, "order": 0},
            {"id": "p2", "name": "2단계: 5인 공격", "description": "수적 우위로 공격 전개", "frames": phase2_frames, "order": 1},
        ],
        "visibility": "public",
        "authorId": "__seed__",
        "authorName": _SEED_AUTHOR,
        "teamId": "__seed_team__",
        "teamName": _SEED_TEAM,
        "createdAt": now - 60000,
        "updatedAt": now - 60000,
        "likesCount": 7,
    }


# ============================================================
# 전술 3: 킥인 세트플레이
# ============================================================
def _strategy_kickin() -> dict:
    now = int(time.time() * 1000)
    away = _home_away_base()

    phase1_frames = [
        # 킥인 준비
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 4, -13),   # 킥인 담당
            _player("h3", "home", 3, 6, -4),
            _player("h4", "home", 4, 8, 2),
            _player("h5", "home", 5, 10, -2),
        ] + away, 4, -13),
        # 벽패스 & 진입
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 6, -10),
            _player("h3", "home", 3, 8, -6),    # 벽패스 받음
            _player("h4", "home", 4, 10, 0),
            _player("h5", "home", 5, 12, -3),
        ] + away, 8, -6),
    ]

    phase2_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 8, -8),
            _player("h3", "home", 3, 10, -4),
            _player("h4", "home", 4, 12, 1),
            _player("h5", "home", 5, 14, -2),   # 슈팅 위치
        ] + away, 14, -2),
    ]

    return {
        "name": "킥인 세트플레이 (사이드)",
        "description": "사이드 킥인에서 벽패스를 이용해 페널티 에어리어로 침투하는 세트플레이",
        "phases": [
            {"id": "p1", "name": "1단계: 킥인 & 벽패스", "description": "킥인 후 근거리 벽패스로 전진", "frames": phase1_frames, "order": 0},
            {"id": "p2", "name": "2단계: 슈팅", "description": "피벗이 슈팅 위치로 침투", "frames": phase2_frames, "order": 1},
        ],
        "visibility": "public",
        "authorId": "__seed__",
        "authorName": _SEED_AUTHOR,
        "teamId": "__seed_team__",
        "teamName": _SEED_TEAM,
        "createdAt": now - 120000,
        "updatedAt": now - 120000,
        "likesCount": 5,
    }


# ============================================================
# 전술 4: 코너킥 전술
# ============================================================
def _strategy_corner() -> dict:
    now = int(time.time() * 1000)

    away_corner = [
        _player("a1", "away", 1, 19, 0),
        _player("a2", "away", 2, 16, -3),
        _player("a3", "away", 3, 16, 3),
        _player("a4", "away", 4, 14, 0),
        _player("a5", "away", 5, 12, 0),
    ]

    phase1_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 20, -13),   # 코너킥 키커
            _player("h3", "home", 3, 14, -4),     # 니어포스트
            _player("h4", "home", 4, 16, 2),      # 파포스트
            _player("h5", "home", 5, 12, 0),      # 탑 지역
        ] + away_corner, 20, -13),
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 18, -10),
            _player("h3", "home", 3, 16, -2),     # 니어 진입
            _player("h4", "home", 4, 17, 1),      # 파 진입
            _player("h5", "home", 5, 14, -1),     # 세컨볼 대비
        ] + away_corner, 16, -2),
    ]

    return {
        "name": "코너킥 세트플레이",
        "description": "코너킥에서 니어포스트 플릭 또는 직접 슈팅을 노리는 전술",
        "phases": [
            {"id": "p1", "name": "1단계: 코너킥 실행", "description": "니어포스트로 빠른 킥 → 플릭 또는 다이렉트 슈팅", "frames": phase1_frames, "order": 0},
        ],
        "visibility": "public",
        "authorId": "__seed__",
        "authorName": _SEED_AUTHOR,
        "teamId": "__seed_team__",
        "teamName": _SEED_TEAM,
        "createdAt": now - 180000,
        "updatedAt": now - 180000,
        "likesCount": 4,
    }


# ============================================================
# 전술 5: 3-1 수비 전환
# ============================================================
def _strategy_defensive_transition() -> dict:
    now = int(time.time() * 1000)
    away_attack = [
        _player("a1", "away", 1, 19, 0),
        _player("a2", "away", 2, 4, -5),
        _player("a3", "away", 3, 4, 5),
        _player("a4", "away", 4, -2, -3),
        _player("a5", "away", 5, -2, 3),
    ]

    phase1_frames = [
        # 공격 중 볼 뺏김 직후
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, 2, -6),
            _player("h3", "home", 3, 2, 6),
            _player("h4", "home", 4, 6, 0),
            _player("h5", "home", 5, 10, 0),
        ] + away_attack, -2, -3),
        # 즉시 후퇴
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -6, -6),
            _player("h3", "home", 3, -6, 6),
            _player("h4", "home", 4, -8, 0),
            _player("h5", "home", 5, -2, 0),    # 전방 압박
        ] + away_attack, -2, -3),
    ]

    phase2_frames = [
        _frame([
            _player("h1", "home", 1, -19, 0),
            _player("h2", "home", 2, -10, -5),
            _player("h3", "home", 3, -10, 5),
            _player("h4", "home", 4, -12, 0),
            _player("h5", "home", 5, -6, 0),
        ] + away_attack, -2, 3),
    ]

    return {
        "name": "수비 전환 (3-1 블록)",
        "description": "볼을 뺏겼을 때 즉시 3-1 수비 블록을 형성하여 역습을 차단하는 전환 전술",
        "phases": [
            {"id": "p1", "name": "1단계: 즉시 후퇴", "description": "볼 뺏긴 직후 4명이 자기 진영으로 후퇴", "frames": phase1_frames, "order": 0},
            {"id": "p2", "name": "2단계: 블록 형성", "description": "3-1 블록으로 중앙과 양쪽 차단", "frames": phase2_frames, "order": 1},
        ],
        "visibility": "public",
        "authorId": "__seed__",
        "authorName": _SEED_AUTHOR,
        "teamId": "__seed_team__",
        "teamName": _SEED_TEAM,
        "createdAt": now - 240000,
        "updatedAt": now - 240000,
        "likesCount": 6,
    }


# ============================================================
# 시드 실행
# ============================================================
_ALL_EXAMPLES = [
    _strategy_121_buildup,
    _strategy_powerplay,
    _strategy_kickin,
    _strategy_corner,
    _strategy_defensive_transition,
]


def seed_example_strategies() -> int:
    """예시 전술이 없으면 생성. 반환: 새로 생성된 수."""
    existing = local_store.query("strategies", [("authorId", "==", "__seed__")])
    if existing:
        return 0

    count = 0
    for factory in _ALL_EXAMPLES:
        data = factory()
        local_store.add_doc("strategies", data)
        count += 1
    return count

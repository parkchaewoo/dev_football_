from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
import time
import random
import string


def generate_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))


@dataclass
class Position3D:
    x: float = 0.0
    y: float = 0.0  # height
    z: float = 0.0


@dataclass
class Player:
    id: str = ""
    team: str = "home"  # "home" or "away"
    number: int = 1
    position: Position3D = field(default_factory=Position3D)


@dataclass
class Frame:
    id: str = ""
    players: List[Player] = field(default_factory=list)
    ball_position: Position3D = field(default_factory=lambda: Position3D(0, 0, 0))
    ball_peak_height: float = 0.0
    ball_trajectory: str = "linear"  # "linear" or "parabolic"
    label: str = ""  # optional section label, e.g. "공격 시작"


# Deprecated: kept for backward-compatible loading only
@dataclass
class Phase:
    id: str = ""
    name: str = "1단계"
    description: str = ""
    frames: List[Frame] = field(default_factory=list)
    order: int = 0


@dataclass
class Strategy:
    id: str = ""
    name: str = ""
    description: str = ""
    frames: List[Frame] = field(default_factory=list)
    created_at: float = 0.0


def create_default_players() -> List[Player]:
    hl = 20  # half length
    players = [
        Player("h1", "home", 1, Position3D(-hl + 1, 0, 0)),
        Player("h2", "home", 2, Position3D(-hl + 6, 0, -6)),
        Player("h3", "home", 3, Position3D(-hl + 6, 0, 6)),
        Player("h4", "home", 4, Position3D(-hl + 12, 0, -3)),
        Player("h5", "home", 5, Position3D(-hl + 12, 0, 3)),
        Player("a1", "away", 1, Position3D(hl - 1, 0, 0)),
        Player("a2", "away", 2, Position3D(hl - 6, 0, -6)),
        Player("a3", "away", 3, Position3D(hl - 6, 0, 6)),
        Player("a4", "away", 4, Position3D(hl - 12, 0, -3)),
        Player("a5", "away", 5, Position3D(hl - 12, 0, 3)),
    ]
    return players


def create_default_strategy() -> Strategy:
    return Strategy(
        id=generate_id(),
        name="",
        description="",
        frames=[Frame(
            id=generate_id(),
            players=create_default_players(),
            ball_position=Position3D(0, 0, 0),
        )],
        created_at=time.time(),
    )


def strategy_to_json(strategy: Strategy) -> str:
    return json.dumps(asdict(strategy), ensure_ascii=False, indent=2)


def _parse_frame_dict(f: dict) -> Frame:
    """단일 프레임 dict → Frame 객체."""
    players = []
    for pl in f.get("players", []):
        pos = pl.get("position", {})
        players.append(Player(
            pl.get("id", ""),
            pl.get("team", "home"),
            pl.get("number", 1),
            Position3D(pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)),
        ))
    bp = f.get("ball_position", f.get("ballPosition", {}))
    return Frame(
        f.get("id", generate_id()),
        players,
        Position3D(bp.get("x", 0), bp.get("y", 0.22), bp.get("z", 0)),
        f.get("ball_peak_height", f.get("ballPeakHeight", 0.0)),
        f.get("ball_trajectory", f.get("ballTrajectory", "linear")),
        f.get("label", ""),
    )


def _parse_frames(data: dict) -> List[Frame]:
    """전략 dict에서 프레임 리스트 추출. phases(레거시) / frames(신규) 양쪽 지원."""
    if "frames" in data and isinstance(data["frames"], list) and data["frames"]:
        # 새 포맷: 프레임 직접
        return [_parse_frame_dict(f) for f in data["frames"]]

    # 레거시 포맷: phases → flatten
    frames = []
    phases = data.get("phases", [])
    # order로 정렬
    phases_sorted = sorted(phases, key=lambda p: p.get("order", 0))
    for p in phases_sorted:
        phase_frames = p.get("frames", [])
        for i, f in enumerate(phase_frames):
            frame = _parse_frame_dict(f)
            if i == 0 and p.get("name"):
                frame.label = p["name"]
            frames.append(frame)
    return frames


def strategy_from_json(json_str: str) -> Strategy:
    data = json.loads(json_str)
    frames = _parse_frames(data)
    return Strategy(
        data.get("id", generate_id()),
        data.get("name", ""),
        data.get("description", ""),
        frames,
        data.get("created_at", time.time()),
    )


def strategy_from_firestore(data: dict) -> Strategy:
    """Firestore 문서 데이터에서 Strategy 객체 생성."""
    frames = _parse_frames(data)
    return Strategy(
        data.get("id", generate_id()),
        data.get("name", ""),
        data.get("description", ""),
        frames,
        data.get("created_at", data.get("createdAt", time.time())),
    )

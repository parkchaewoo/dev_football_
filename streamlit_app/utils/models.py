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
    ball_peak_height: float = 0.0  # 프레임 간 공 최고 높이 (롭볼 궤적)
    ball_trajectory: str = "linear"  # "linear" (직선) or "parabolic" (롭볼)


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
    phases: List[Phase] = field(default_factory=list)
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


def create_default_phase() -> Phase:
    return Phase(
        id=generate_id(),
        name="1단계",
        description="",
        frames=[Frame(
            id=generate_id(),
            players=create_default_players(),
            ball_position=Position3D(0, 0, 0),
        )],
        order=0,
    )


def create_default_strategy() -> Strategy:
    return Strategy(
        id=generate_id(),
        name="",
        description="",
        phases=[create_default_phase()],
        created_at=time.time(),
    )


def strategy_to_json(strategy: Strategy) -> str:
    return json.dumps(asdict(strategy), ensure_ascii=False, indent=2)


def strategy_from_json(json_str: str) -> Strategy:
    data = json.loads(json_str)
    phases = []
    for p in data.get("phases", []):
        frames = []
        for f in p.get("frames", []):
            players = [
                Player(
                    pl["id"], pl["team"], pl["number"],
                    Position3D(**pl["position"])
                ) for pl in f.get("players", [])
            ]
            frames.append(Frame(f["id"], players, Position3D(**f["ball_position"]), f.get("ball_peak_height", 0.0), f.get("ball_trajectory", "linear")))
        phases.append(Phase(p["id"], p["name"], p["description"], frames, p["order"]))
    return Strategy(
        data["id"], data["name"], data["description"],
        phases, data.get("created_at", time.time())
    )


def strategy_from_firestore(data: dict) -> Strategy:
    """Firestore 문서 데이터에서 Strategy 객체 생성."""
    phases = []
    for p in data.get("phases", []):
        frames = []
        for f in p.get("frames", []):
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
            frames.append(Frame(
                f.get("id", generate_id()),
                players,
                Position3D(bp.get("x", 0), bp.get("y", 0.22), bp.get("z", 0)),
                f.get("ball_peak_height", f.get("ballPeakHeight", 0.0)),
                f.get("ball_trajectory", f.get("ballTrajectory", "linear")),
            ))
        phases.append(Phase(
            p.get("id", generate_id()),
            p.get("name", ""),
            p.get("description", ""),
            frames,
            p.get("order", 0),
        ))
    return Strategy(
        data.get("id", generate_id()),
        data.get("name", ""),
        data.get("description", ""),
        phases,
        data.get("created_at", data.get("createdAt", time.time())),
    )

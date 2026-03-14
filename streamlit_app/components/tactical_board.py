"""Tactical board component - bidirectional Streamlit component with CSS 3D."""
import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

import streamlit.components.v1 as components

from utils.models import Player, Position3D

_COMPONENT_DIR = Path(__file__).parent / "tactical_board_component"
_component_func = components.declare_component("tactical_board", path=str(_COMPONENT_DIR))


def tactical_board_component(
    players: List[Player],
    ball_position: Position3D,
    frames: list = None,
    is_playing: bool = False,
    key: str = None,
) -> Optional[dict]:
    """Render the 3D tactical board and return drag results.

    Returns:
        dict with {players: [{id, x, z}, ...], ball: {x, z}} when user drags,
        or None when no drag occurred.
    """
    players_data = [asdict(p) for p in players]
    ball_data = asdict(ball_position)

    result = _component_func(
        players=players_data,
        ball=ball_data,
        frames=frames or [],
        is_playing=is_playing,
        key=key,
        default=None,
    )
    return result

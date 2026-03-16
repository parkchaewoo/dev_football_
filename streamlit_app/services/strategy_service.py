from __future__ import annotations

from services import local_store
import time


def save_strategy(
    strategy_dict: dict,
    author_id: str,
    author_name: str,
    team_id: str,
    team_name: str,
    visibility: str,
    existing_id: str = None,
) -> str | None:
    """전략 저장. 반환: strategy ID."""
    data = {
        "name": strategy_dict.get("name", ""),
        "description": strategy_dict.get("description", ""),
        "authorId": author_id,
        "authorName": author_name,
        "teamId": team_id,
        "teamName": team_name,
        "visibility": visibility,
        "phases": strategy_dict.get("phases", []),
        "updatedAt": int(time.time() * 1000),
    }

    if existing_id:
        local_store.update_doc("strategies", existing_id, data)
        return existing_id
    else:
        data["createdAt"] = int(time.time() * 1000)
        data["likesCount"] = 0
        return local_store.add_doc("strategies", data)


# 하위 호환용 별칭
save_strategy_to_firestore = save_strategy


def get_team_strategies(team_id: str) -> list:
    """팀 전술 목록."""
    return local_store.query(
        "strategies",
        [("teamId", "==", team_id)],
        order_by="updatedAt",
        order_dir="DESC",
    )


def get_my_strategies(author_id: str) -> list:
    """내가 만든 전술 목록."""
    return local_store.query(
        "strategies",
        [("authorId", "==", author_id)],
        order_by="updatedAt",
        order_dir="DESC",
    )


def get_public_strategies() -> list:
    """공개 전술 목록."""
    return local_store.query(
        "strategies",
        [("visibility", "==", "public")],
        order_by="updatedAt",
        order_dir="DESC",
    )


def delete_strategy(strategy_id: str) -> None:
    """전략 삭제."""
    local_store.delete_doc("strategies", strategy_id)


def increment_likes(strategy_id: str, delta: int) -> None:
    """좋아요 수 증감."""
    local_store.increment("strategies", strategy_id, "likesCount", delta)

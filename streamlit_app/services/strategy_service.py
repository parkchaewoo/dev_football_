from services.firebase_init import get_firestore_client
from google.cloud.firestore_v1 import Increment
from dataclasses import asdict
import time
import json


def save_strategy_to_firestore(
    strategy_dict: dict,
    author_id: str,
    author_name: str,
    team_id: str,
    team_name: str,
    visibility: str,
    existing_id: str = None,
) -> str | None:
    """전략을 Firestore에 저장. 반환: strategy ID."""
    db = get_firestore_client()
    if not db:
        return None

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
        db.collection("strategies").document(existing_id).update(data)
        return existing_id
    else:
        data["createdAt"] = int(time.time() * 1000)
        data["likesCount"] = 0
        _, ref = db.collection("strategies").add(data)
        return ref.id


def get_team_strategies(team_id: str) -> list:
    """팀 전술 목록."""
    db = get_firestore_client()
    if not db:
        return []
    docs = (
        db.collection("strategies")
        .where("teamId", "==", team_id)
        .order_by("updatedAt", direction="DESCENDING")
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def get_public_strategies() -> list:
    """공개 전술 목록."""
    db = get_firestore_client()
    if not db:
        return []
    docs = (
        db.collection("strategies")
        .where("visibility", "==", "public")
        .order_by("updatedAt", direction="DESCENDING")
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def delete_strategy(strategy_id: str) -> None:
    """전략 삭제."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("strategies").document(strategy_id).delete()


def increment_likes(strategy_id: str, delta: int) -> None:
    """좋아요 수 증감."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("strategies").document(strategy_id).update({
        "likesCount": Increment(delta)
    })

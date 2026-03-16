from __future__ import annotations

from services import local_store
import time
import hashlib


def _nickname_to_uid(nickname: str) -> str:
    """닉네임을 기반으로 고유 uid 생성."""
    return hashlib.sha256(nickname.encode()).hexdigest()[:16]


def create_or_get_user(nickname: str) -> dict | None:
    """닉네임으로 유저 조회/생성. 반환: {uid, displayName, teams, createdAt}"""
    uid = _nickname_to_uid(nickname)
    existing = local_store.get_doc("users", uid)

    if existing:
        existing["uid"] = uid
        return existing

    user_data = {
        "displayName": nickname,
        "photoURL": "",
        "email": "",
        "createdAt": int(time.time() * 1000),
        "teams": [],
    }
    local_store.set_doc("users", uid, user_data)
    user_data["uid"] = uid
    return user_data


def get_user(uid: str) -> dict | None:
    """유저 정보 조회."""
    doc = local_store.get_doc("users", uid)
    if doc:
        doc["uid"] = uid
        return doc
    return None

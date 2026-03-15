from __future__ import annotations

from services.firebase_init import get_firestore_client
import time
import hashlib

try:
    from google.cloud.firestore_v1 import ArrayUnion
except ImportError:
    ArrayUnion = None


def _nickname_to_uid(nickname: str) -> str:
    """닉네임을 기반으로 고유 uid 생성."""
    return hashlib.sha256(nickname.encode()).hexdigest()[:16]


def create_or_get_user(nickname: str) -> dict | None:
    """닉네임으로 유저 조회/생성. 반환: {uid, displayName, teams, createdAt}"""
    db = get_firestore_client()
    if not db:
        return None

    uid = _nickname_to_uid(nickname)
    ref = db.collection("users").document(uid)
    doc = ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["uid"] = uid
        return data

    user_data = {
        "displayName": nickname,
        "photoURL": "",
        "email": "",
        "createdAt": int(time.time() * 1000),
        "teams": [],
    }
    ref.set(user_data)
    user_data["uid"] = uid
    return user_data


def get_user(uid: str) -> dict | None:
    """유저 정보 조회."""
    db = get_firestore_client()
    if not db:
        return None
    doc = db.collection("users").document(uid).get()
    if doc.exists:
        data = doc.to_dict()
        data["uid"] = uid
        return data
    return None

from __future__ import annotations

from services import local_store
import os
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


def is_super_admin(nickname: str) -> bool:
    """환경변수 SUPER_ADMIN_NICKNAME에 등록된 슈퍼 관리자인지 확인.

    여러 명 지정 시 쉼표로 구분: SUPER_ADMIN_NICKNAME=admin,관리자
    """
    env_val = os.environ.get("SUPER_ADMIN_NICKNAME", "")
    if not env_val:
        return False
    admin_nicks = [n.strip() for n in env_val.split(",") if n.strip()]
    return nickname in admin_nicks


def delete_user(uid: str) -> None:
    """사용자 삭제 — 소속 팀에서도 제거."""
    user_doc = local_store.get_doc("users", uid)
    if not user_doc:
        return
    for team_id in user_doc.get("teams", []):
        local_store.array_remove("teams", team_id, "members", [uid])
        local_store.array_remove("teams", team_id, "admins", [uid])
    local_store.delete_doc("users", uid)

from __future__ import annotations

from services import local_store
import time
import random
import string


def _generate_invite_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def team_name_exists(name: str) -> bool:
    """동일한 이름의 팀이 이미 존재하는지 확인."""
    existing = local_store.query("teams", [("name", "==", name)])
    return len(existing) > 0


def create_team(name: str, description: str, user_id: str) -> dict | None:
    """팀 생성. 중복 이름이면 None 반환."""
    if team_name_exists(name):
        return None
    team_data = {
        "name": name,
        "description": description,
        "leaderId": user_id,
        "members": [user_id],
        "admins": [user_id],
        "inviteCode": _generate_invite_code(),
        "createdAt": int(time.time() * 1000),
    }
    team_id = local_store.add_doc("teams", team_data)
    local_store.array_union("users", user_id, "teams", [team_id])
    team_data["id"] = team_id
    return team_data


def join_team_by_code(invite_code: str, user_id: str) -> dict | None:
    """초대코드로 팀 가입."""
    teams = local_store.query("teams", [("inviteCode", "==", invite_code)])
    if not teams:
        return None

    team = teams[0]
    team_id = team["id"]

    if user_id in team.get("members", []):
        return team

    local_store.array_union("teams", team_id, "members", [user_id])
    local_store.array_union("users", user_id, "teams", [team_id])
    team["members"].append(user_id)
    return team


def get_my_teams(user_id: str) -> list:
    """내 팀 목록 조회."""
    return local_store.query("teams", [("members", "array_contains", user_id)])


def leave_team(team_id: str, user_id: str) -> None:
    """팀 탈퇴."""
    local_store.array_remove("teams", team_id, "members", [user_id])
    local_store.array_remove("users", user_id, "teams", [team_id])


def set_admin(team_id: str, user_id: str) -> bool:
    """팀 운영진으로 지정."""
    local_store.array_union("teams", team_id, "admins", [user_id])
    return True


def remove_admin(team_id: str, user_id: str) -> bool:
    """팀 운영진 해제."""
    local_store.array_remove("teams", team_id, "admins", [user_id])
    return True


def get_team(team_id: str) -> dict | None:
    """팀 정보 조회 (admins 포함)."""
    doc = local_store.get_doc("teams", team_id)
    if doc:
        doc["id"] = team_id
        return doc
    return None


def is_admin(team: dict, user_id: str) -> bool:
    """해당 유저가 팀 운영진인지 확인."""
    if not team:
        return False
    if team.get("leaderId") == user_id:
        return True
    return user_id in team.get("admins", [])


def delete_team(team_id: str) -> None:
    """팀 삭제 (리더만)."""
    doc = local_store.get_doc("teams", team_id)
    if not doc:
        return
    for uid in doc.get("members", []):
        local_store.array_remove("users", uid, "teams", [team_id])
    local_store.delete_doc("teams", team_id)

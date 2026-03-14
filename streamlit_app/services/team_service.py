from services.firebase_init import get_firestore_client
from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
import time
import random
import string


def _generate_invite_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


def create_team(name: str, description: str, user_id: str) -> dict | None:
    """팀 생성. 반환: 팀 dict."""
    db = get_firestore_client()
    if not db:
        return None

    team_data = {
        "name": name,
        "description": description,
        "leaderId": user_id,
        "members": [user_id],
        "inviteCode": _generate_invite_code(),
        "createdAt": int(time.time() * 1000),
    }
    _, ref = db.collection("teams").add(team_data)
    db.collection("users").document(user_id).update({
        "teams": ArrayUnion([ref.id])
    })
    team_data["id"] = ref.id
    return team_data


def join_team_by_code(invite_code: str, user_id: str) -> dict | None:
    """초대코드로 팀 가입."""
    db = get_firestore_client()
    if not db:
        return None

    teams = db.collection("teams").where("inviteCode", "==", invite_code).get()
    if not teams:
        return None

    team_doc = teams[0]
    team = team_doc.to_dict()
    team["id"] = team_doc.id

    if user_id in team.get("members", []):
        return team

    db.collection("teams").document(team_doc.id).update({
        "members": ArrayUnion([user_id])
    })
    db.collection("users").document(user_id).update({
        "teams": ArrayUnion([team_doc.id])
    })
    team["members"].append(user_id)
    return team


def get_my_teams(user_id: str) -> list:
    """내 팀 목록 조회."""
    db = get_firestore_client()
    if not db:
        return []

    teams = db.collection("teams").where("members", "array_contains", user_id).get()
    result = []
    for doc in teams:
        t = doc.to_dict()
        t["id"] = doc.id
        result.append(t)
    return result


def leave_team(team_id: str, user_id: str) -> None:
    """팀 탈퇴."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("teams").document(team_id).update({
        "members": ArrayRemove([user_id])
    })
    db.collection("users").document(user_id).update({
        "teams": ArrayRemove([team_id])
    })


def delete_team(team_id: str) -> None:
    """팀 삭제 (리더만)."""
    db = get_firestore_client()
    if not db:
        return
    team_doc = db.collection("teams").document(team_id).get()
    if not team_doc.exists:
        return
    team = team_doc.to_dict()
    for uid in team.get("members", []):
        db.collection("users").document(uid).update({
            "teams": ArrayRemove([team_id])
        })
    db.collection("teams").document(team_id).delete()

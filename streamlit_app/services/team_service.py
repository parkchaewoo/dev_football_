from services.firebase_init import get_firestore_client
import time
import random
import string

try:
    from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove
except ImportError:
    ArrayUnion = None
    ArrayRemove = None


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
        "admins": [user_id],  # 리더는 자동으로 운영진
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


def set_admin(team_id: str, user_id: str) -> bool:
    """팀 운영진으로 지정."""
    db = get_firestore_client()
    if not db:
        return False
    db.collection("teams").document(team_id).update({
        "admins": ArrayUnion([user_id])
    })
    return True


def remove_admin(team_id: str, user_id: str) -> bool:
    """팀 운영진 해제."""
    db = get_firestore_client()
    if not db:
        return False
    db.collection("teams").document(team_id).update({
        "admins": ArrayRemove([user_id])
    })
    return True


def get_team(team_id: str) -> dict | None:
    """팀 정보 조회 (admins 포함)."""
    db = get_firestore_client()
    if not db:
        return None
    doc = db.collection("teams").document(team_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
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

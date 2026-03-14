"""팀 게시판 서비스 - Firestore CRUD + 로컬 모드 지원."""
from services.firebase_init import get_firestore_client
import time
import hashlib


def _hash_password(password: str) -> str:
    """비밀번호 해시."""
    return hashlib.sha256(password.encode()).hexdigest()


def can_read_secret(post: dict, user_id: str, team: dict | None) -> bool:
    """비밀글 읽기 권한 확인. 작성자 본인 또는 운영진이면 True."""
    if not post.get("isSecret"):
        return True
    if post.get("authorId") == user_id:
        return True
    if team:
        if team.get("leaderId") == user_id:
            return True
        if user_id in team.get("admins", []):
            return True
    return False


def can_manage_post(post: dict, user_id: str, team: dict | None) -> bool:
    """게시글 수정/삭제 권한 확인. 작성자 본인 또는 운영진."""
    if post.get("authorId") == user_id:
        return True
    if team:
        if team.get("leaderId") == user_id:
            return True
        if user_id in team.get("admins", []):
            return True
    return False


def create_post(
    title: str,
    content: str,
    author_id: str,
    author_name: str,
    team_id: str,
    is_secret: bool = False,
    password: str = "",
) -> dict | None:
    """게시글 작성."""
    db = get_firestore_client()
    if not db:
        return None

    post_data = {
        "title": title,
        "content": content,
        "authorId": author_id,
        "authorName": author_name,
        "teamId": team_id,
        "isSecret": is_secret,
        "passwordHash": _hash_password(password) if is_secret and password else "",
        "createdAt": int(time.time() * 1000),
        "updatedAt": int(time.time() * 1000),
    }
    _, ref = db.collection("board_posts").add(post_data)
    post_data["id"] = ref.id
    return post_data


def get_team_posts(team_id: str) -> list:
    """팀 게시글 목록 조회 (최신순)."""
    db = get_firestore_client()
    if not db:
        return []
    docs = (
        db.collection("board_posts")
        .where("teamId", "==", team_id)
        .order_by("createdAt", direction="DESCENDING")
        .limit(50)
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def get_post(post_id: str) -> dict | None:
    """단일 게시글 조회."""
    db = get_firestore_client()
    if not db:
        return None
    doc = db.collection("board_posts").document(post_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def verify_post_password(post_id: str, password: str) -> bool:
    """비밀글 비밀번호 확인."""
    post = get_post(post_id)
    if not post:
        return False
    if not post.get("isSecret"):
        return True
    return post.get("passwordHash", "") == _hash_password(password)


def update_post(
    post_id: str,
    title: str,
    content: str,
    is_secret: bool = False,
    password: str = "",
) -> bool:
    """게시글 수정."""
    db = get_firestore_client()
    if not db:
        return False
    update_data = {
        "title": title,
        "content": content,
        "isSecret": is_secret,
        "updatedAt": int(time.time() * 1000),
    }
    if is_secret and password:
        update_data["passwordHash"] = _hash_password(password)
    elif not is_secret:
        update_data["passwordHash"] = ""
    db.collection("board_posts").document(post_id).update(update_data)
    return True


def delete_post(post_id: str) -> None:
    """게시글 삭제."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("board_posts").document(post_id).delete()

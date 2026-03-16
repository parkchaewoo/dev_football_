"""팀 게시판 서비스 - 로컬 JSON 저장소."""
from __future__ import annotations

from services import local_store
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
    post_id = local_store.add_doc("board_posts", post_data)
    post_data["id"] = post_id
    return post_data


def get_team_posts(team_id: str) -> list:
    """팀 게시글 목록 조회 (최신순)."""
    return local_store.query(
        "board_posts",
        [("teamId", "==", team_id)],
        order_by="createdAt",
        order_dir="DESC",
        limit=50,
    )


def get_post(post_id: str) -> dict | None:
    """단일 게시글 조회."""
    doc = local_store.get_doc("board_posts", post_id)
    if doc:
        doc["id"] = post_id
        return doc
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
    local_store.update_doc("board_posts", post_id, update_data)
    return True


def delete_post(post_id: str) -> None:
    """게시글 삭제."""
    local_store.delete_doc("board_posts", post_id)

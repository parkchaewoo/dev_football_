from __future__ import annotations

from services.firebase_init import get_firestore_client
from services.strategy_service import increment_likes
import time


def add_comment(
    strategy_id: str,
    author_id: str,
    author_name: str,
    text: str,
) -> dict | None:
    """댓글 추가."""
    db = get_firestore_client()
    if not db:
        return None

    comment_data = {
        "strategyId": strategy_id,
        "authorId": author_id,
        "authorName": author_name,
        "authorPhoto": "",
        "text": text,
        "createdAt": int(time.time() * 1000),
    }
    _, ref = db.collection("comments").add(comment_data)
    comment_data["id"] = ref.id
    return comment_data


def get_comments(strategy_id: str) -> list:
    """댓글 목록 조회."""
    db = get_firestore_client()
    if not db:
        return []
    docs = (
        db.collection("comments")
        .where("strategyId", "==", strategy_id)
        .order_by("createdAt")
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def delete_comment(comment_id: str) -> None:
    """댓글 삭제."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("comments").document(comment_id).delete()


def toggle_like(strategy_id: str, user_id: str) -> bool:
    """좋아요 토글. 반환: True=좋아요 추가, False=좋아요 취소."""
    db = get_firestore_client()
    if not db:
        return False

    like_id = f"{strategy_id}__{user_id}"
    ref = db.collection("likes").document(like_id)
    doc = ref.get()

    if doc.exists:
        ref.delete()
        increment_likes(strategy_id, -1)
        return False
    else:
        ref.set({
            "strategyId": strategy_id,
            "userId": user_id,
            "createdAt": int(time.time() * 1000),
        })
        increment_likes(strategy_id, 1)
        return True


def has_liked(strategy_id: str, user_id: str) -> bool:
    """좋아요 여부 확인."""
    db = get_firestore_client()
    if not db:
        return False
    like_id = f"{strategy_id}__{user_id}"
    return db.collection("likes").document(like_id).get().exists


# ===== 병원 리뷰 =====

def add_hospital_review(
    body_part: str,
    hospital_keyword: str,
    author_id: str,
    author_name: str,
    text: str,
    rating: int,
) -> dict | None:
    """병원 리뷰 추가."""
    db = get_firestore_client()
    if not db:
        return None

    review_data = {
        "bodyPart": body_part,
        "hospitalKeyword": hospital_keyword,
        "authorId": author_id,
        "authorName": author_name,
        "text": text,
        "rating": max(1, min(5, rating)),
        "createdAt": int(time.time() * 1000),
    }
    _, ref = db.collection("hospital_reviews").add(review_data)
    review_data["id"] = ref.id
    return review_data


def get_hospital_reviews(body_part: str, hospital_keyword: str) -> list:
    """특정 부위+병원 키워드에 대한 리뷰 목록 조회."""
    db = get_firestore_client()
    if not db:
        return []
    docs = (
        db.collection("hospital_reviews")
        .where("bodyPart", "==", body_part)
        .where("hospitalKeyword", "==", hospital_keyword)
        .order_by("createdAt")
        .get()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]


def delete_hospital_review(review_id: str) -> None:
    """병원 리뷰 삭제."""
    db = get_firestore_client()
    if not db:
        return
    db.collection("hospital_reviews").document(review_id).delete()

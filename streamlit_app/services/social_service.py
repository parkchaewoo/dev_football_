from __future__ import annotations

from services import local_store
from services.strategy_service import increment_likes
import time


def add_comment(
    strategy_id: str,
    author_id: str,
    author_name: str,
    text: str,
) -> dict | None:
    """댓글 추가."""
    comment_data = {
        "strategyId": strategy_id,
        "authorId": author_id,
        "authorName": author_name,
        "authorPhoto": "",
        "text": text,
        "createdAt": int(time.time() * 1000),
    }
    comment_id = local_store.add_doc("comments", comment_data)
    comment_data["id"] = comment_id
    return comment_data


def get_comments(strategy_id: str) -> list:
    """댓글 목록 조회."""
    return local_store.query(
        "comments",
        [("strategyId", "==", strategy_id)],
        order_by="createdAt",
        order_dir="ASC",
    )


def delete_comment(comment_id: str) -> None:
    """댓글 삭제."""
    local_store.delete_doc("comments", comment_id)


def toggle_like(strategy_id: str, user_id: str) -> bool:
    """좋아요 토글. 반환: True=좋아요 추가, False=좋아요 취소."""
    like_id = f"{strategy_id}__{user_id}"
    existing = local_store.get_doc("likes", like_id)

    if existing:
        local_store.delete_doc("likes", like_id)
        increment_likes(strategy_id, -1)
        return False
    else:
        local_store.set_doc("likes", like_id, {
            "strategyId": strategy_id,
            "userId": user_id,
            "createdAt": int(time.time() * 1000),
        })
        increment_likes(strategy_id, 1)
        return True


def has_liked(strategy_id: str, user_id: str) -> bool:
    """좋아요 여부 확인."""
    like_id = f"{strategy_id}__{user_id}"
    return local_store.get_doc("likes", like_id) is not None


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
    review_data = {
        "bodyPart": body_part,
        "hospitalKeyword": hospital_keyword,
        "authorId": author_id,
        "authorName": author_name,
        "text": text,
        "rating": max(1, min(5, rating)),
        "createdAt": int(time.time() * 1000),
    }
    review_id = local_store.add_doc("hospital_reviews", review_data)
    review_data["id"] = review_id
    return review_data


def get_hospital_reviews(body_part: str, hospital_keyword: str) -> list:
    """특정 부위+병원 키워드에 대한 리뷰 목록 조회."""
    return local_store.query(
        "hospital_reviews",
        [("bodyPart", "==", body_part), ("hospitalKeyword", "==", hospital_keyword)],
        order_by="createdAt",
        order_dir="ASC",
    )


def delete_hospital_review(review_id: str) -> None:
    """병원 리뷰 삭제."""
    local_store.delete_doc("hospital_reviews", review_id)

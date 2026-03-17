"""채팅 서비스 — Firebase Realtime Database 사용, 미설정 시 로컬 폴백."""
from __future__ import annotations

import time
import uuid

from services.firebase_init import get_rtdb_reference


def _gen_id() -> str:
    return uuid.uuid4().hex[:16]


def get_messages(limit: int = 50) -> list[dict]:
    """채팅 메시지 목록 조회 (최신 limit개)."""
    ref_fn = get_rtdb_reference()
    if ref_fn is None:
        return []

    chat_ref = ref_fn("chat")
    data = chat_ref.order_by_child("timestamp").limit_to_last(limit).get()

    if not data:
        return []

    messages = []
    for key, val in data.items():
        if isinstance(val, dict):
            val["_key"] = key
            messages.append(val)

    messages.sort(key=lambda m: m.get("timestamp", 0))
    return messages


def send_message(
    author: str,
    text: str,
    strategy_id: str | None = None,
    phase_id: str | None = None,
) -> dict | None:
    """채팅 메시지 전송."""
    ref_fn = get_rtdb_reference()
    if ref_fn is None:
        return None

    message = {
        "id": _gen_id(),
        "author": author,
        "text": text.strip(),
        "timestamp": int(time.time() * 1000),
    }
    if strategy_id:
        message["strategyId"] = strategy_id
    if phase_id:
        message["phaseId"] = phase_id

    chat_ref = ref_fn("chat")
    chat_ref.push(message)
    return message

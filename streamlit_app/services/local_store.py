"""저장소 모듈 — Firebase Firestore 사용, 미설정 시 로컬 JSON 폴백."""
from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any

from services.firebase_init import get_firestore_client

# ===== 로컬 JSON 폴백 (Firebase 미설정 시) =====
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_locks: dict[str, threading.Lock] = {}
_global_lock = threading.Lock()


def _get_lock(collection: str) -> threading.Lock:
    with _global_lock:
        if collection not in _locks:
            _locks[collection] = threading.Lock()
        return _locks[collection]


def _collection_path(collection: str) -> Path:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    return _DATA_DIR / f"{collection}.json"


def _read_collection(collection: str) -> dict[str, dict]:
    path = _collection_path(collection)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_collection(collection: str, data: dict[str, dict]) -> None:
    path = _collection_path(collection)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _gen_id() -> str:
    return uuid.uuid4().hex[:16]


def _use_firestore() -> bool:
    return get_firestore_client() is not None


# ===== CRUD =====

def get_doc(collection: str, doc_id: str) -> dict | None:
    if _use_firestore():
        db = get_firestore_client()
        snap = db.collection(collection).document(doc_id).get()
        if snap.exists:
            return snap.to_dict()
        return None

    with _get_lock(collection):
        docs = _read_collection(collection)
        return docs.get(doc_id)


def set_doc(collection: str, doc_id: str, data: dict) -> None:
    if _use_firestore():
        db = get_firestore_client()
        db.collection(collection).document(doc_id).set(data)
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        docs[doc_id] = data
        _write_collection(collection, docs)


def add_doc(collection: str, data: dict) -> str:
    if _use_firestore():
        db = get_firestore_client()
        _, ref = db.collection(collection).add(data)
        return ref.id

    doc_id = _gen_id()
    with _get_lock(collection):
        docs = _read_collection(collection)
        docs[doc_id] = data
        _write_collection(collection, docs)
    return doc_id


def update_doc(collection: str, doc_id: str, updates: dict) -> None:
    if _use_firestore():
        db = get_firestore_client()
        db.collection(collection).document(doc_id).update(updates)
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        if doc_id in docs:
            docs[doc_id].update(updates)
            _write_collection(collection, docs)


def delete_doc(collection: str, doc_id: str) -> None:
    if _use_firestore():
        db = get_firestore_client()
        db.collection(collection).document(doc_id).delete()
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        if doc_id in docs:
            del docs[doc_id]
            _write_collection(collection, docs)


# ===== Array operations =====

def array_union(collection: str, doc_id: str, field: str, values: list) -> None:
    if _use_firestore():
        from google.cloud.firestore_v1 import ArrayUnion
        db = get_firestore_client()
        db.collection(collection).document(doc_id).update({
            field: ArrayUnion(values)
        })
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        if doc_id in docs:
            arr = docs[doc_id].get(field, [])
            for v in values:
                if v not in arr:
                    arr.append(v)
            docs[doc_id][field] = arr
            _write_collection(collection, docs)


def array_remove(collection: str, doc_id: str, field: str, values: list) -> None:
    if _use_firestore():
        from google.cloud.firestore_v1 import ArrayRemove
        db = get_firestore_client()
        db.collection(collection).document(doc_id).update({
            field: ArrayRemove(values)
        })
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        if doc_id in docs:
            arr = docs[doc_id].get(field, [])
            docs[doc_id][field] = [v for v in arr if v not in values]
            _write_collection(collection, docs)


def increment(collection: str, doc_id: str, field: str, delta: int) -> None:
    if _use_firestore():
        from google.cloud.firestore_v1 import Increment
        db = get_firestore_client()
        db.collection(collection).document(doc_id).update({
            field: Increment(delta)
        })
        return

    with _get_lock(collection):
        docs = _read_collection(collection)
        if doc_id in docs:
            docs[doc_id][field] = docs[doc_id].get(field, 0) + delta
            _write_collection(collection, docs)


# ===== Query =====

def query(
    collection: str,
    filters: list[tuple[str, str, Any]] | None = None,
    order_by: str | None = None,
    order_dir: str = "ASC",
    limit: int | None = None,
) -> list[dict]:
    """Query documents.

    filters: list of (field, op, value) where op is "==" or "array_contains"
    """
    if _use_firestore():
        from google.cloud.firestore_v1 import query as fquery
        db = get_firestore_client()
        ref = db.collection(collection)

        for field, op, value in (filters or []):
            try:
                ref = ref.where(filter=fquery.FieldFilter(field, op, value))
            except AttributeError:
                ref = ref.where(field, op, value)

        results = []
        for doc in ref.stream():
            d = doc.to_dict()
            d["id"] = doc.id
            results.append(d)

        # 복합 인덱스 없이도 동작하도록 Python에서 정렬
        if order_by:
            reverse = order_dir.upper() in ("DESC", "DESCENDING")
            results.sort(key=lambda d: d.get(order_by, 0), reverse=reverse)

        if limit:
            results = results[:limit]

        return results

    # 로컬 폴백
    with _get_lock(collection):
        docs = _read_collection(collection)

    results = []
    for doc_id, doc in docs.items():
        match = True
        for field, op, value in (filters or []):
            if op == "==":
                if doc.get(field) != value:
                    match = False
                    break
            elif op == "array_contains":
                if value not in doc.get(field, []):
                    match = False
                    break
        if match:
            result = dict(doc)
            result["id"] = doc_id
            results.append(result)

    if order_by:
        reverse = order_dir.upper() in ("DESC", "DESCENDING")
        results.sort(key=lambda d: d.get(order_by, 0), reverse=reverse)

    if limit:
        results = results[:limit]

    return results

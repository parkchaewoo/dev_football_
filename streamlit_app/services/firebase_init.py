"""Firebase Admin SDK 초기화 — Firestore + Realtime Database."""
from __future__ import annotations

import os
import json

_firestore_client = None
_rtdb_ref = None
_initialized = False


def _init_firebase():
    global _firestore_client, _rtdb_ref, _initialized
    if _initialized:
        return
    _initialized = True

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, db as rtdb

        cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY", "")
        cred_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")

        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        elif cred_json:
            cred = credentials.Certificate(json.loads(cred_json))
        else:
            return

        database_url = os.environ.get("FIREBASE_DATABASE_URL", "")

        if not firebase_admin._apps:
            options = {}
            if database_url:
                options["databaseURL"] = database_url
            firebase_admin.initialize_app(cred, options)

        _firestore_client = firestore.client()

        if database_url:
            _rtdb_ref = rtdb.reference
    except Exception:
        _firestore_client = None
        _rtdb_ref = None


def get_firestore_client():
    """Firestore 클라이언트 반환. 미설정 시 None."""
    _init_firebase()
    return _firestore_client


def get_rtdb_reference():
    """Realtime Database reference 함수 반환. 미설정 시 None."""
    _init_firebase()
    return _rtdb_ref


def is_firebase_configured() -> bool:
    """Firebase가 정상적으로 설정되었는지 확인."""
    _init_firebase()
    return _firestore_client is not None

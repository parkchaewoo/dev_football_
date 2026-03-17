"""Firebase Admin SDK 초기화."""
from __future__ import annotations

import os
import json

_firestore_client = None
_initialized = False


def _init_firebase():
    global _firestore_client, _initialized
    if _initialized:
        return
    _initialized = True

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY", "")
        cred_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")

        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
        elif cred_json:
            cred = credentials.Certificate(json.loads(cred_json))
        else:
            return

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        _firestore_client = firestore.client()
    except Exception:
        _firestore_client = None


def get_firestore_client():
    """Firestore 클라이언트 반환. 미설정 시 None."""
    _init_firebase()
    return _firestore_client


def is_firebase_configured() -> bool:
    """Firebase가 정상적으로 설정되었는지 확인."""
    _init_firebase()
    return _firestore_client is not None

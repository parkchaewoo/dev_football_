"""Firebase Admin SDK 초기화 — Firestore only."""
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
        import streamlit as st
        import firebase_admin
        from firebase_admin import credentials, firestore

        # 1) st.secrets의 TOML 테이블 (Streamlit Cloud 권장)
        # 2) 환경변수 JSON 문자열
        # 3) 환경변수 파일 경로
        cred_dict = None

        if "FIREBASE_SERVICE_ACCOUNT" in st.secrets:
            cred_dict = dict(st.secrets["FIREBASE_SERVICE_ACCOUNT"])

        if cred_dict is None:
            cred_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON", "")
            if cred_json:
                cred_dict = json.loads(cred_json)

        if cred_dict is None:
            cred_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY", "")
            if cred_path and os.path.exists(cred_path):
                cred_dict = json.load(open(cred_path))

        if cred_dict is None:
            return

        cred = credentials.Certificate(cred_dict)

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

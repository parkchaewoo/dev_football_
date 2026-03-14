import streamlit as st
import json
import os

_firestore_client = None
_firebase_available = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    _firebase_available = True
except ImportError:
    _firebase_available = False


def get_firestore_client():
    """Firebase Admin SDK 초기화 및 Firestore 클라이언트 반환."""
    global _firestore_client

    if not _firebase_available:
        return None

    if _firestore_client is not None:
        return _firestore_client

    if firebase_admin._apps:
        _firestore_client = firestore.client()
        return _firestore_client

    # 방법 1: Streamlit secrets에서 서비스 계정 키 로드
    try:
        if hasattr(st, 'secrets') and 'firebase' in st.secrets:
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _firestore_client = firestore.client()
            return _firestore_client
    except Exception:
        pass

    # 방법 2: GOOGLE_APPLICATION_CREDENTIALS 환경변수
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        return _firestore_client

    # 방법 3: 서비스 계정 JSON 문자열 환경변수
    cred_json = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if cred_json:
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        _firestore_client = firestore.client()
        return _firestore_client

    return None


def is_firebase_configured() -> bool:
    """Firebase가 설정되어 있는지 확인."""
    if not _firebase_available:
        return False
    return get_firestore_client() is not None

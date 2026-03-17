"""관리자 데이터 관리 페이지 - Firestore 컬렉션 데이터 조회/삭제."""
import streamlit as st
import datetime


# 관리 대상 컬렉션 정의
_COLLECTIONS = {
    "strategies": {
        "label": "전술",
        "display_fields": ["name", "authorName", "teamName", "updatedAt"],
        "headers": ["이름", "작성자", "팀", "수정일"],
    },
    "board_posts": {
        "label": "게시글",
        "display_fields": ["title", "authorName", "createdAt"],
        "headers": ["제목", "작성자", "작성일"],
    },
    "comments": {
        "label": "댓글",
        "display_fields": ["text", "authorName", "createdAt"],
        "headers": ["내용", "작성자", "작성일"],
    },
    "hospital_reviews": {
        "label": "병원 리뷰",
        "display_fields": ["hospitalKeyword", "authorName", "rating", "createdAt"],
        "headers": ["병원", "작성자", "평점", "작성일"],
    },
    "likes": {
        "label": "좋아요",
        "display_fields": ["strategyId", "userId", "createdAt"],
        "headers": ["전술ID", "유저ID", "날짜"],
    },
}


def _format_ts(ts) -> str:
    """타임스탬프를 날짜 문자열로 변환."""
    if not ts or not isinstance(ts, (int, float)):
        return "-"
    try:
        return datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def _format_value(field: str, value) -> str:
    """필드 값을 표시용 문자열로 변환."""
    if field in ("createdAt", "updatedAt"):
        return _format_ts(value)
    if value is None:
        return "-"
    s = str(value)
    return s[:40] + "..." if len(s) > 40 else s


def render_admin_manage_page():
    user = st.session_state.user
    team = st.session_state.current_team

    st.header("🛠️ 데이터 관리")

    if not team or not team.get("id"):
        st.info("팀에 가입한 후 사용할 수 있습니다.")
        return

    from services.team_service import get_team, is_admin
    team_data = get_team(team["id"])
    if not team_data:
        team_data = team

    # 팀 정보 표시
    team_name_display = team_data.get("name", team.get("name", ""))
    invite_code = team_data.get("inviteCode", "")
    if team_name_display:
        st.info(f"🏟️ {team_name_display}" + (f" · 초대코드: **{invite_code}**" if invite_code else ""))
    if invite_code:
        st.code(invite_code, language=None)

    # 리더만 접근 가능
    if team_data.get("leaderId") != user["uid"]:
        st.warning("팀 리더만 데이터를 관리할 수 있습니다.")
        return

    from services import local_store

    st.caption("Firestore에 쌓인 데이터를 조회하고 불필요한 항목을 삭제할 수 있습니다.")

    col_sel = st.selectbox(
        "컬렉션 선택",
        list(_COLLECTIONS.keys()),
        format_func=lambda k: f"{_COLLECTIONS[k]['label']} ({k})",
    )

    config = _COLLECTIONS[col_sel]

    # 팀 데이터만 보기 옵션
    team_only = st.checkbox("내 팀 데이터만 보기", value=True)

    if team_only:
        # 컬렉션별 팀 필터 필드
        team_field_map = {
            "strategies": "teamId",
            "board_posts": "teamId",
            "comments": None,  # 댓글은 팀 필드 없음
            "hospital_reviews": None,
            "likes": None,
        }
        team_field = team_field_map.get(col_sel)
        if team_field:
            docs = local_store.query(col_sel, [(team_field, "==", team["id"])])
        else:
            docs = local_store.get_all_docs(col_sel, limit=200)
    else:
        docs = local_store.get_all_docs(col_sel, limit=200)

    st.caption(f"총 {len(docs)}건")

    if not docs:
        st.info("데이터가 없습니다.")
        return

    # 선택 삭제를 위한 체크박스 상태
    select_key = f"admin_select_{col_sel}"
    if select_key not in st.session_state:
        st.session_state[select_key] = set()

    # 전체 선택/해제
    col_all, col_del = st.columns([3, 1])
    with col_all:
        select_all = st.checkbox("전체 선택", key=f"admin_all_{col_sel}")
    with col_del:
        if st.button("🗑️ 선택 삭제", type="primary", key=f"admin_del_{col_sel}"):
            selected = st.session_state[select_key]
            if selected:
                deleted = local_store.delete_docs_batch(col_sel, list(selected))
                st.session_state[select_key] = set()
                st.success(f"{deleted}건 삭제 완료!")
                st.rerun()
            else:
                st.warning("삭제할 항목을 선택하세요.")

    # 헤더
    header_cols = st.columns([0.5] + [2] * len(config["headers"]))
    with header_cols[0]:
        st.caption("✓")
    for i, h in enumerate(config["headers"]):
        with header_cols[i + 1]:
            st.caption(f"**{h}**")

    st.divider()

    # 데이터 행
    for doc in docs:
        doc_id = doc.get("id", "")
        row_cols = st.columns([0.5] + [2] * len(config["display_fields"]))

        with row_cols[0]:
            checked = select_all or doc_id in st.session_state[select_key]
            if st.checkbox("", value=checked, key=f"chk_{col_sel}_{doc_id}", label_visibility="collapsed"):
                st.session_state[select_key].add(doc_id)
            else:
                st.session_state[select_key].discard(doc_id)

        for i, field in enumerate(config["display_fields"]):
            with row_cols[i + 1]:
                st.text(_format_value(field, doc.get(field)))

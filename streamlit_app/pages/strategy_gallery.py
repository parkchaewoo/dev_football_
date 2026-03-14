"""공개 전술 갤러리 - 다른 사람들이 만든 전술을 열람."""
import streamlit as st
import datetime


def render_strategy_gallery_page():
    firebase_ok = st.session_state.get("firebase_ok", False)
    user = st.session_state.user

    st.subheader("🌐 공개 전술 갤러리")
    st.caption("다른 사람들이 공유한 전술을 구경하고 불러올 수 있습니다.")

    if not firebase_ok:
        st.info("Firebase 미설정: 온라인 갤러리를 사용할 수 없습니다.")
        return

    from services.strategy_service import get_public_strategies
    from services.social_service import has_liked, toggle_like, get_comments, add_comment, delete_comment
    from utils.models import strategy_from_firestore

    strategies = get_public_strategies()

    if not strategies:
        st.info("아직 공개된 전술이 없습니다. 전술을 만들고 '전체 공개'로 저장해보세요!")
        return

    st.markdown(f"총 **{len(strategies)}**개의 공개 전술")

    for idx, s in enumerate(strategies):
        strat_id = s["id"]
        name = s.get("name", "(이름 없음)")
        author = s.get("authorName", "?")
        team_name = s.get("teamName", "")
        likes_count = s.get("likesCount", 0)
        updated_ts = s.get("updatedAt", 0)
        phases = s.get("phases", [])
        frame_count = sum(len(p.get("frames", [])) for p in phases)
        phase_count = len(phases)

        # Format date
        if updated_ts:
            date_str = datetime.datetime.fromtimestamp(updated_ts / 1000).strftime("%Y-%m-%d")
        else:
            date_str = ""

        with st.container(border=True):
            col_info, col_actions = st.columns([5, 2])

            with col_info:
                st.markdown(f"### {name}")
                st.caption(
                    f"👤 {author}"
                    + (f" · 🏟️ {team_name}" if team_name else "")
                    + f" · 📅 {date_str}"
                    + f" · {phase_count}단계 {frame_count}프레임"
                    + f" · ♥ {likes_count}"
                )

            with col_actions:
                # Load button
                if st.button("📂 불러오기", key=f"gal_load_{strat_id}", use_container_width=True):
                    loaded = strategy_from_firestore(s)
                    st.session_state.strategy = loaded
                    st.session_state.current_phase_idx = 0
                    st.session_state.current_frame_idx = 0
                    st.session_state.firestore_strategy_id = strat_id
                    if "tb_frame_sel" in st.session_state:
                        del st.session_state["tb_frame_sel"]
                    st.success(f"'{name}' 전술을 불러왔습니다! '전술 보드' 탭에서 확인하세요.")
                    st.rerun()

                # Like button
                liked = has_liked(strat_id, user["uid"])
                like_label = f"♥ {likes_count}" if liked else f"♡ {likes_count}"
                if st.button(like_label, key=f"gal_like_{strat_id}", use_container_width=True):
                    toggle_like(strat_id, user["uid"])
                    st.rerun()

            # Expandable comments
            with st.expander(f"💬 댓글", expanded=False):
                comments = get_comments(strat_id)
                if comments:
                    for c in comments:
                        c_col, d_col = st.columns([9, 1])
                        with c_col:
                            ts = c.get("createdAt", 0)
                            c_date = datetime.datetime.fromtimestamp(ts / 1000).strftime("%m/%d") if ts else ""
                            st.markdown(
                                f"**{c.get('authorName', '?')}**: {c.get('text', '')} "
                                f"<span style='color:#666;font-size:12px;'>{c_date}</span>",
                                unsafe_allow_html=True,
                            )
                        with d_col:
                            if c.get("authorId") == user["uid"]:
                                if st.button("×", key=f"gal_dc_{strat_id}_{c['id']}"):
                                    delete_comment(c["id"])
                                    st.rerun()
                else:
                    st.caption("아직 댓글이 없습니다.")

                comment_text = st.text_input(
                    "댓글 입력", key=f"gal_cmt_{strat_id}",
                    placeholder="댓글을 입력하세요...", label_visibility="collapsed",
                )
                if st.button("등록", key=f"gal_sc_{strat_id}"):
                    if comment_text.strip():
                        add_comment(strat_id, user["uid"], user["displayName"], comment_text.strip())
                        st.rerun()

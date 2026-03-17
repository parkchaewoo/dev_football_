"""전술 갤러리 - 팀 전술 공유 & 공개 전술 열람."""
import streamlit as st
import json
import datetime


def _render_strategy_card(s, idx, prefix, user, team, show_team_badge=True):
    """전술 카드 하나를 렌더링."""
    from services.social_service import has_liked, toggle_like, get_comments, add_comment, delete_comment
    from services.strategy_service import save_strategy, delete_strategy
    from utils.models import strategy_from_firestore, strategy_to_json

    strat_id = s["id"]
    name = s.get("name", "(이름 없음)")
    author = s.get("authorName", "?")
    author_id = s.get("authorId", "")
    team_name = s.get("teamName", "")
    description = s.get("description", "")
    likes_count = s.get("likesCount", 0)
    updated_ts = s.get("updatedAt", 0)
    phases = s.get("phases", [])
    frame_count = sum(len(p.get("frames", [])) for p in phases)
    phase_count = len(phases)
    visibility = s.get("visibility", "")

    date_str = ""
    if updated_ts:
        date_str = datetime.datetime.fromtimestamp(updated_ts / 1000).strftime("%Y-%m-%d")

    vis_icon = {"public": "🌐", "team": "👥", "private": "🔒"}.get(visibility, "")

    with st.container(border=True):
        col_info, col_actions = st.columns([5, 2])

        with col_info:
            st.markdown(f"### {vis_icon} {name}")
            meta = f"👤 {author}"
            if show_team_badge and team_name:
                meta += f" · 🏟️ {team_name}"
            meta += f" · 📅 {date_str}"
            meta += f" · {phase_count}단계 {frame_count}프레임"
            meta += f" · ♥ {likes_count}"
            st.caption(meta)
            if description:
                st.markdown(f"_{description}_")

        with col_actions:
            my_team_id = team.get("id", "") if team else ""
            strat_team_id = s.get("teamId", "")
            is_other_team = my_team_id and strat_team_id != my_team_id

            # === 다른 팀 전술: 원클릭 가져오기가 메인 ===
            if is_other_team:
                if st.button(
                    "⚡ 우리 팀에 가져오기",
                    key=f"{prefix}_import_{strat_id}",
                    use_container_width=True,
                    type="primary",
                ):
                    loaded = strategy_from_firestore(s)
                    strategy_dict = json.loads(strategy_to_json(loaded))
                    strategy_dict["name"] = name  # 원본 이름 유지
                    new_id = save_strategy(
                        strategy_dict,
                        user["uid"],
                        user["displayName"],
                        my_team_id,
                        team.get("name", ""),
                        "team",
                    )
                    if new_id:
                        # 저장 + 에디터에 로드 + 전술보드 전환
                        loaded.name = name
                        st.session_state.strategy = loaded
                        st.session_state.current_phase_idx = 0
                        st.session_state.current_frame_idx = 0
                        st.session_state.firestore_strategy_id = new_id
                        st.session_state.active_tab = "⚽ 전술 보드"
                        st.toast(f"✅ '{name}' → 우리 팀에 저장 완료!")
                        st.rerun()

            # === 같은 팀 또는 팀 없음: 불러오기가 메인 ===
            else:
                if st.button(
                    "📂 불러오기",
                    key=f"{prefix}_load_{strat_id}",
                    use_container_width=True,
                    type="primary",
                ):
                    loaded = strategy_from_firestore(s)
                    st.session_state.strategy = loaded
                    st.session_state.current_phase_idx = 0
                    st.session_state.current_frame_idx = 0
                    st.session_state.firestore_strategy_id = strat_id
                    st.session_state.active_tab = "⚽ 전술 보드"
                    st.rerun()

            # 미리보기 (다른 팀일 때만 — 저장 없이 에디터로)
            if is_other_team:
                if st.button("👁️ 미리보기", key=f"{prefix}_preview_{strat_id}", use_container_width=True):
                    loaded = strategy_from_firestore(s)
                    st.session_state.strategy = loaded
                    st.session_state.current_phase_idx = 0
                    st.session_state.current_frame_idx = 0
                    st.session_state.firestore_strategy_id = None
                    st.session_state.active_tab = "⚽ 전술 보드"
                    st.toast(f"👁️ '{name}' 미리보기 — 저장하려면 사이드바에서 저장하세요")
                    st.rerun()

            # 복사 (같은 팀 전술을 복제할 때)
            if not is_other_team and strat_team_id:
                if st.button("📋 복사", key=f"{prefix}_fork_{strat_id}", use_container_width=True):
                    loaded = strategy_from_firestore(s)
                    strategy_dict = json.loads(strategy_to_json(loaded))
                    strategy_dict["name"] = f"{name} (복사본)"
                    new_id = save_strategy(
                        strategy_dict,
                        user["uid"],
                        user["displayName"],
                        my_team_id,
                        team.get("name", ""),
                        "team",
                    )
                    if new_id:
                        loaded.name = f"{name} (복사본)"
                        st.session_state.strategy = loaded
                        st.session_state.current_phase_idx = 0
                        st.session_state.current_frame_idx = 0
                        st.session_state.firestore_strategy_id = new_id
                        st.toast(f"📋 '{name}' 복사 완료!")
                        st.rerun()

            # Like button
            liked = has_liked(strat_id, user["uid"])
            like_label = f"♥ {likes_count}" if liked else f"♡ {likes_count}"
            if st.button(like_label, key=f"{prefix}_like_{strat_id}", use_container_width=True):
                toggle_like(strat_id, user["uid"])
                st.rerun()

            # Delete (own strategies only)
            if author_id == user["uid"]:
                if st.button("🗑️ 삭제", key=f"{prefix}_del_{strat_id}", use_container_width=True):
                    delete_strategy(strat_id)
                    st.success(f"'{name}' 삭제됨")
                    st.rerun()

        # Comments
        with st.expander("💬 댓글", expanded=False):
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
                            if st.button("×", key=f"{prefix}_dc_{strat_id}_{c['id']}"):
                                delete_comment(c["id"])
                                st.rerun()
            else:
                st.caption("아직 댓글이 없습니다.")

            comment_text = st.text_input(
                "댓글 입력", key=f"{prefix}_cmt_{strat_id}",
                placeholder="댓글을 입력하세요...", label_visibility="collapsed",
            )
            if st.button("등록", key=f"{prefix}_sc_{strat_id}"):
                if comment_text.strip():
                    add_comment(strat_id, user["uid"], user["displayName"], comment_text.strip())
                    st.rerun()


def render_strategy_gallery_page():
    user = st.session_state.user
    team = st.session_state.get("current_team")

    st.subheader("📚 전술 공유")
    st.caption("팀원들과 전술을 공유하고, 다른 팀의 공개 전술도 참고해보세요.")

    from services.strategy_service import get_team_strategies, get_public_strategies

    tab_team, tab_public, tab_my = st.tabs(["👥 팀 전술", "🌐 공개 전술", "📁 내 전술"])

    # ===== 팀 전술 탭 =====
    with tab_team:
        if team and team.get("id"):
            team_strats = get_team_strategies(team["id"])
            if team_strats:
                st.markdown(f"**{team.get('name', '')}** 팀의 전술 **{len(team_strats)}**개")
                for idx, s in enumerate(team_strats):
                    _render_strategy_card(s, idx, "team", user, team, show_team_badge=False)
            else:
                st.info(
                    "아직 팀 전술이 없습니다.\n\n"
                    "전술 보드에서 전술을 만든 후 사이드바에서 '☁️ 팀에 저장'을 눌러보세요!"
                )
        else:
            st.info("팀을 선택하면 팀 전술을 볼 수 있습니다.")

    # ===== 공개 전술 탭 =====
    with tab_public:
        pub_strats = get_public_strategies()
        if pub_strats:
            st.markdown(f"총 **{len(pub_strats)}**개의 공개 전술")
            for idx, s in enumerate(pub_strats):
                _render_strategy_card(s, idx, "pub", user, team, show_team_badge=True)
        else:
            st.info("아직 공개된 전술이 없습니다. 전술을 만들고 '전체 공개'로 저장해보세요!")

    # ===== 내 전술 탭 =====
    with tab_my:
        from services.strategy_service import get_my_strategies
        my_strats = get_my_strategies(user["uid"])
        if my_strats:
            st.markdown(f"내가 만든 전술 **{len(my_strats)}**개")
            for idx, s in enumerate(my_strats):
                _render_strategy_card(s, idx, "my", user, team, show_team_badge=True)
        else:
            st.info("아직 저장한 전술이 없습니다. 전술 보드에서 만들어보세요!")

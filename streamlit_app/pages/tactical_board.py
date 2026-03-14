"""전술 보드 페이지 - 3D 전술 보드, 프레임/단계 관리, 소셜 기능."""
import streamlit as st
import json
import copy
from utils.models import (
    generate_id, Position3D, Frame, Phase,
)
from components.tactical_board import tactical_board_component


def render_tactical_board_page():
    strategy = st.session_state.strategy
    phase_idx = st.session_state.current_phase_idx
    frame_idx = st.session_state.current_frame_idx
    user = st.session_state.user
    firebase_ok = st.session_state.get("firebase_ok", False)

    # Bounds check
    if phase_idx >= len(strategy.phases):
        phase_idx = 0
        st.session_state.current_phase_idx = 0
    current_phase = strategy.phases[phase_idx]
    if frame_idx >= len(current_phase.frames):
        frame_idx = 0
        st.session_state.current_frame_idx = 0
    current_frame = current_phase.frames[frame_idx]

    # Frame-key prefix to prevent Streamlit widget state caching across frames
    fk = f"f{frame_idx}_"

    # ===== Frame controls =====
    frame_col1, frame_col2, frame_col3, frame_col4, frame_col5 = st.columns([2, 2, 2, 2, 4])

    with frame_col1:
        if st.button("+ 프레임 추가", key="tb_add_frame"):
            cur_frame = current_phase.frames[frame_idx]
            new_frame = Frame(
                id=generate_id(),
                players=copy.deepcopy(cur_frame.players),
                ball_position=copy.deepcopy(cur_frame.ball_position),
                ball_peak_height=0.0,
                ball_trajectory="linear",
            )
            current_phase.frames.insert(frame_idx + 1, new_frame)
            st.session_state.current_frame_idx = frame_idx + 1
            # Force selectbox to match new frame index
            st.session_state["tb_frame_sel"] = frame_idx + 1
            st.rerun()

    with frame_col2:
        if len(current_phase.frames) > 1:
            if st.button("- 프레임 삭제", key="tb_del_frame"):
                current_phase.frames.pop(frame_idx)
                new_idx = min(frame_idx, len(current_phase.frames) - 1)
                st.session_state.current_frame_idx = new_idx
                # Force selectbox to match new frame index
                st.session_state["tb_frame_sel"] = new_idx
                st.rerun()

    with frame_col3:
        frame_options = [f"프레임 {i+1}" for i in range(len(current_phase.frames))]
        # Initialize selectbox value if not set
        if "tb_frame_sel" not in st.session_state:
            st.session_state["tb_frame_sel"] = frame_idx
        sel_frame = st.selectbox(
            "프레임", range(len(frame_options)),
            format_func=lambda i: frame_options[i],
            label_visibility="collapsed",
            key="tb_frame_sel",
        )
        if sel_frame != frame_idx:
            st.session_state.current_frame_idx = sel_frame
            st.rerun()

    with frame_col4:
        can_play = len(current_phase.frames) >= 2
        play_label = "▶ 전체 재생" if can_play else "(2프레임 이상)"
        is_playing = st.button(play_label, disabled=not can_play, key="tb_play")

    # When playing, always start from frame 1
    if is_playing:
        st.session_state.current_frame_idx = 0
        frame_idx = 0
        current_frame = current_phase.frames[0]
        fk = "f0_"

    with frame_col5:
        ball_h = st.slider(
            "공 높이",
            min_value=0.0, max_value=8.0, value=float(current_frame.ball_position.y),
            step=0.1, format="%.1fm", label_visibility="collapsed",
            key=fk + "ball_h",
        )
        if abs(ball_h - current_frame.ball_position.y) > 0.01:
            current_frame.ball_position.y = ball_h

    # Ball trajectory and peak height controls (when 2+ frames)
    if len(current_phase.frames) >= 2:
        traj_col1, traj_col2, traj_col3 = st.columns([3, 3, 6])
        with traj_col1:
            trajectory_options = ["일반 (직선)", "롭볼"]
            current_traj = getattr(current_frame, 'ball_trajectory', 'linear')
            traj_idx = 0 if current_traj == "linear" else 1
            traj_sel = st.selectbox(
                "공 궤적 타입",
                trajectory_options,
                index=traj_idx,
                key=fk + "ball_traj",
            )
            new_traj = "linear" if traj_sel == "일반 (직선)" else "parabolic"  # 롭볼 = parabolic
            if new_traj != current_traj:
                current_frame.ball_trajectory = new_traj
                st.rerun()

        with traj_col2:
            if getattr(current_frame, 'ball_trajectory', 'linear') == "parabolic":
                peak_h = st.slider(
                    "최고 높이 (실제 미터)",
                    min_value=0.5, max_value=8.0,
                    value=max(0.5, float(getattr(current_frame, 'ball_peak_height', 3.0))),
                    step=0.5, format="%.1fm",
                    help="로브패스 2~4m, 슈팅 1~2m, 프리킥 5~7m",
                    key=fk + "ball_peak",
                )
                if abs(peak_h - current_frame.ball_peak_height) > 0.01:
                    current_frame.ball_peak_height = peak_h
            else:
                current_frame.ball_peak_height = 0.0

        with traj_col3:
            st.caption(
                "💡 **일반**: 공이 직선으로 이동 | **롭볼**: 공이 올라갔다 내려옴"
            )

    # Prepare frames data for animation (minimal data to reduce memory)
    frames_for_js = []
    if is_playing:
        for f in current_phase.frames:
            frames_for_js.append({
                "players": [
                    {"id": p.id, "position": {"x": p.position.x, "z": p.position.z}}
                    for p in f.players
                ],
                "ball_position": {"x": f.ball_position.x, "y": f.ball_position.y, "z": f.ball_position.z},
                "ball_trajectory": getattr(f, 'ball_trajectory', 'linear'),
                "ball_peak_height": getattr(f, 'ball_peak_height', 0.0),
            })

    # 3D Board (bidirectional component via declare_component)
    drag_result = tactical_board_component(
        players=current_frame.players,
        ball_position=current_frame.ball_position,
        frames=frames_for_js,
        is_playing=is_playing,
        key=f"tb_board_{frame_idx}",
    )

    # Apply drag positions to session state
    if drag_result:
        for dp in drag_result.get("players", []):
            for p in current_frame.players:
                if p.id == dp["id"]:
                    p.position.x = dp["x"]
                    p.position.z = dp["z"]
        ball = drag_result.get("ball")
        if ball:
            current_frame.ball_position.x = ball["x"]
            current_frame.ball_position.z = ball["z"]
        st.rerun()

    # Info
    st.caption(
        f"📋 {strategy.name or '(이름 없음)'} | "
        f"📍 {current_phase.name} | "
        f"🎞️ 프레임 {frame_idx + 1}/{len(current_phase.frames)} | "
        f"⚽ 공 높이: {'지면' if ball_h <= 0.3 else f'{ball_h:.1f}m'}"
    )

    # ===== POSITION EDITOR =====
    with st.expander("📍 선수/공 위치 정밀 편집 (드래그 대신 좌표 입력)", expanded=True):
        st.caption("아래에서 정밀 좌표를 수정하면 3D 보드에 즉시 반영됩니다.")

        st.markdown("**⚽ 공 위치**")
        ball_cols = st.columns(3)
        with ball_cols[0]:
            new_ball_x = st.number_input(
                "공 X (좌우)", min_value=-20.0, max_value=20.0,
                value=float(current_frame.ball_position.x), step=0.5,
                key=fk + "ball_x", format="%.1f",
            )
        with ball_cols[1]:
            new_ball_z = st.number_input(
                "공 Z (상하)", min_value=-10.0, max_value=10.0,
                value=float(current_frame.ball_position.z), step=0.5,
                key=fk + "ball_z", format="%.1f",
            )
        with ball_cols[2]:
            new_ball_y = st.number_input(
                "공 높이 (Y)", min_value=0.0, max_value=8.0,
                value=float(current_frame.ball_position.y), step=0.1,
                key=fk + "ball_y", format="%.1f",
            )
        if (abs(new_ball_x - current_frame.ball_position.x) > 0.01 or
                abs(new_ball_z - current_frame.ball_position.z) > 0.01 or
                abs(new_ball_y - current_frame.ball_position.y) > 0.01):
            current_frame.ball_position.x = new_ball_x
            current_frame.ball_position.z = new_ball_z
            current_frame.ball_position.y = new_ball_y

        st.divider()

        home_players = [p for p in current_frame.players if p.team == "home"]
        away_players = [p for p in current_frame.players if p.team == "away"]

        team_col1, team_col2 = st.columns(2)
        with team_col1:
            st.markdown("**🔴 홈 팀**")
            for p in home_players:
                pc1, pc2 = st.columns(2)
                with pc1:
                    nx = st.number_input(
                        f"#{p.number} X", min_value=-20.0, max_value=20.0,
                        value=float(p.position.x), step=0.5,
                        key=fk + f"p_{p.id}_x", format="%.1f",
                    )
                with pc2:
                    nz = st.number_input(
                        f"#{p.number} Z", min_value=-10.0, max_value=10.0,
                        value=float(p.position.z), step=0.5,
                        key=fk + f"p_{p.id}_z", format="%.1f",
                    )
                if abs(nx - p.position.x) > 0.01 or abs(nz - p.position.z) > 0.01:
                    p.position.x = nx
                    p.position.z = nz

        with team_col2:
            st.markdown("**🔵 어웨이 팀**")
            for p in away_players:
                pc1, pc2 = st.columns(2)
                with pc1:
                    nx = st.number_input(
                        f"#{p.number} X", min_value=-20.0, max_value=20.0,
                        value=float(p.position.x), step=0.5,
                        key=fk + f"p_{p.id}_x", format="%.1f",
                    )
                with pc2:
                    nz = st.number_input(
                        f"#{p.number} Z", min_value=-10.0, max_value=10.0,
                        value=float(p.position.z), step=0.5,
                        key=fk + f"p_{p.id}_z", format="%.1f",
                    )
                if abs(nx - p.position.x) > 0.01 or abs(nz - p.position.z) > 0.01:
                    p.position.x = nx
                    p.position.z = nz

    # ===== SOCIAL SECTION =====
    if firebase_ok and st.session_state.firestore_strategy_id:
        from services.social_service import add_comment, get_comments, delete_comment, toggle_like, has_liked
        import datetime

        strat_id = st.session_state.firestore_strategy_id
        st.divider()

        social_col1, social_col2 = st.columns([1, 4])
        with social_col1:
            liked = has_liked(strat_id, user["uid"])
            like_label = "♥ 좋아요 취소" if liked else "♡ 좋아요"
            if st.button(like_label, key="tb_like_btn"):
                toggle_like(strat_id, user["uid"])
                st.rerun()
        with social_col2:
            st.markdown("**💬 댓글**")

        comments = get_comments(strat_id)
        for c in comments:
            col_cmt, col_del = st.columns([9, 1])
            with col_cmt:
                ts = c.get("createdAt", 0)
                date_str = datetime.datetime.fromtimestamp(ts / 1000).strftime("%m/%d") if ts else ""
                st.markdown(
                    f"**{c.get('authorName', '?')}**: {c.get('text', '')} "
                    f"<span style='color:#666;font-size:12px;'>{date_str}</span>",
                    unsafe_allow_html=True,
                )
            with col_del:
                if c.get("authorId") == user["uid"]:
                    if st.button("×", key=f"tb_del_c_{c['id']}"):
                        delete_comment(c["id"])
                        st.rerun()

        comment_text = st.text_input("댓글 입력", key="tb_comment_input", placeholder="댓글을 입력하세요...")
        if st.button("댓글 등록", key="tb_submit_comment"):
            if comment_text.strip():
                add_comment(strat_id, user["uid"], user["displayName"], comment_text.strip())
                st.rerun()

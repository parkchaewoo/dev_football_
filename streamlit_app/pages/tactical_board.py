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

    # ===== Usage guide =====
    with st.expander("📖 사용 가이드 (처음이시면 클릭!)", expanded=False):
        guide_tab1, guide_tab2, guide_tab3 = st.tabs(["🎮 기본 조작", "📝 실전 예시", "💡 팁"])

        with guide_tab1:
            st.markdown("""
**선수/공 이동**
- 선수나 공을 **클릭한 채로 드래그**하면 위치를 이동할 수 있습니다
- 아래 **좌표 입력**란에서 정밀한 위치를 숫자로 직접 지정할 수도 있습니다

**카메라 조작**
- **빈 코트 영역을 드래그**하면 카메라 각도가 회전됩니다 (3D 시점)
- **스크롤(휠)**로 확대/축소할 수 있습니다
- **빈 곳을 빠르게 두 번 탭(더블클릭)**하면 위에서 내려다보는 2D 시점 ↔ 3D 시점이 전환됩니다

**프레임 관리**
- **+ 프레임 추가**: 현재 프레임을 복사해서 다음 프레임을 만듭니다
- **- 프레임 삭제**: 현재 프레임을 삭제합니다 (최소 1개는 유지)
- **프레임 선택**: 드롭다운으로 원하는 프레임으로 이동합니다

**전체 재생**
- 프레임이 2개 이상이면 **▶ 전체 재생** 버튼이 활성화됩니다
- 재생하면 프레임 1부터 순서대로 선수와 공이 이동하는 애니메이션을 볼 수 있습니다

**공 궤적**
- **일반 (직선)**: 공이 땅 위로 직선 이동합니다
- **롭볼**: 공이 포물선으로 올라갔다 내려옵니다. 최고 높이를 조절할 수 있습니다
""")

        with guide_tab2:
            st.markdown("#### 예시 1: 킥오프 후 원투패스 만들기")
            st.markdown("""
> 킥오프 상황에서 중앙 선수가 원투패스로 전진하는 전술을 만들어 봅시다.

**1단계 — 초기 배치 (프레임 1)**
1. 기본 배치 상태에서 시작합니다
2. 공을 **중앙 선수(#10)** 발 앞으로 드래그합니다

**2단계 — 짧은 패스 (프레임 2)**
1. **+ 프레임 추가**를 클릭합니다
2. 공을 **가까운 동료(#7)** 쪽으로 드래그합니다
3. #10 선수를 앞쪽 빈 공간으로 달리게 드래그합니다 (벽패스 런)

**3단계 — 리턴 패스 (프레임 3)**
1. **+ 프레임 추가**를 다시 클릭합니다
2. 공을 **달려간 #10** 앞으로 드래그합니다
3. ▶ **전체 재생**을 눌러 원투패스 움직임을 확인합니다!
""")
            st.divider()

            st.markdown("#### 예시 2: 코너킥 롭볼 전술")
            st.markdown("""
> 코너킥에서 롭볼로 니어포스트를 공략하는 세트피스를 그려봅시다.

**1단계 — 코너킥 배치 (프레임 1)**
1. 공을 코너 부근 **(X: -20, Z: -10)** 으로 이동합니다
2. 홈팀 선수 1명을 공 옆에 배치 (키커)
3. 나머지 선수를 페널티 에어리어 근처에 배치합니다

**2단계 — 롭볼 진행 (프레임 2)**
1. **+ 프레임 추가** 클릭
2. 공 궤적을 **롭볼**로 변경합니다
3. **최고 높이**를 **4.0m**으로 설정합니다
4. 공을 **니어포스트 (X: -16, Z: -2)** 쪽으로 이동합니다
5. 니어포스트 공략 선수를 해당 위치로 이동시킵니다
6. ▶ **전체 재생**으로 공이 포물선을 그리며 날아가는 것을 확인!
""")
            st.divider()

            st.markdown("#### 예시 3: 단계 기능으로 수비→공격 전환")
            st.markdown("""
> 수비 대형과 공격 전환을 '단계'로 나눠 관리해봅시다.

**1단계 — 수비 대형 (1단계)**
1. 사이드바에서 단계 이름을 **"수비 대형"**으로 입력합니다
2. 선수들을 수비 위치로 배치합니다 (4-0 또는 1-2-1 등)
3. 프레임을 추가해 수비 시 움직임을 그립니다

**2단계 — 공격 전환 (2단계)**
1. 사이드바에서 **➕ 단계 추가**를 클릭합니다
2. 단계 이름을 **"역습 전환"**으로 입력합니다
3. 이전 단계 마지막 프레임의 선수 배치가 복사되어 있습니다
4. 프레임을 추가하며 역습 동선을 그립니다

> 단계별로 전술을 나누면 팀원에게 **수비→공격 전환**을 체계적으로 설명할 수 있습니다!
""")
            st.divider()

            st.markdown("#### 예시 4: 팀원에게 전술 공유하기")
            st.markdown("""
> 완성한 전술을 팀원들과 공유하는 방법입니다.

1. 사이드바에서 **전략 이름**과 **설명**을 입력합니다
2. **공개 범위**를 선택합니다:
   - **팀 내**: 우리 팀원만 볼 수 있음
   - **전체 공개**: 모든 사용자가 갤러리에서 볼 수 있음
   - **나만 보기**: 나만 볼 수 있음
3. **☁️ 팀에 저장**을 클릭합니다
4. 팀원은 **📚 전술 공유** 탭 → **👥 팀 전술**에서 확인할 수 있습니다
5. 다른 팀의 전술이 마음에 들면 **📋 내 전술로 복사** 또는 **💾 우리 팀에 저장**을 할 수 있습니다
""")

        with guide_tab3:
            st.markdown("""
**유용한 팁들**

- **정밀 배치**: 드래그가 어려우면 아래 **좌표 입력**란에서 숫자로 정확히 지정하세요
- **3D로 확인**: 더블클릭으로 3D 시점 전환 후 선수 간격과 깊이감을 확인하세요
- **프레임 복사 활용**: 프레임 추가 시 현재 배치가 그대로 복사됩니다. 조금씩 이동시키면 자연스러운 움직임이 됩니다
- **단계 나누기**: 공격/수비/세트피스 등 상황별로 단계를 나누면 정리가 쉽습니다
- **JSON 백업**: 사이드바 **💾 JSON 저장**으로 로컬에 백업해두면 안전합니다
- **롭볼 높이**: 로브패스 2~4m, 슈팅 1~2m, 프리킥 5~7m이 현실적입니다
""")

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
            st.rerun()

    with frame_col2:
        if len(current_phase.frames) > 1:
            if st.button("- 프레임 삭제", key="tb_del_frame"):
                current_phase.frames.pop(frame_idx)
                new_idx = min(frame_idx, len(current_phase.frames) - 1)
                st.session_state.current_frame_idx = new_idx
                st.rerun()

    with frame_col3:
        frame_options = [f"프레임 {i+1}" for i in range(len(current_phase.frames))]
        sel_frame = st.selectbox(
            "프레임", frame_options,
            index=frame_idx,
            label_visibility="collapsed",
            key=f"tb_frame_sel_{len(current_phase.frames)}",
        )
        sel_idx = frame_options.index(sel_frame) if sel_frame in frame_options else 0
        if sel_idx != frame_idx:
            st.session_state.current_frame_idx = sel_idx
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
        current_traj = getattr(current_frame, 'ball_trajectory', 'linear')
        if current_traj == "parabolic":
            ball_h = st.slider(
                "공 높이",
                min_value=0.0, max_value=8.0, value=float(current_frame.ball_position.y),
                step=0.1, format="%.1fm", label_visibility="collapsed",
                key=fk + "ball_h",
            )
            if abs(ball_h - current_frame.ball_position.y) > 0.01:
                current_frame.ball_position.y = ball_h
        else:
            current_frame.ball_position.y = 0.0
            ball_h = 0.0
            st.caption("⚽ 지면")

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
        key="tb_board",
    )

    # Apply drag/animation-end positions to session state.
    # Skip during playback — the cached drag_result from a previous drag
    # must not interfere. The animation sends its own result when it ends.
    # Only rerun if positions actually changed to avoid infinite loops.
    if drag_result and not is_playing:
        changed = False

        for dp in drag_result.get("players", []):
            for p in current_frame.players:
                if p.id == dp["id"]:
                    if abs(p.position.x - dp["x"]) > 0.001 or abs(p.position.z - dp["z"]) > 0.001:
                        p.position.x = dp["x"]
                        p.position.z = dp["z"]
                        changed = True

        ball = drag_result.get("ball")
        if ball:
            if (abs(current_frame.ball_position.x - ball["x"]) > 0.001 or
                    abs(current_frame.ball_position.z - ball["z"]) > 0.001):
                current_frame.ball_position.x = ball["x"]
                current_frame.ball_position.z = ball["z"]
                changed = True

        if changed:
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
        is_lob = getattr(current_frame, 'ball_trajectory', 'linear') == "parabolic"
        ball_cols = st.columns(3 if is_lob else 2)
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
        new_ball_y = 0.0
        if is_lob:
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

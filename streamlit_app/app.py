import streamlit as st
import json
import copy
from utils.models import (
    create_default_strategy, create_default_phase,
    strategy_to_json, strategy_from_json, strategy_from_firestore,
    generate_id, Phase, Frame,
)
from services.firebase_init import is_firebase_configured

# Firebase 서비스는 지연 import (firebase-admin 미설치 시에도 앱 동작)
firebase_ok = is_firebase_configured()

st.set_page_config(
    page_title="풋살 전술 보드",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ===== SESSION STATE INIT =====
if "strategy" not in st.session_state:
    st.session_state.strategy = create_default_strategy()
if "current_phase_idx" not in st.session_state:
    st.session_state.current_phase_idx = 0
if "current_frame_idx" not in st.session_state:
    st.session_state.current_frame_idx = 0
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
if "user" not in st.session_state:
    st.session_state.user = None
if "current_team" not in st.session_state:
    st.session_state.current_team = None
if "firestore_strategy_id" not in st.session_state:
    st.session_state.firestore_strategy_id = None

# ===== LOGIN SCREEN =====
if not st.session_state.user:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 0;">
            <div style="font-size:80px;">⚽</div>
            <h1>풋살 전술 보드</h1>
            <p style="color:#64748b;">팀원들과 전술을 만들고 공유하세요</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_login = st.columns([1, 2, 1])[1]
    with col_login:
        nick = st.text_input("닉네임을 입력하세요", key="login_nick", placeholder="닉네임")
        if st.button("시작하기", use_container_width=True, type="primary"):
            if nick.strip():
                if firebase_ok:
                    from services.auth_service import create_or_get_user
                    user = create_or_get_user(nick.strip())
                    st.session_state.user = user
                else:
                    st.session_state.user = {
                        "uid": generate_id(),
                        "displayName": nick.strip(),
                        "teams": [],
                    }
                st.session_state.nickname = nick.strip()
                st.rerun()
            else:
                st.warning("닉네임을 입력해주세요.")

        if not firebase_ok:
            st.info("Firebase 미설정: 로컬 모드로 실행됩니다. (팀/공유 기능 제한)")
    st.stop()

# ===== TEAM SELECTION (Firebase only) =====
if firebase_ok and not st.session_state.current_team:
    from services.team_service import create_team, join_team_by_code, get_my_teams, leave_team

    user = st.session_state.user

    st.markdown(f"### 👤 {user['displayName']}님, 환영합니다!")

    teams = get_my_teams(user["uid"])

    if teams:
        st.subheader("내 팀")
        for team in teams:
            col_t1, col_t2 = st.columns([4, 1])
            with col_t1:
                if st.button(
                    f"**{team['name']}** ({len(team.get('members', []))}명) · 코드: {team.get('inviteCode', '')}",
                    key=f"team_{team['id']}",
                    use_container_width=True,
                ):
                    st.session_state.current_team = team
                    st.rerun()
            with col_t2:
                if team.get("leaderId") != user["uid"]:
                    if st.button("탈퇴", key=f"leave_{team['id']}"):
                        leave_team(team["id"], user["uid"])
                        st.rerun()
    else:
        st.info("아직 가입한 팀이 없습니다.")

    st.divider()

    col_c, col_j = st.columns(2)
    with col_c:
        st.subheader("팀 만들기")
        team_name = st.text_input("팀 이름", key="new_team_name")
        team_desc = st.text_input("팀 설명 (선택)", key="new_team_desc")
        if st.button("만들기", use_container_width=True, type="primary"):
            if team_name.strip():
                new_team = create_team(team_name.strip(), team_desc.strip(), user["uid"])
                if new_team:
                    st.session_state.current_team = new_team
                    st.success(f"팀 '{new_team['name']}' 생성! 초대코드: {new_team['inviteCode']}")
                    st.rerun()

    with col_j:
        st.subheader("팀 가입")
        invite_code = st.text_input("초대코드 (6자리)", key="invite_code", max_chars=6)
        if st.button("가입", use_container_width=True):
            if invite_code.strip():
                joined = join_team_by_code(invite_code.strip().upper(), user["uid"])
                if joined:
                    st.session_state.current_team = joined
                    st.success(f"'{joined['name']}' 팀에 가입했습니다!")
                    st.rerun()
                else:
                    st.error("유효하지 않은 초대코드입니다.")

    col_skip = st.columns([1, 2, 1])[1]
    with col_skip:
        if st.button("팀 없이 사용하기", use_container_width=True):
            st.session_state.current_team = {"id": "", "name": "개인", "inviteCode": ""}
            st.rerun()

    col_logout = st.columns([1, 2, 1])[1]
    with col_logout:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.user = None
            st.session_state.nickname = ""
            st.session_state.current_team = None
            st.rerun()

    st.stop()

# If firebase not configured, set a dummy team
if not firebase_ok and not st.session_state.current_team:
    st.session_state.current_team = {"id": "", "name": "로컬", "inviteCode": ""}

# ===== MAIN APP =====
strategy = st.session_state.strategy
phase_idx = st.session_state.current_phase_idx
frame_idx = st.session_state.current_frame_idx
user = st.session_state.user
team = st.session_state.current_team

# Bounds check
if phase_idx >= len(strategy.phases):
    phase_idx = 0
    st.session_state.current_phase_idx = 0
current_phase = strategy.phases[phase_idx]
if frame_idx >= len(current_phase.frames):
    frame_idx = 0
    st.session_state.current_frame_idx = 0
current_frame = current_phase.frames[frame_idx]

# ===== SIDEBAR =====
with st.sidebar:
    st.title("⚽ 풋살 전술 보드")

    # User info
    if user:
        col_user, col_logout = st.columns([3, 1])
        with col_user:
            team_label = team.get("name", "") if team else ""
            st.caption(f"👤 {user['displayName']} · {team_label}")
        with col_logout:
            if st.button("↩", help="팀 목록으로"):
                st.session_state.current_team = None
                st.rerun()

    st.divider()

    # Strategy management
    st.subheader("전략 관리")
    strategy_name = st.text_input(
        "전략 이름",
        value=strategy.name,
        placeholder="전략 이름을 입력하세요"
    )
    if strategy_name != strategy.name:
        strategy.name = strategy_name

    strategy_desc = st.text_area(
        "전략 설명",
        value=strategy.description,
        placeholder="전술 설명을 간단히 입력하세요 (선택)",
        height=68,
    )
    if strategy_desc != strategy.description:
        strategy.description = strategy_desc

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 새 전략", use_container_width=True):
            st.session_state.strategy = create_default_strategy()
            st.session_state.current_phase_idx = 0
            st.session_state.current_frame_idx = 0
            st.session_state.firestore_strategy_id = None
            st.rerun()
    with col2:
        json_str = strategy_to_json(strategy)
        st.download_button(
            "💾 JSON 저장",
            data=json_str,
            file_name=f"{strategy.name or 'strategy'}.json",
            mime="application/json",
            use_container_width=True,
        )

    # Firestore save
    if firebase_ok and team and team.get("id"):
        from services.strategy_service import save_strategy_to_firestore
        visibility = st.selectbox(
            "공개 범위",
            ["team", "public", "private"],
            format_func=lambda v: {"team": "팀 내", "public": "전체 공개", "private": "나만 보기"}[v],
        )
        if st.button("☁️ 팀에 저장", use_container_width=True, type="primary"):
            if strategy.name.strip():
                strategy_dict = json.loads(strategy_to_json(strategy))
                sid = save_strategy_to_firestore(
                    strategy_dict,
                    user["uid"],
                    user["displayName"],
                    team["id"],
                    team["name"],
                    visibility,
                    st.session_state.firestore_strategy_id,
                )
                st.session_state.firestore_strategy_id = sid
                st.success("저장 완료!")
            else:
                st.warning("전략 이름을 입력하세요.")

    # Load from file
    uploaded = st.file_uploader("📂 JSON 불러오기", type=["json"])
    if uploaded:
        try:
            loaded = strategy_from_json(uploaded.read().decode("utf-8"))
            st.session_state.strategy = loaded
            st.session_state.current_phase_idx = 0
            st.session_state.current_frame_idx = 0
            st.session_state.firestore_strategy_id = None
            st.success(f"'{loaded.name}' 불러오기 완료!")
            st.rerun()
        except Exception as e:
            st.error(f"파일 로드 실패: {e}")

    # Load from Firestore
    if firebase_ok:
        from services.strategy_service import get_team_strategies, get_public_strategies

        st.divider()
        load_tab1, load_tab2 = st.tabs(["팀 전술", "공개 전술"])
        with load_tab1:
            if team and team.get("id"):
                team_strats = get_team_strategies(team["id"])
                for s in team_strats:
                    vis_label = {"public": "🌐", "team": "👥", "private": "🔒"}.get(s.get("visibility", ""), "")
                    if st.button(
                        f"{vis_label} {s.get('name', '?')} — {s.get('authorName', '')}",
                        key=f"load_t_{s['id']}",
                        use_container_width=True,
                    ):
                        loaded = strategy_from_firestore(s)
                        st.session_state.strategy = loaded
                        st.session_state.current_phase_idx = 0
                        st.session_state.current_frame_idx = 0
                        st.session_state.firestore_strategy_id = s["id"]
                        st.rerun()
            else:
                st.caption("팀을 선택하면 팀 전술을 볼 수 있습니다.")

        with load_tab2:
            pub_strats = get_public_strategies()
            for s in pub_strats:
                if st.button(
                    f"🌐 {s.get('name', '?')} — {s.get('authorName', '')} ({s.get('teamName', '')})",
                    key=f"load_p_{s['id']}",
                    use_container_width=True,
                ):
                    loaded = strategy_from_firestore(s)
                    st.session_state.strategy = loaded
                    st.session_state.current_phase_idx = 0
                    st.session_state.current_frame_idx = 0
                    st.session_state.firestore_strategy_id = s["id"]
                    st.rerun()

    st.divider()

    # Phase management
    st.subheader("단계 관리")
    phase_names = [f"{p.name}" for p in strategy.phases]
    selected_phase = st.selectbox(
        "현재 단계",
        range(len(phase_names)),
        format_func=lambda i: phase_names[i],
        index=phase_idx,
    )
    if selected_phase != phase_idx:
        st.session_state.current_phase_idx = selected_phase
        st.session_state.current_frame_idx = 0
        st.rerun()

    phase_name = st.text_input(
        "단계 이름",
        value=current_phase.name,
        key="phase_name_input"
    )
    if phase_name != current_phase.name:
        current_phase.name = phase_name

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ 단계 추가", use_container_width=True):
            last_phase = strategy.phases[-1]
            last_frame = last_phase.frames[-1]
            new_phase = Phase(
                id=generate_id(),
                name=f"{len(strategy.phases) + 1}단계",
                description="",
                frames=[Frame(
                    id=generate_id(),
                    players=copy.deepcopy(last_frame.players),
                    ball_position=copy.deepcopy(last_frame.ball_position),
                )],
                order=len(strategy.phases),
            )
            strategy.phases.append(new_phase)
            st.session_state.current_phase_idx = len(strategy.phases) - 1
            st.session_state.current_frame_idx = 0
            st.rerun()
    with col_b:
        if len(strategy.phases) > 1:
            if st.button("🗑️ 단계 삭제", use_container_width=True):
                strategy.phases.pop(phase_idx)
                st.session_state.current_phase_idx = min(phase_idx, len(strategy.phases) - 1)
                st.session_state.current_frame_idx = 0
                st.rerun()

    st.divider()

    # Chat
    st.subheader("💬 채팅")
    st.caption(f"👤 {st.session_state.nickname}")

    chat_container = st.container(height=200)
    with chat_container:
        for msg in st.session_state.chat_messages:
            is_own = msg["author"] == st.session_state.nickname
            with st.chat_message("user" if is_own else "assistant"):
                st.markdown(f"**{msg['author']}**: {msg['text']}")

    chat_text = st.text_input("메시지 입력", key="sidebar_chat_input", placeholder="메시지를 입력하세요...", label_visibility="collapsed")
    if st.button("전송", key="send_chat", use_container_width=True):
        if chat_text.strip():
            st.session_state.chat_messages.append({
                "author": st.session_state.nickname,
                "text": chat_text.strip(),
            })
            st.rerun()


# ===== MAIN CONTENT - TAB NAVIGATION =====
st.session_state.firebase_ok = firebase_ok

tab1, tab2, tab3, tab4 = st.tabs(["⚽ 전술 보드", "📚 전술 공유", "🏥 부상/병원", "📋 게시판"])

with tab1:
    from pages.tactical_board import render_tactical_board_page
    render_tactical_board_page()

with tab2:
    from pages.strategy_gallery import render_strategy_gallery_page
    render_strategy_gallery_page()

with tab3:
    from pages.injury_hospital import render_injury_hospital_page
    render_injury_hospital_page()

with tab4:
    from pages.team_board import render_team_board_page
    render_team_board_page()

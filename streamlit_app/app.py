import streamlit as st
import json
import copy
from dataclasses import asdict
from utils.models import (
    create_default_strategy, create_default_phase,
    strategy_to_json, strategy_from_json,
    generate_id, Position3D, Player, Frame, Phase
)
from components.tactical_board import generate_board_html

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

strategy = st.session_state.strategy
phase_idx = st.session_state.current_phase_idx
frame_idx = st.session_state.current_frame_idx

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

    # Strategy management
    st.subheader("전략 관리")
    strategy_name = st.text_input(
        "전략 이름",
        value=strategy.name,
        placeholder="전략 이름을 입력하세요"
    )
    if strategy_name != strategy.name:
        strategy.name = strategy_name

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 새 전략", use_container_width=True):
            st.session_state.strategy = create_default_strategy()
            st.session_state.current_phase_idx = 0
            st.session_state.current_frame_idx = 0
            st.rerun()
    with col2:
        json_str = strategy_to_json(strategy)
        st.download_button(
            "💾 저장 (JSON)",
            data=json_str,
            file_name=f"{strategy.name or 'strategy'}.json",
            mime="application/json",
            use_container_width=True,
        )

    uploaded = st.file_uploader("📂 전략 불러오기", type=["json"])
    if uploaded:
        try:
            loaded = strategy_from_json(uploaded.read().decode("utf-8"))
            st.session_state.strategy = loaded
            st.session_state.current_phase_idx = 0
            st.session_state.current_frame_idx = 0
            st.success(f"'{loaded.name}' 불러오기 완료!")
            st.rerun()
        except Exception as e:
            st.error(f"파일 로드 실패: {e}")

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
    if not st.session_state.nickname:
        nick = st.text_input("닉네임을 입력하세요", key="nick_input")
        if st.button("입장", use_container_width=True) and nick.strip():
            st.session_state.nickname = nick.strip()
            st.rerun()
    else:
        st.caption(f"👤 {st.session_state.nickname}")

        # Display messages
        chat_container = st.container(height=200)
        with chat_container:
            for msg in st.session_state.chat_messages:
                is_own = msg["author"] == st.session_state.nickname
                with st.chat_message("user" if is_own else "assistant"):
                    st.markdown(f"**{msg['author']}**: {msg['text']}")

        chat_input = st.chat_input("메시지를 입력하세요...")
        if chat_input:
            st.session_state.chat_messages.append({
                "author": st.session_state.nickname,
                "text": chat_input,
            })
            st.rerun()


# ===== MAIN CONTENT =====

# Frame controls
frame_col1, frame_col2, frame_col3, frame_col4, frame_col5 = st.columns([2, 2, 2, 2, 4])

with frame_col1:
    if st.button("➕ 프레임 추가"):
        last_frame = current_phase.frames[-1]
        new_frame = Frame(
            id=generate_id(),
            players=copy.deepcopy(last_frame.players),
            ball_position=copy.deepcopy(last_frame.ball_position),
        )
        current_phase.frames.append(new_frame)
        st.session_state.current_frame_idx = len(current_phase.frames) - 1
        st.rerun()

with frame_col2:
    if len(current_phase.frames) > 1:
        if st.button("🗑️ 프레임 삭제"):
            current_phase.frames.pop(frame_idx)
            st.session_state.current_frame_idx = min(frame_idx, len(current_phase.frames) - 1)
            st.rerun()

with frame_col3:
    frame_options = [f"프레임 {i+1}" for i in range(len(current_phase.frames))]
    sel_frame = st.selectbox(
        "프레임", range(len(frame_options)),
        format_func=lambda i: frame_options[i],
        index=frame_idx,
        label_visibility="collapsed",
    )
    if sel_frame != frame_idx:
        st.session_state.current_frame_idx = sel_frame
        st.rerun()

with frame_col4:
    can_play = len(current_phase.frames) >= 2
    play_label = "▶ 재생" if can_play else "▶ (2프레임 이상 필요)"
    is_playing = st.button(play_label, disabled=not can_play)

with frame_col5:
    ball_h = st.slider(
        "⚽ 공 높이",
        min_value=0.0, max_value=8.0, value=float(current_frame.ball_position.y),
        step=0.1,
        format="%.1fm",
        label_visibility="collapsed",
    )
    if abs(ball_h - current_frame.ball_position.y) > 0.01:
        current_frame.ball_position.y = ball_h


# Prepare frames data for animation
frames_for_js = []
if is_playing:
    for f in current_phase.frames:
        frames_for_js.append(asdict(f))

# 3D Board
board_html = generate_board_html(
    players=current_frame.players,
    ball_position=current_frame.ball_position,
    ball_height=ball_h,
    frames_data=json.dumps(frames_for_js),
    is_playing=is_playing,
)
st.components.v1.html(board_html, height=600)

# Info
st.caption(
    f"📋 {strategy.name or '(이름 없음)'} | "
    f"📍 {current_phase.name} | "
    f"🎞️ 프레임 {frame_idx + 1}/{len(current_phase.frames)} | "
    f"⚽ 공 높이: {'지면' if ball_h <= 0.3 else f'{ball_h:.1f}m'}"
)

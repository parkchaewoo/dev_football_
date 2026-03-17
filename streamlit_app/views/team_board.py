"""팀 게시판 페이지 - 글/비밀글 작성, 운영진 관리."""
import streamlit as st
import datetime


def render_team_board_page():
    user = st.session_state.user
    team = st.session_state.current_team

    st.header("📋 팀 게시판")

    if not team or not team.get("id"):
        st.info("팀에 가입한 후 게시판을 사용할 수 있습니다.")
        return

    from services.board_service import (
        create_post, get_team_posts, get_post,
        update_post, delete_post,
        can_read_secret, can_manage_post,
    )
    from services.team_service import (
        get_team, is_admin, set_admin, remove_admin,
    )

    # Refresh team data for admin info
    team_data = get_team(team["id"])
    if not team_data:
        team_data = team
    user_is_admin = is_admin(team_data, user["uid"])

    # ===== ADMIN MANAGEMENT (리더만) =====
    if team_data.get("leaderId") == user["uid"]:
        with st.expander("👑 운영진 관리", expanded=False):
            members = team_data.get("members", [])
            admins = team_data.get("admins", [])
            st.caption(f"현재 운영진: {len(admins)}명 / 전체 멤버: {len(members)}명")

            for member_uid in members:
                if member_uid == team_data["leaderId"]:
                    continue  # 리더는 항상 운영진
                is_member_admin = member_uid in admins
                col_m, col_btn = st.columns([3, 1])
                with col_m:
                    label = f"{'[운영진]' if is_member_admin else ''} {member_uid[:8]}..."
                    st.text(label)
                with col_btn:
                    if is_member_admin:
                        if st.button("해제", key=f"rm_admin_{member_uid}"):
                            remove_admin(team["id"], member_uid)
                            st.rerun()
                    else:
                        if st.button("지정", key=f"set_admin_{member_uid}"):
                            set_admin(team["id"], member_uid)
                            st.rerun()

    # ===== VIEW STATE =====
    if "board_view" not in st.session_state:
        st.session_state.board_view = "list"  # list, write, detail
    if "board_detail_id" not in st.session_state:
        st.session_state.board_detail_id = None
    if "board_edit_id" not in st.session_state:
        st.session_state.board_edit_id = None

    view = st.session_state.board_view

    # ===== WRITE / EDIT POST =====
    if view == "write":
        _render_write_form(user, team, create_post, update_post)
        return

    # ===== POST DETAIL =====
    if view == "detail" and st.session_state.board_detail_id:
        _render_post_detail(
            user, team_data, user_is_admin,
            get_post, delete_post, can_read_secret, can_manage_post,
        )
        return

    # ===== POST LIST =====
    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.subheader(f"{team_data.get('name', '')} 게시판")
    with col_btn:
        if st.button("✏️ 글쓰기", use_container_width=True, type="primary"):
            st.session_state.board_view = "write"
            st.session_state.board_edit_id = None
            st.rerun()

    posts = get_team_posts(team["id"])

    if not posts:
        st.info("아직 게시글이 없습니다. 첫 글을 작성해보세요!")
        return

    for post in posts:
        is_secret = post.get("isSecret", False)
        ts = post.get("createdAt", 0)
        date_str = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else ""

        secret_icon = "🔒 " if is_secret else ""
        title_text = f"{secret_icon}**{post.get('title', '(제목 없음)')}**"

        col_p1, col_p2, col_p3 = st.columns([5, 2, 2])
        with col_p1:
            if st.button(
                title_text,
                key=f"post_{post['id']}",
                use_container_width=True,
            ):
                st.session_state.board_view = "detail"
                st.session_state.board_detail_id = post["id"]
                st.rerun()
        with col_p2:
            st.caption(post.get("authorName", ""))
        with col_p3:
            st.caption(date_str)


def _render_write_form(user, team, create_post_fn, update_post_fn):
    """글쓰기/수정 폼."""
    edit_id = st.session_state.board_edit_id
    is_edit = edit_id is not None

    st.subheader("✏️ 글 수정" if is_edit else "✏️ 새 글 작성")

    if st.button("← 목록으로"):
        st.session_state.board_view = "list"
        st.rerun()

    # Pre-fill if editing
    default_title = ""
    default_content = ""
    default_secret = False
    if is_edit:
        from services.board_service import get_post
        existing = get_post(edit_id)
        if existing:
            default_title = existing.get("title", "")
            default_content = existing.get("content", "")
            default_secret = existing.get("isSecret", False)

    title = st.text_input("제목", value=default_title, key="board_write_title")
    content = st.text_area("내용", value=default_content, height=200, key="board_write_content")

    is_secret = st.checkbox(
        "🔒 비밀글 (운영진에게 요청/건의)",
        value=default_secret,
        key="board_write_secret",
    )

    password = ""
    if is_secret:
        st.caption("비밀글은 작성자 본인과 팀 운영진만 열람할 수 있습니다.")
        password = st.text_input(
            "비밀번호 (선택 - 외부 접근 차단용)",
            type="password",
            key="board_write_pw",
        )

    submit_label = "수정 완료" if is_edit else "작성 완료"
    if st.button(submit_label, type="primary", use_container_width=True):
        if not title.strip():
            st.warning("제목을 입력하세요.")
            return
        if not content.strip():
            st.warning("내용을 입력하세요.")
            return

        if is_edit:
            update_post_fn(edit_id, title.strip(), content.strip(), is_secret, password)
            st.success("수정 완료!")
        else:
            create_post_fn(
                title.strip(), content.strip(),
                user["uid"], user["displayName"],
                team["id"], is_secret, password,
            )
            st.success("작성 완료!")

        st.session_state.board_view = "list"
        st.session_state.board_edit_id = None
        st.rerun()


def _render_post_detail(user, team_data, user_is_admin, get_post_fn, delete_post_fn, can_read_fn, can_manage_fn):
    """게시글 상세보기."""
    post_id = st.session_state.board_detail_id
    post = get_post_fn(post_id)

    if not post:
        st.error("게시글을 찾을 수 없습니다.")
        if st.button("← 목록으로"):
            st.session_state.board_view = "list"
            st.rerun()
        return

    if st.button("← 목록으로", key="back_to_list"):
        st.session_state.board_view = "list"
        st.session_state.board_detail_id = None
        st.rerun()

    is_secret = post.get("isSecret", False)
    can_read = can_read_fn(post, user["uid"], team_data)

    # Secret post access check
    if is_secret and not can_read:
        st.warning("🔒 비밀글입니다. 작성자 본인 또는 운영진만 열람할 수 있습니다.")
        # Password fallback
        if post.get("passwordHash"):
            pw_key = f"secret_pw_{post_id}"
            if pw_key not in st.session_state:
                st.session_state[pw_key] = False

            if not st.session_state[pw_key]:
                pw = st.text_input("비밀번호 입력", type="password", key="board_detail_pw")
                if st.button("확인", key="board_verify_pw"):
                    from services.board_service import verify_post_password
                    if verify_post_password(post_id, pw):
                        st.session_state[pw_key] = True
                        st.rerun()
                    else:
                        st.error("비밀번호가 일치하지 않습니다.")
                return
        else:
            return

    # Display post
    secret_badge = " 🔒 비밀글" if is_secret else ""
    st.subheader(f"{post.get('title', '')}{secret_badge}")

    ts = post.get("createdAt", 0)
    date_str = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M") if ts else ""
    st.caption(f"작성자: {post.get('authorName', '?')} | {date_str}")

    if is_secret and can_read and user["uid"] != post.get("authorId"):
        st.info("운영진 권한으로 열람 중입니다.")

    st.divider()
    st.markdown(post.get("content", ""))
    st.divider()

    # Edit / Delete (author or admin)
    can_manage = can_manage_fn(post, user["uid"], team_data)
    if can_manage:
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("✏️ 수정", use_container_width=True):
                st.session_state.board_view = "write"
                st.session_state.board_edit_id = post_id
                st.rerun()
        with col_del:
            if st.button("🗑️ 삭제", use_container_width=True):
                delete_post_fn(post_id)
                st.session_state.board_view = "list"
                st.session_state.board_detail_id = None
                st.success("삭제되었습니다.")
                st.rerun()

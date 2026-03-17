"""종합 관리자(슈퍼 어드민) 페이지 — 팀·사용자·전술 등 전체 데이터 관리."""
import streamlit as st
import datetime

from services import local_store
from services.auth_service import is_super_admin


def _fmt_ts(ts) -> str:
    if not ts or not isinstance(ts, (int, float)):
        return "-"
    try:
        return datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def render_super_admin_page():
    user = st.session_state.user
    nickname = st.session_state.nickname

    st.header("👑 종합 관리자")

    if not is_super_admin(nickname):
        st.error("접근 권한이 없습니다.")
        return

    st.caption("환경변수 `SUPER_ADMIN_NICKNAME`으로 지정된 슈퍼 관리자 전용 페이지입니다.")

    section = st.selectbox(
        "관리 항목",
        ["teams", "users", "strategies", "board_posts", "comments", "hospital_reviews", "likes"],
        format_func=lambda k: {
            "teams": "🏟️ 팀 관리",
            "users": "👤 사용자 관리",
            "strategies": "⚽ 전술 관리",
            "board_posts": "📋 게시글 관리",
            "comments": "💬 댓글 관리",
            "hospital_reviews": "🏥 병원 리뷰 관리",
            "likes": "❤️ 좋아요 관리",
        }[k],
    )

    if section == "teams":
        _render_teams()
    elif section == "users":
        _render_users()
    elif section == "strategies":
        _render_strategies()
    elif section == "board_posts":
        _render_board_posts()
    elif section == "comments":
        _render_comments()
    elif section == "hospital_reviews":
        _render_reviews()
    elif section == "likes":
        _render_likes()


# ──────────────────────────────────────
# 팀 관리
# ──────────────────────────────────────
def _render_teams():
    st.subheader("🏟️ 팀 관리")
    teams = local_store.get_all_docs("teams", limit=500)
    st.caption(f"총 {len(teams)}개 팀")

    if not teams:
        st.info("등록된 팀이 없습니다.")
        return

    for team in teams:
        tid = team.get("id", "")
        members = team.get("members", [])
        with st.expander(
            f"**{team.get('name', '?')}** — 멤버 {len(members)}명 · "
            f"코드: {team.get('inviteCode', '')} · "
            f"생성: {_fmt_ts(team.get('createdAt'))}"
        ):
            st.text(f"ID: {tid}")
            st.text(f"리더: {team.get('leaderId', '-')}")
            st.text(f"설명: {team.get('description', '-')}")
            st.text(f"운영진: {', '.join(team.get('admins', []))}")
            st.text(f"멤버: {', '.join(members)}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ 팀 삭제", key=f"sdel_team_{tid}", type="primary"):
                    from services.team_service import delete_team
                    delete_team(tid)
                    st.success(f"팀 '{team.get('name')}' 삭제 완료")
                    st.rerun()
            with col2:
                # 팀의 전술/게시글도 함께 삭제
                if st.button("🗑️ 팀+데이터 전체 삭제", key=f"sdel_team_all_{tid}"):
                    from services.team_service import delete_team
                    # 전술 삭제
                    strats = local_store.query("strategies", [("teamId", "==", tid)])
                    for s in strats:
                        local_store.delete_doc("strategies", s["id"])
                    # 게시글 삭제
                    posts = local_store.query("board_posts", [("teamId", "==", tid)])
                    for p in posts:
                        local_store.delete_doc("board_posts", p["id"])
                    delete_team(tid)
                    st.success(f"팀 '{team.get('name')}' 및 관련 데이터 전체 삭제 완료")
                    st.rerun()


# ──────────────────────────────────────
# 사용자 관리
# ──────────────────────────────────────
def _render_users():
    st.subheader("👤 사용자 관리")
    users = local_store.get_all_docs("users", limit=500)
    st.caption(f"총 {len(users)}명")

    if not users:
        st.info("등록된 사용자가 없습니다.")
        return

    for u in users:
        uid = u.get("id", "")
        team_count = len(u.get("teams", []))
        with st.expander(
            f"**{u.get('displayName', '?')}** — 팀 {team_count}개 · "
            f"가입: {_fmt_ts(u.get('createdAt'))}"
        ):
            st.text(f"UID: {uid}")
            st.text(f"소속 팀: {', '.join(u.get('teams', []))}")

            if st.button("🗑️ 사용자 삭제", key=f"sdel_user_{uid}", type="primary"):
                from services.auth_service import delete_user
                delete_user(uid)
                st.success(f"사용자 '{u.get('displayName')}' 삭제 완료")
                st.rerun()


# ──────────────────────────────────────
# 전술 관리
# ──────────────────────────────────────
def _render_strategies():
    st.subheader("⚽ 전술 관리")
    strats = local_store.get_all_docs("strategies", limit=500)
    st.caption(f"총 {len(strats)}건")

    if not strats:
        st.info("저장된 전술이 없습니다.")
        return

    for s in strats:
        sid = s.get("id", "")
        with st.expander(
            f"**{s.get('name', '?')}** — {s.get('authorName', '?')} · "
            f"{s.get('teamName', '-')} · {_fmt_ts(s.get('updatedAt'))}"
        ):
            st.text(f"ID: {sid}")
            st.text(f"공개: {s.get('visibility', '-')}")
            st.text(f"좋아요: {s.get('likesCount', 0)}")

            if st.button("🗑️ 전술 삭제", key=f"sdel_strat_{sid}", type="primary"):
                local_store.delete_doc("strategies", sid)
                st.success("전술 삭제 완료")
                st.rerun()


# ──────────────────────────────────────
# 게시글 관리
# ──────────────────────────────────────
def _render_board_posts():
    st.subheader("📋 게시글 관리")
    posts = local_store.get_all_docs("board_posts", limit=500)
    st.caption(f"총 {len(posts)}건")

    if not posts:
        st.info("게시글이 없습니다.")
        return

    for p in posts:
        pid = p.get("id", "")
        secret = "🔒 " if p.get("isSecret") else ""
        with st.expander(
            f"{secret}**{p.get('title', '?')}** — {p.get('authorName', '?')} · "
            f"{_fmt_ts(p.get('createdAt'))}"
        ):
            st.text(f"ID: {pid}")
            st.text(f"팀ID: {p.get('teamId', '-')}")
            st.markdown(f"내용: {(p.get('content', '') or '')[:200]}")

            if st.button("🗑️ 게시글 삭제", key=f"sdel_post_{pid}", type="primary"):
                local_store.delete_doc("board_posts", pid)
                st.success("게시글 삭제 완료")
                st.rerun()


# ──────────────────────────────────────
# 댓글 관리
# ──────────────────────────────────────
def _render_comments():
    st.subheader("💬 댓글 관리")
    comments = local_store.get_all_docs("comments", limit=500)
    st.caption(f"총 {len(comments)}건")

    if not comments:
        st.info("댓글이 없습니다.")
        return

    # 일괄 삭제
    if len(comments) > 5:
        if st.button("🗑️ 전체 댓글 삭제", type="primary"):
            local_store.delete_docs_batch("comments", [c["id"] for c in comments])
            st.success(f"{len(comments)}건 삭제 완료")
            st.rerun()

    for c in comments:
        cid = c.get("id", "")
        text = (c.get("text", "") or "")[:60]
        col1, col2, col3 = st.columns([4, 2, 1])
        with col1:
            st.text(f"{text}")
        with col2:
            st.caption(f"{c.get('authorName', '?')} · {_fmt_ts(c.get('createdAt'))}")
        with col3:
            if st.button("삭제", key=f"sdel_cmt_{cid}"):
                local_store.delete_doc("comments", cid)
                st.rerun()


# ──────────────────────────────────────
# 병원 리뷰 관리
# ──────────────────────────────────────
def _render_reviews():
    st.subheader("🏥 병원 리뷰 관리")
    reviews = local_store.get_all_docs("hospital_reviews", limit=500)
    st.caption(f"총 {len(reviews)}건")

    if not reviews:
        st.info("리뷰가 없습니다.")
        return

    if len(reviews) > 5:
        if st.button("🗑️ 전체 리뷰 삭제", type="primary"):
            local_store.delete_docs_batch("hospital_reviews", [r["id"] for r in reviews])
            st.success(f"{len(reviews)}건 삭제 완료")
            st.rerun()

    for r in reviews:
        rid = r.get("id", "")
        with st.expander(
            f"**{r.get('hospitalKeyword', '?')}** — ⭐{r.get('rating', '-')} · "
            f"{r.get('authorName', '?')} · {_fmt_ts(r.get('createdAt'))}"
        ):
            st.text(f"부위: {r.get('bodyPart', '-')}")
            st.markdown(r.get("text", ""))

            if st.button("🗑️ 리뷰 삭제", key=f"sdel_rev_{rid}", type="primary"):
                local_store.delete_doc("hospital_reviews", rid)
                st.success("리뷰 삭제 완료")
                st.rerun()


# ──────────────────────────────────────
# 좋아요 관리
# ──────────────────────────────────────
def _render_likes():
    st.subheader("❤️ 좋아요 관리")
    likes = local_store.get_all_docs("likes", limit=500)
    st.caption(f"총 {len(likes)}건")

    if not likes:
        st.info("좋아요 데이터가 없습니다.")
        return

    if st.button("🗑️ 전체 좋아요 초기화", type="primary"):
        local_store.delete_docs_batch("likes", [lk["id"] for lk in likes])
        st.success(f"{len(likes)}건 삭제 완료")
        st.rerun()

    for lk in likes:
        lid = lk.get("id", "")
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.caption(f"전술: {lk.get('strategyId', '-')}")
        with col2:
            st.caption(f"유저: {lk.get('userId', '-')}")
        with col3:
            if st.button("삭제", key=f"sdel_like_{lid}"):
                local_store.delete_doc("likes", lid)
                st.rerun()

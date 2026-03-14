"""부상 위치 병원 추천 페이지 - 부상 부위 선택 → 네이버 지도 병원 검색."""
import streamlit as st
import urllib.parse

# 풋살에서 자주 발생하는 부상 부위 및 관련 병원 정보
INJURY_DATA = {
    "발목": {
        "icon": "🦶",
        "injuries": ["발목 염좌 (접질림)", "아킬레스건 부상", "발목 골절"],
        "description": "풋살에서 가장 흔한 부상입니다. 급격한 방향 전환이나 상대와의 접촉으로 발생합니다.",
        "hospital_keywords": ["정형외과", "스포츠의학과"],
        "first_aid": "RICE 처치 (Rest, Ice, Compression, Elevation) - 즉시 냉찜질하고 압박 붕대로 감싸세요.",
        "severity_guide": "걸을 수 없을 정도면 응급실, 붓기와 통증이 있으면 정형외과 방문",
    },
    "무릎": {
        "icon": "🦵",
        "injuries": ["전방십자인대(ACL) 파열", "반월상연골 손상", "무릎 인대 염좌", "슬개골 탈구"],
        "description": "급정지, 회전, 점프 착지 시 무릎에 큰 부하가 걸려 발생합니다. 심한 경우 수술이 필요할 수 있습니다.",
        "hospital_keywords": ["정형외과", "스포츠의학과", "무릎전문병원"],
        "first_aid": "무릎을 구부리지 말고 고정하세요. 냉찜질 후 즉시 병원 방문을 권합니다.",
        "severity_guide": "'뚝' 소리가 났거나 무릎이 불안정하면 즉시 정형외과 방문",
    },
    "허벅지/햄스트링": {
        "icon": "🦿",
        "injuries": ["햄스트링 파열/긴장", "대퇴사두근 좌상", "근육 경련"],
        "description": "스프린트나 킥 동작에서 근육이 과도하게 늘어나 발생합니다.",
        "hospital_keywords": ["정형외과", "재활의학과", "스포츠의학과"],
        "first_aid": "즉시 운동을 중단하고 냉찜질하세요. 스트레칭은 금물입니다.",
        "severity_guide": "걸을 수 있으면 재활의학과, 극심한 통증이면 정형외과",
    },
    "어깨": {
        "icon": "💪",
        "injuries": ["어깨 탈구", "회전근개 손상", "쇄골 골절"],
        "description": "골키퍼의 다이빙이나 넘어질 때 팔을 짚으면서 발생합니다.",
        "hospital_keywords": ["정형외과", "어깨전문병원"],
        "first_aid": "탈구 시 억지로 맞추지 말고 응급실로 가세요. 팔걸이로 고정하세요.",
        "severity_guide": "팔을 올릴 수 없으면 응급실, 통증만 있으면 정형외과",
    },
    "손목/손가락": {
        "icon": "🤚",
        "injuries": ["손목 염좌/골절", "손가락 골절", "손가락 탈구"],
        "description": "넘어질 때 손을 짚거나, 골키퍼가 공을 막다가 발생합니다.",
        "hospital_keywords": ["정형외과", "수부외과"],
        "first_aid": "부목으로 고정하고 냉찜질하세요. 변형이 보이면 즉시 응급실.",
        "severity_guide": "변형이 있으면 응급실, 부종과 통증만 있으면 정형외과",
    },
    "머리/얼굴": {
        "icon": "🧠",
        "injuries": ["뇌진탕", "코뼈 골절", "안면 타박상", "찰과상"],
        "description": "머리끼리 충돌하거나 팔꿈치에 맞아 발생합니다. 뇌진탕은 특히 주의가 필요합니다.",
        "hospital_keywords": ["신경외과", "응급실", "이비인후과"],
        "first_aid": "의식이 흐릿하거나 구토가 있으면 즉시 119에 연락하세요.",
        "severity_guide": "의식 변화/구토/심한 두통이면 응급실, 코피가 멈추지 않으면 이비인후과",
    },
    "허리/등": {
        "icon": "🔙",
        "injuries": ["요추 염좌", "디스크 탈출", "근육 좌상"],
        "description": "공을 차는 동작이나 몸싸움에서 허리에 무리가 가면 발생합니다.",
        "hospital_keywords": ["정형외과", "재활의학과", "척추전문병원"],
        "first_aid": "무리하지 말고 편안한 자세로 안정하세요. 하지 저림이 있으면 즉시 병원.",
        "severity_guide": "다리 저림/힘빠짐이 있으면 즉시 정형외과, 단순 통증은 재활의학과",
    },
    "발/발가락": {
        "icon": "👟",
        "injuries": ["발가락 골절", "족저근막염", "발등 타박상"],
        "description": "볼에 밟히거나 강한 슈팅 시 발에 충격이 가해져 발생합니다.",
        "hospital_keywords": ["정형외과", "족부전문병원"],
        "first_aid": "신발을 벗고 냉찜질하세요. 체중을 싣지 마세요.",
        "severity_guide": "걸을 수 없으면 정형외과, 경미한 통증은 며칠 관찰",
    },
}


def render_injury_hospital_page():
    st.header("🏥 부상 위치 병원 추천")
    st.caption("풋살 중 부상을 당했나요? 부상 부위를 선택하면 적합한 병원을 찾아드립니다.")

    # ===== AD PLACEHOLDER (TOP) =====
    with st.container():
        st.markdown(
            """<div style="background: linear-gradient(90deg, #1e3a5f, #2d5a8e);
            border-radius: 8px; padding: 12px 20px; margin-bottom: 16px;
            text-align: center; color: #94a3b8; font-size: 13px;">
            📢 광고 영역 (Ad Space) — 스포츠 용품, 보호대, 테이핑 등
            </div>""",
            unsafe_allow_html=True,
        )

    # ===== BODY PART SELECTOR =====
    st.subheader("부상 부위 선택")

    # Grid of body parts
    cols = st.columns(4)
    selected_part = st.session_state.get("injury_selected_part", None)

    for i, (part_name, data) in enumerate(INJURY_DATA.items()):
        col = cols[i % 4]
        with col:
            is_selected = selected_part == part_name
            btn_type = "primary" if is_selected else "secondary"
            if st.button(
                f"{data['icon']} {part_name}",
                key=f"injury_part_{part_name}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state.injury_selected_part = part_name
                st.rerun()

    if not selected_part:
        st.info("위에서 부상 부위를 선택해주세요.")
        return

    # ===== INJURY DETAILS =====
    data = INJURY_DATA[selected_part]
    st.divider()

    st.subheader(f"{data['icon']} {selected_part} 부상 정보")

    # Description
    st.markdown(f"**설명:** {data['description']}")

    # Common injuries
    st.markdown("**흔한 부상 종류:**")
    for injury in data["injuries"]:
        st.markdown(f"- {injury}")

    # First aid
    st.warning(f"**응급 처치:** {data['first_aid']}")

    # Severity guide
    st.info(f"**병원 선택 가이드:** {data['severity_guide']}")

    # ===== HOSPITAL SEARCH =====
    st.divider()
    st.subheader("🗺️ 주변 병원 찾기")

    # Location input
    location = st.text_input(
        "현재 위치 (지역명)",
        value=st.session_state.get("injury_location", ""),
        placeholder="예: 강남, 잠실, 수원 등",
        key="injury_location_input",
    )
    if location:
        st.session_state.injury_location = location

    # Hospital search links
    st.markdown("**추천 진료과:**")
    for keyword in data["hospital_keywords"]:
        search_query = f"{location} {keyword}" if location else keyword
        encoded_query = urllib.parse.quote(search_query)
        naver_map_url = f"https://map.naver.com/v5/search/{encoded_query}"

        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"🏥 **{keyword}**")
        with col_b:
            st.link_button(
                "네이버 지도에서 검색",
                naver_map_url,
                use_container_width=True,
            )

    # Quick emergency search
    if location:
        st.divider()
        emergency_query = urllib.parse.quote(f"{location} 응급실")
        emergency_url = f"https://map.naver.com/v5/search/{emergency_query}"
        st.link_button(
            "🚨 응급실 검색 (네이버 지도)",
            emergency_url,
            type="primary",
            use_container_width=True,
        )

    # ===== AD PLACEHOLDER (BOTTOM) =====
    st.divider()
    with st.container():
        st.markdown(
            """<div style="background: linear-gradient(90deg, #3a1e1e, #5a2d2d);
            border-radius: 8px; padding: 16px 20px; margin-top: 8px;
            text-align: center; color: #94a3b8; font-size: 13px;">
            📢 광고 영역 (Ad Space) — 스포츠 보험, 부상 예방 프로그램 등
            </div>""",
            unsafe_allow_html=True,
        )

    # ===== PREVENTION TIPS =====
    with st.expander("💡 부상 예방 팁", expanded=False):
        st.markdown("""
        **풋살 부상 예방을 위한 팁:**
        1. **워밍업 필수** — 최소 10분 이상 스트레칭과 가벼운 러닝
        2. **적절한 신발** — 풋살화(실내용/실외용 구분) 착용
        3. **보호대 착용** — 발목, 무릎 보호대로 관절 보호
        4. **수분 보충** — 경기 전/중/후 충분히 수분 섭취
        5. **컨디션 관리** — 피로한 상태에서 무리하지 않기
        6. **바닥 확인** — 미끄러운 바닥이나 이물질 확인
        7. **페어플레이** — 과격한 태클 자제
        """)

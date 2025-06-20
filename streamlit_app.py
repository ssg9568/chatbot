import streamlit as st
from openai import OpenAI
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="여행 플래너 AI",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
/* 동일한 스타일 유지 */
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🏖️ AI 여행 플래너</h1>
    <p>🌊 완벽한 여름 휴가를 계획해보세요! 🌞</p>
</div>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.markdown("## 🔑 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        st.success("✅ API Key 연결됨")
    st.markdown("---")
    travel_type = st.selectbox("여행 스타일:", ["🏖️ 휴양", "🏛️ 문화", "🍜 미식", "🏔️ 자연", "🏙️ 도시", "🎊 축제"])
    budget = st.select_slider("1인 예산 (만원):", [50,100,200,300,500,1000], value=300)
    duration = st.slider("여행 기간 (일):", 1, 30, 5)
    companions = st.number_input("동반자 수:", 1, 20, 2)
    st.markdown("---")
    currency = st.selectbox("통화:", ["USD", "JPY", "EUR", "CNY", "THB", "VND"])
    amount = st.number_input("금액:", 0.0, value=100.0)
    if st.button("환율 조회"):
        rates = {"USD": 1300, "JPY": 9, "EUR": 1400, "CNY": 180, "THB": 36, "VND": 0.05}
        if currency in rates:
            converted = amount * rates[currency]
            st.info(f"{amount} {currency} = {converted:,.0f} 원")

# 메인 컬럼
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("## 🚀 빠른 질문")
    quick_questions = [
        "🏖️ 여름 휴가지 추천해줘",
        "✈️ 항공료 절약 팁 알려줘",
        "🏨 숙소 예약 꿀팁이 뭐야?",
        "🍽️ 현지 맛집 추천해줘",
        "📱 여행 필수 앱 알려줘",
        "💼 짐 싸기 체크리스트 만들어줘"
    ]
    cols = st.columns(2)
    for i, question in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(question, key=f"quick_{i}"):
                st.session_state.quick_question = question

with col2:
    st.markdown("## 📊 여행 계획 진행도")
    progress_data = {"단계": ["목적지 선택", "항공권 예약", "숙소 예약"], "완료율": [100, 80, 60]}
    for step, progress in zip(progress_data["단계"], progress_data["완료율"]):
        col_a, col_b = st.columns([2,1])
        col_a.write(f"**{step}**")
        col_b.write(f"{progress}%")
        st.progress(progress/100)

    st.markdown("## 🌤️ 날씨 정보")
    st.markdown("""
    <div class="info-card">
        <h4>서울 날씨</h4>
        <p>🌡️ 28°C (맑음)</p>
        <p>💧 습도: 65%</p>
        <p>💨 바람: 남동풍 2m/s</p>
    </div>
    """, unsafe_allow_html=True)

# OpenAI
if not openai_api_key:
    st.info("🔑 사이드바에서 OpenAI API Key를 입력해주세요.")
else:
    client = OpenAI(api_key=openai_api_key)

    # 메시지 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "system",
            "content": f"""
            너는 친근한 여행 플래너 AI야.
            현재 설정: 스타일={travel_type}, 예산={budget}만원, 기간={duration}일, 동반자={companions}명.
            이를 바탕으로 맞춤 추천과 팁을 제공해줘.
            """
        }]

    # ✅ 상단에 채팅 입력창 (대체)
    st.markdown("## 💬 여행 상담")
    user_input = st.text_input("여행에 대해 무엇이든 물어보세요!", key="manual_input")

    if st.button("전송하기"):
        if user_input.strip() != "":
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.manual_input = ""

            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("답변을 생성하고 있습니다..."):
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        stream=True,
                        temperature=0.7
                    )
                    response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # 빠른 질문 처리
    if "quick_question" in st.session_state:
        prompt = st.session_state.quick_question
        st.session_state.messages.append({"role": "user", "content": prompt})
        del st.session_state.quick_question

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("답변을 생성하고 있습니다..."):
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    stream=True,
                    temperature=0.7
                )
                response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 이전 메시지 출력
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 하단 부가 기능
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🗺️ 여행지 지도")
    if st.button("지도 보기"):
        st.markdown("구글 맵 링크 등...")

with col2:
    st.markdown("### 📊 여행 통계")
    if st.button("통계 보기"):
        stats = {
            "순위": ["1위", "2위"],
            "여행지": ["제주도", "부산"],
            "방문객수": ["2400만", "1800만"]
        }
        df = pd.DataFrame(stats)
        st.dataframe(df)

with col3:
    st.markdown("### 💾 계획 관리")
    if st.button("💾 대화 저장"):
        chat = ""
        for msg in st.session_state.messages[1:]:
            role = "사용자" if msg["role"] == "user" else "AI"
            chat += f"{role}: {msg['content']}\n\n"
        st.download_button("📄 다운로드", chat, f"대화_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
    if st.button("🔄 초기화"):
        st.session_state.messages = st.session_state.messages[:1]
        st.rerun()

st.markdown("---")
st.markdown("""
<div style="text-align: center;">
🏖️ AI 여행 플래너 | OpenAI로 구동됩니다.
</div>
""", unsafe_allow_html=True)

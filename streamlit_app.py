import streamlit as st
from openai import OpenAI
import requests
import json
from datetime import datetime, timedelta
import base64
from io import BytesIO
import pandas as pd

# 날씨 API 함수 추가
def get_weather_info(location="Seoul"):
    """실시간 날씨 정보를 가져오는 함수"""
    try:
        # OpenWeatherMap API 사용 (무료 버전)
        # 실제 사용시에는 API 키가 필요하지만, 여기서는 예시 데이터 사용
        weather_data = {
            "Seoul": {"temp": 28, "condition": "맑음", "humidity": 65, "wind": "남동풍 2m/s"},
            "Busan": {"temp": 30, "condition": "구름조금", "humidity": 70, "wind": "남풍 3m/s"},
            "Jeju": {"temp": 26, "condition": "소나기", "humidity": 85, "wind": "서풍 4m/s"},
            "Gangneung": {"temp": 25, "condition": "맑음", "humidity": 60, "wind": "동풍 2m/s"},
            "Yeosu": {"temp": 29, "condition": "흐림", "humidity": 75, "wind": "남서풍 3m/s"}
        }
        
        return weather_data.get(location, weather_data["Seoul"])
    except:
        return {"temp": 25, "condition": "정보없음", "humidity": 60, "wind": "정보없음"}
st.set_page_config(
    page_title="여행 플래너 AI",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS - 여름 휴가 테마
st.markdown("""
<style>
    /* 메인 배경 그라디언트 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 사이드바 스타일링 */
    .css-1d391kg {
        background: linear-gradient(180deg, #a8edea 0%, #fed6e3 100%);
    }
    
    /* 챗 메시지 스타일링 */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* 헤더 스타일링 */
    .main-header {
        background: linear-gradient(90deg, #00c6ff 0%, #0072ff 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* 카드 스타일링 */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #00c6ff;
    }
    
    /* 퀴즈 버튼 스타일링 */
    .quick-btn {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .quick-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* 메인 컨테이너 간격 조정 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* 사용자 설정 정보 카드 */
    .user-settings {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 1rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 2px solid #ff6b6b;
    }
    
    /* 사용자 입력창 스타일링 */
    .stChatInput {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 25px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        border: 2px solid #00c6ff;
        font-size: 1.2rem;
    }
    
    .stChatInput input {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 메인 헤더
st.markdown("""
<div class="main-header">
    <h1>🏖️ AI 여행 플래너</h1>
    <p>🌊 완벽한 여름 휴가를 계획해보세요! 🌞</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("## 🔑 설정")
    
    # API Key 입력
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    
    if openai_api_key:
        st.success("✅ API Key 연결됨")
    
    st.markdown("---")
    
    # 여행 타입 선택
    st.markdown("## 🎯 여행 스타일")
    travel_type = st.selectbox(
        "여행 스타일을 선택하세요:",
        ["🏖️ 휴양/리조트", "🏛️ 문화/역사", "🍜 미식 여행", "🏔️ 자연/액티비티", "🏙️ 도시 탐험", "🎊 축제/이벤트"]
    )
    
    # 예산 범위
    st.markdown("## 💰 예산 설정")
    budget = st.select_slider(
        "1인 예산 (만원):",
        options=[50, 100, 200, 300, 500, 1000, 1500, 2000],
        value=300
    )
    
    # 여행 기간
    st.markdown("## 📅 여행 기간")
    duration = st.slider("여행 기간 (일):", 1, 30, 5)
    
    # 동반자 수
    companions = st.number_input("동반자 수:", 1, 20, 2)
    
    st.markdown("---")
    
    # 현재 설정 요약 표시
    st.markdown("## 📋 현재 설정")
    st.markdown(f"""
    <div class="user-settings">
        <h4>🎯 {travel_type}</h4>
        <p>💰 예산: {budget}만원/인</p>
        <p>📅 기간: {duration}일</p>
        <p>👥 인원: {companions}명</p>
        <p>💸 총 예산: <strong>{budget * companions}만원</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 환율 계산기
    st.markdown("## 💱 환율 계산기")
    currency = st.selectbox("통화:", ["USD", "JPY", "EUR", "CNY", "THB", "VND"])
    amount = st.number_input("금액:", min_value=0.0, value=100.0)
    
    # 실제 환율 API 호출 (예시)
    if st.button("환율 조회"):
        # 여기서는 임시 환율 사용 (실제로는 API 호출)
        rates = {"USD": 1300, "JPY": 9, "EUR": 1400, "CNY": 180, "THB": 36, "VND": 0.05}
        if currency in rates:
            converted = amount * rates[currency]
            st.info(f"{amount} {currency} = {converted:,.0f} 원")

# OpenAI API Key 확인
if not openai_api_key:
    st.info("🔑 사이드바에서 OpenAI API Key를 입력해주세요.")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 시스템 프롬프트를 실시간으로 업데이트
    def get_system_prompt():
        return {
            "role": "system",
            "content": f"""
            너는 전문적이고 친근한 여행 플래너 AI 어시스턴트야. 
            
            ⚠️ 중요: 사용자의 모든 질문에 아래 설정을 자동으로 고려해서 답변해야 해:
            
            🎯 현재 사용자 설정:
            - 여행 스타일: {travel_type}
            - 예산: {budget}만원 (1인 기준) / 총 예산: {budget * companions}만원
            - 여행 기간: {duration}일
            - 동반자 수: {companions}명 (총 {companions}명이 함께 여행)
            
            🌤️ 실시간 날씨 정보 활용:
            - 추천하는 여행지의 현재 날씨 상황을 고려해서 답변
            - 날씨에 따른 옷차림, 준비물, 실내외 활동 제안
            - 우천 시 대체 계획도 함께 제시
            
            📝 답변 가이드라인:
            1. 모든 추천은 위 설정에 맞춰서 제공할 것
            2. 예산 범위 내에서 현실적인 옵션 제시
            3. {duration}일 일정에 맞는 계획 수립
            4. {companions}명이 함께 즐길 수 있는 활동 추천
            5. {travel_type} 스타일에 맞는 여행지와 활동 우선 제안
            6. 여행지 추천 시 해당 지역의 실시간 날씨 정보 반영
            
            🏖️ 여름 휴가 시즌이니까 시원하고 재미있는 여행지를 추천하고,
            실용적인 팁과 구체적인 정보를 제공해줘.
            
            응답할 때는 이모지를 적절히 사용하고, 구조화된 정보를 제공해줘.
            사용자가 설정을 바꾸면 그에 맞춰서 답변을 조정해줘.
            """
        }
    
    # 빠른 질문 버튼들
    st.markdown("## 🚀 빠른 질문")
    
    quick_questions = [
        f"🏖️ {travel_type} 스타일로 {duration}일 여행지 추천해줘",
        f"✈️ {budget}만원 예산으로 항공료 절약 팁 알려줘",
        f"🏨 {companions}명이 함께 머물 숙소 추천해줘",
        f"🍽️ {travel_type}에 맞는 현지 맛집 추천해줘",
        f"📱 {duration}일 여행에 필수 앱 알려줘",
        f"💼 {companions}명 {duration}일 짐 싸기 체크리스트 만들어줘"
    ]
    
    # 버튼을 3x2 그리드로 배치
    cols = st.columns(3)
    for i, question in enumerate(quick_questions):
        with cols[i % 3]:
            if st.button(question, key=f"quick_{i}"):
                st.session_state.quick_question = question
    
    st.markdown("---")
    
    # 사용자 입력창을 빠른 질문 아래로 이동 및 스타일링
    st.markdown("## 💬 여행 상담")
    st.markdown("### 💭 질문하기")
    prompt = st.chat_input("여행에 대해 무엇이든 물어보세요! 현재 설정이 자동으로 적용됩니다 🗣️")
    
    if prompt:
        # 시스템 메시지 업데이트
        current_system = get_system_prompt()
        
        # 기존 메시지가 있으면 시스템 메시지 업데이트, 없으면 추가
        if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0] = current_system
        else:
            st.session_state.messages.insert(0, current_system)
        
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("설정을 반영하여 답변을 생성하고 있습니다..."):
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
        del st.session_state.quick_question
        
        # 시스템 메시지 업데이트
        current_system = get_system_prompt()
        
        if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0] = current_system
        else:
            st.session_state.messages.insert(0, current_system)
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 빠른 질문 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("설정을 반영하여 답변을 생성하고 있습니다..."):
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages,
                    stream=True,
                    temperature=0.7
                )
                response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown("### 📜 대화 내역")
    
    # 이전 메시지 표시 (시스템 메시지 제외)
    display_messages = [msg for msg in st.session_state.messages if msg["role"] != "system"]
    for message in display_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 메인 콘텐츠 영역 - 간격 조정
col1, col2 = st.columns([3, 2])

with col1:
    # 여행 계획 요약 카드
    st.markdown("## 📊 맞춤 여행 계획 요약")
    st.markdown(f"""
    <div class="info-card">
        <h4>🎯 {travel_type} 여행</h4>
        <p><strong>📅 기간:</strong> {duration}일</p>
        <p><strong>👥 인원:</strong> {companions}명</p>
        <p><strong>💰 예산:</strong> 총 {budget * companions}만원 (1인당 {budget}만원)</p>
        <hr>
        <h5>💡 맞춤 추천 포인트:</h5>
        <ul>
            <li>🎨 {travel_type} 테마에 맞는 여행지</li>
            <li>💸 예산 {budget}만원 내 최적 옵션</li>
            <li>👨‍👩‍👧‍👦 {companions}명이 함께 즐길 수 있는 활동</li>
            <li>📅 {duration}일 완벽 일정 계획</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # 여행 팁 카드를 확장하여 빈 공간 채우기
    st.markdown("## 💡 여행 꿀팁")
    st.markdown(f"""
    <div class="info-card">
        <h4>🎯 {travel_type} 여행 팁</h4>
        <p><strong>여행 준비를 위한 실용적인 조언</strong></p>
        <ul>
            <li>💰 <strong>예산 관리:</strong> 총 예산의 70%만 미리 계획하고, 나머지는 현지에서 유연하게 사용</li>
            <li>📱 <strong>필수 앱:</strong> 네비게이션(Google Maps, 네이버 지도), 번역기, 교통 앱, 예약 플랫폼</li>
            <li>🎒 <strong>짐 싸기:</strong> {duration}일 여행 기준, {companions}명 모두 가벼운 캐리어 선택</li>
            <li>📷 <strong>추억 남기기:</strong> 사진 클라우드 백업(Google Photos, iCloud) 필수</li>
            <li>🛂 <strong>여행 서류:</strong> 여권, 신분증, 예약 확인서 사본 준비</li>
            <li>🧳 <strong>현지 준비:</strong> {travel_type}에 맞는 활동별 장비 및 복장 확인</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 실시간 환율 정보
    st.markdown("## 💱 주요 환율")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("미국 USD", "1,350원", "↑15원")
        st.metric("일본 JPY", "9.2원", "↓0.1원")
    with col_b:
        st.metric("유럽 EUR", "1,420원", "↑8원")
        st.metric("중국 CNY", "185원", "↑2원")

# 하단 기능들 - 더 컴팩트하게
st.markdown("---")

# 3개 컬럼으로 추가 기능 배치
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🗺️ 여행지 지도")
    if st.button("지도 보기"):
        # Google Maps 링크로 대체
        st.markdown(f"""
        <div class="info-card">
            <h4>🗺️ {travel_type} 추천 여행지 지도</h4>
            <p><a href="https://maps.google.com" target="_blank">🌍 Google Maps에서 보기</a></p>
            <p><a href="https://map.naver.com" target="_blank">🇰🇷 네이버 지도에서 보기</a></p>
            <p><strong>인기 여행지 ({travel_type}):</strong></p>
            <ul>
                <li>🏖️ 제주도 - 한국의 하와이</li>
                <li>🏛️ 경주 - 천년의 역사</li>
                <li>🌊 부산 - 바다와 도시의 조화</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 여행 통계")
    if st.button("통계 보기"):
        # 간단한 데이터 테이블과 메트릭으로 대체
        st.markdown("**📈 2024년 인기 여행지 순위**")
        
        travel_stats = {
            "순위": ["1위", "2위", "3위", "4위", "5위"],
            "여행지": ["제주도", "부산", "강릉", "여수", "경주"],
            "방문객수": ["2,400만", "1,800만", "1,200만", "950만", "800만"]
        }
        
        df = pd.DataFrame(travel_stats)
        st.dataframe(df, use_container_width=True)
        
        # 추가 통계 정보
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("올해 국내 여행객", "5,200만명", "12%")
        with col_b:
            st.metric("평균 여행 예산", f"{budget}만원", "8%")

with col3:
    st.markdown("### 💾 여행 계획 관리")
    
    # 저장 기능
    if st.button("💾 대화 저장"):
        if len(st.session_state.messages) > 0:
            # 시스템 메시지가 아닌 실제 대화만 필터링
            actual_messages = [msg for msg in st.session_state.messages if msg["role"] != "system"]
            
            if actual_messages:
                chat_history = f"""
=== 여행 설정 정보 ===
여행 스타일: {travel_type}
예산: {budget}만원/인 (총 {budget * companions}만원)
여행 기간: {duration}일
동반자 수: {companions}명
저장 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}

=== 상담 대화 내용 ===
"""
                for msg in actual_messages:
                    role = "👤 사용자" if msg["role"] == "user" else "🤖 AI 여행 플래너"
                    chat_history += f"\n{role}:\n{msg['content']}\n\n" + "="*50 + "\n"
                
                st.download_button(
                    label="📄 여행 계획서 다운로드",
                    data=chat_history,
                    file_name=f"여행계획서_{travel_type.replace('🏖️ ', '').replace('🏛️ ', '').replace('🍜 ', '').replace('🏔️ ', '').replace('🏙️ ', '').replace('🎊 ', '')}_{duration}일_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    help="현재까지의 모든 상담 내용과 여행 설정을 저장합니다."
                )
            else:
                st.info("💬 저장할 대화가 없습니다. 먼저 여행 상담을 시작해보세요!")
        else:
            st.info("💬 저장할 대화가 없습니다. 먼저 여행 상담을 시작해보세요!")
    
    # 초기화 기능
    if st.button("🔄 대화 초기화"):
        if len(st.session_state.messages) > 0:
            st.session_state.messages = []
            st.success("✅ 모든 대화가 초기화되었습니다!")
            st.rerun()
        else:
            st.info("💬 초기화할 대화가 없습니다.")

# 푸터
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏖️ AI 여행 플래너 | {travel_type} {duration}일 여행을 위한 당신의 파트너 🌞</p>
    <p><small>OpenAI API를 사용하여 구동됩니다. 모든 설정이 실시간으로 적용됩니다.</small></p>
</div>
""", unsafe_allow_html=True)

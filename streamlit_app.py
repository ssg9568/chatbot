import streamlit as st
from openai import OpenAI
import requests
import json
from datetime import datetime, timedelta
import base64
from io import BytesIO
import pandas as pd

# 페이지 설정
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
</style>
""", unsafe_allow_html=True)

# 메인 헤더 - 더 세련된 디자인
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 20px;">
        <div style="font-size: 4rem;">🏖️</div>
        <div>
            <h1 style="margin: 0; font-size: 3rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                AI 여행 플래너
            </h1>
            <p style="margin: 0; font-size: 1.2rem; opacity: 0.9; font-weight: 300;">
                Smart Travel Planning Assistant
            </p>
        </div>
        <div style="font-size: 4rem;">✈️</div>
    </div>
    <p style="font-size: 1.1rem; margin: 0; opacity: 0.95;">
        🌊 완벽한 여름 휴가를 계획해보세요! 🌞
    </p>
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

# 메인 콘텐츠 영역 - 레이아웃 개선
if not openai_api_key:
    # API Key가 없을 때 가운데 영역 채우기
    st.markdown("## 🌟 여행 플래너 소개")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="info-card" style="text-align: center; padding: 3rem;">
            <h2 style="color: #00c6ff; margin-bottom: 2rem;">🎯 AI 여행 플래너의 특별한 기능</h2>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;">
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border-radius: 15px; color: white;">
                    <h3>🤖 맞춤형 AI 추천</h3>
                    <p>당신의 취향과 예산에 맞는 완벽한 여행 계획</p>
                </div>
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #4ECDC4, #44A08D); border-radius: 15px; color: white;">
                    <h3>💰 실시간 환율</h3>
                    <p>여행 예산 계획을 위한 정확한 환율 정보</p>
                </div>
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #667eea, #764ba2); border-radius: 15px; color: white;">
                    <h3>🌤️ 날씨 & 팁</h3>
                    <p>여행지 날씨와 현지 꿀팁 정보 제공</p>
                </div>
                <div style="padding: 1.5rem; background: linear-gradient(45deg, #f093fb, #f5576c); border-radius: 15px; color: white;">
                    <h3>📱 원클릭 계획</h3>
                    <p>빠른 질문으로 즉시 여행 계획 시작</p>
                </div>
            </div>
            
            <div style="margin-top: 3rem; padding: 2rem; background: rgba(0,198,255,0.1); border-radius: 15px;">
                <h3 style="color: #0072ff;">🔑 시작하기</h3>
                <p style="font-size: 1.1rem; line-height: 1.6;">
                    왼쪽 사이드바에서 <strong>OpenAI API Key</strong>를 입력하시면<br>
                    즉시 AI 여행 상담을 시작할 수 있습니다!
                </p>
                <p style="margin-top: 1rem; opacity: 0.8;">
                    💡 API Key가 없으시다면 <a href="https://platform.openai.com" target="_blank" style="color: #0072ff;">OpenAI 홈페이지</a>에서 발급받으세요
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 하단에 샘플 대화 예시 추가
    st.markdown("## 💬 대화 예시")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card">
            <h4>🏖️ 휴양지 추천 문의</h4>
            <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <strong>사용자:</strong> "가족과 함께 갈 수 있는 조용한 해변 휴양지 추천해줘"
            </div>
            <div style="background: #f0fff0; padding: 15px; border-radius: 10px;">
                <strong>AI:</strong> "🏖️ 가족 여행에 완벽한 휴양지를 추천해드릴게요!<br><br>
                📍 <strong>제주도 함덕해수욕장</strong><br>
                - 얕고 맑은 바다로 아이들에게 안전<br>
                - 주변 카페와 음식점 다양..."
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h4>💰 예산 계획 상담</h4>
            <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <strong>사용자:</strong> "일본 3박4일 여행 예산이 얼마나 들까?"
            </div>
            <div style="background: #f0fff0; padding: 15px; border-radius: 10px;">
                <strong>AI:</strong> "💰 일본 3박4일 예산을 계산해드릴게요!<br><br>
                ✈️ <strong>항공료:</strong> 30-50만원<br>
                🏨 <strong>숙박비:</strong> 20-40만원<br>
                🍜 <strong>식비:</strong> 15-25만원..."
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # API Key가 있을 때는 기존 레이아웃
    col1, col2 = st.columns([2, 1])

    with col1:
        # 빠른 질문 버튼들
        st.markdown("## 🚀 빠른 질문")
        
        quick_questions = [
            "🏖️ 여름 휴가지 추천해줘",
            "✈️ 항공료 절약 팁 알려줘",
            "🏨 숙소 예약 꿀팁이 뭐야?",
            "🍽️ 현지 맛집 추천해줘",
            "📱 여행 필수 앱 알려줘",
            "💼 짐 싸기 체크리스트 만들어줘"
        ]
        
        # 버튼을 3x2 그리드로 배치
        cols = st.columns(3)
        for i, question in enumerate(quick_questions):
            with cols[i % 3]:
                if st.button(question, key=f"quick_{i}"):
                    st.session_state.quick_question = question

    with col2:
        # 여행 진행 상황 표시
        st.markdown("## 📊 여행 계획 진행도")
        
        # 가상의 진행도 데이터
        progress_data = {
            "단계": ["목적지 선택", "항공권 예약", "숙소 예약", "액티비티 계획", "짐 준비"],
            "완료율": [100, 80, 60, 30, 0]
        }
        
        for step, progress in zip(progress_data["단계"], progress_data["완료율"]):
            st.metric(step, f"{progress}%")
            st.progress(progress / 100)
        
        # 날씨 정보 (예시)
        st.markdown("## 🌤️ 날씨 정보")
        st.markdown("""
        <div class="info-card">
            <h4>서울 날씨</h4>
            <p>🌡️ 28°C (맑음)</p>
            <p>💧 습도: 65%</p>
            <p>💨 바람: 남동풍 2m/s</p>
        </div>
        """, unsafe_allow_html=True)

# OpenAI API Key 확인
if not openai_api_key:
    st.info("🔑 사이드바에서 OpenAI API Key를 입력해주세요.")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)
    
    # 세션 상태 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""
                너는 전문적이고 친근한 여행 플래너 AI 어시스턴트야. 
                
                현재 사용자 설정:
                - 여행 스타일: {travel_type}
                - 예산: {budget}만원 (1인 기준)
                - 여행 기간: {duration}일
                - 동반자 수: {companions}명
                
                이 정보를 바탕으로 맞춤형 여행 계획을 제안해줘. 
                여름 휴가 시즌이니까 시원하고 재미있는 여행지를 추천하고,
                실용적인 팁과 구체적인 정보를 제공해줘.
                
                응답할 때는 이모지를 적절히 사용하고, 구조화된 정보를 제공해줘.
                """
            }
        ]
    
    # 빠른 질문 처리
    if "quick_question" in st.session_state:
        prompt = st.session_state.quick_question
        st.session_state.messages.append({"role": "user", "content": prompt})
        del st.session_state.quick_question
        
        # 빠른 질문 표시
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
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
    
    # 채팅 메시지 표시
    st.markdown("## 💬 여행 상담")
    
    # 이전 메시지 표시 (시스템 메시지 제외)
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("여행에 대해 무엇이든 물어보세요! 🗣️"):
        # 사용자 메시지 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # AI 응답 생성
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

# 하단 기능들
st.markdown("---")

# 3개 컬럼으로 추가 기능 배치
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🗺️ 여행지 지도")
    if st.button("지도 보기"):
        # Google Maps 링크로 대체
        st.markdown("""
        <div class="info-card">
            <h4>🗺️ 추천 여행지 지도</h4>
            <p><a href="https://maps.google.com" target="_blank">🌍 Google Maps에서 보기</a></p>
            <p><a href="https://map.naver.com" target="_blank">🇰🇷 네이버 지도에서 보기</a></p>
            <p><strong>인기 여행지:</strong></p>
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
            st.metric("평균 여행 예산", "180만원", "8%")

with col3:
    st.markdown("### 💾 여행 계획 관리")
    
    # 저장 기능
    if st.button("💾 대화 저장"):
        if len(st.session_state.messages) > 1:
            chat_history = ""
            for msg in st.session_state.messages[1:]:  # 시스템 메시지 제외
                role = "사용자" if msg["role"] == "user" else "AI"
                chat_history += f"**{role}**: {msg['content']}\n\n"
            
            st.download_button(
                label="📄 대화 내용 다운로드",
                data=chat_history,
                file_name=f"여행계획_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        else:
            st.info("저장할 대화가 없습니다.")
    
    # 초기화 기능
    if st.button("🔄 대화 초기화"):
        st.session_state.messages = st.session_state.messages[:1]  # 시스템 메시지만 유지
        st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>🏖️ AI 여행 플래너 | 완벽한 여름 휴가를 위한 당신의 파트너 🌞</p>
    <p><small>OpenAI API를 사용하여 구동됩니다.</small></p>
</div>
""", unsafe_allow_html=True)

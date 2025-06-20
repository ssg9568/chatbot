import streamlit as st
from openai import OpenAI

# Streamlit 앱 제목 및 설명
st.title("✈️ 여행 플래너 챗봇")
st.write(
    "이 챗봇은 여행지 추천, 숙소 정보, 액티비티 제안, 예산 계산 등을 도와드립니다! "
    "OpenAI API Key를 입력해주세요."
)

# OpenAI API Key 입력
openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("OpenAI API Key를 입력해주세요.", icon="🔑")
else:
    # OpenAI 클라이언트 생성
    client = OpenAI(api_key=openai_api_key)

    # 대화 메시지 상태 관리
    if "messages" not in st.session_state:
        # 초기 system 메시지에 챗봇의 역할을 명확히 작성
        st.session_state.messages = [
            {
                "role": "system",
                "content": (
                    "너는 친절한 여행 플래너 챗봇이야. "
                    "사용자의 여행 목적, 희망지, 기간, 예산 정보를 단계적으로 질문해서 "
                    "적절한 여행지, 숙소, 액티비티를 추천해주고, 예상 예산도 계산해줘."
                )
            }
        ]

    # 이전 메시지 표시
    for message in st.session_state.messages[1:]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("여행 계획을 도와드릴까요?"):

        # 입력 저장 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # OpenAI 응답 생성 (스트리밍)
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            stream=True,
            temperature=0.7  # 창의성 추가!
        )

        # 응답 표시 및 기록
        with st.chat_message("assistant"):
            response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ✅ 상단에 직접 입력창과 전송 버튼 추가
st.markdown("## 💬 여행 상담")

# 1) 텍스트 입력 상자
user_input = st.text_input(
    "여행에 대해 무엇이든 물어보세요! 🗣️",
    key="manual_input"
)

# 2) 전송 버튼
if st.button("전송하기"):
    if user_input.strip() != "":
        # 입력 저장
        st.session_state.messages.append({"role": "user", "content": user_input})
        # 입력창 초기화
        st.session_state.manual_input = ""
        
        # 사용자 메시지 출력
        with st.chat_message("user"):
            st.markdown(user_input)
        
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

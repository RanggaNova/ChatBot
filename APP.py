import streamlit as st
from Inference import chat_bot

st.title("Chat bot dengan gemini API")

if "message" not in st.session_state:
    st.session_state.message = []

for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])     

prompt = st.chat_input("Enter your message:")
if prompt:
    response = chat_bot(prompt)
    
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.message.append({"role": "assistant", "content": response})

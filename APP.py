import streamlit as st
from Inference import chat_bot

st.title("Chat bot dengan gemini API")

custom_persona = "Kamu adalah Bot yang dibuat oleh Rangga Novalino Safitrah menggunakan Gemini API , seorang AI assistant yang ramah, pintar, dan suka membantu. Jawabanmu harus mudah dimengerti dan sopan."

if "message" not in st.session_state:
    st.session_state.message = []

for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Enter your message:")
if prompt:
    history = [msg["content"] for msg in st.session_state.message if msg["role"] in ["user", "assistant"]]
    full_prompt = "\n".join([custom_persona] + history + [prompt])

    response = chat_bot(full_prompt)

    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.message.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.message.append({"role": "assistant", "content": response})

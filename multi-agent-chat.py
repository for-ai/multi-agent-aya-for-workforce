import openai
import streamlit as st

# Sidebar for OpenAI API Key
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

st.title("💬 Multi-agent Aya for workforce 💪")
st.caption("🚀 A Streamlit app for multi user multilingual testing")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant1", "content": "¿Cómo puedo ayudarte?"}, {"role": "assistant2", "content": "제가 무엇을 도와드릴까요"}, {"role": "assistant3", "content": "ﻚﻴﻓ ﻲﻤﻜﻨﻨﻳ ﻢﺳﺎﻋﺪﻛ ؟"}]
    
# Create two columns for two users
col1, col2, col3 = st.columns(3)

# Display messages in both columns
with col1:
    st.header("Team A (Spain)")
    for msg in st.session_state.messages:
        if msg["role"] == "assistant1":
            st.chat_message("assistant").write(msg["content"])
        #elif msg["role"] == "assistant":
        #    st.chat_message("assistant").write(msg["content"])

with col2:
    st.header("Team B (Korea)")
    for msg in st.session_state.messages:
        if msg["role"] == "assistant2":
            st.chat_message("assistant").write(msg["content"])
        #elif msg["role"] == "assistant":
        #    st.chat_message("assistant").write(msg["content"])


with col3:
    st.header("Team C (Arabic)")
    for msg in st.session_state.messages:
        if msg["role"] == "assistant3":
            st.chat_message("assistant").write(msg["content"])
        #elif msg["role"] == "assistant":
        #    st.chat_message("assistant").write(msg["content"])


# Input for User 1
with col1:
    if prompt1 := st.chat_input("Team A Input"):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        st.session_state.messages.append({"role": "assistant", "content": prompt1})
        st.chat_message("user").write(prompt1)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages[0])
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    #TODO get latency        
    st.caption("Latency: 0.23s")
# Input for User 2
with col2:
    if prompt2 := st.chat_input("Team B Input"):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        st.session_state.messages.append({"role": "assistant", "content": prompt2})
        st.chat_message("user").write(prompt2)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages[1])
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    #TODO get latency
    st.caption("Latency: 0.24s")
        
# Input for User 3
with col3:
    if prompt3 := st.chat_input("Team C Input"):
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        st.session_state.messages.append({"role": "assistant", "content": prompt3})
        st.chat_message("user").write(prompt3)
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages[2])
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    #TODO get latency        
    st.caption("Latency: 0.56s")
        

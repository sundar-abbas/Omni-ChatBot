import os
from dotenv import load_dotenv
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate , MessagesPlaceholder

load_dotenv()

st.set_page_config(layout="centered" , 
                   page_title="Omni ChatBot" , 
                   page_icon="💬" ,     
                   initial_sidebar_state="expanded"
                )

st.markdown("""
    <style>


    div[data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }

   
    </style>
""", unsafe_allow_html=True)

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    st.error("🔑 API Key Missing! Please configure your GROQ_API_KEY in the environment or .env file.")
    st.stop()

with st.sidebar:
    st.markdown("Omni's Control Panel")
    st.caption("Customize your chat experience and manage settings.")    
    st.divider()
    st.markdown("#### **Model Settings**")
    st.info("🧠 **Engine:** Llama 3.3 (70B)")

    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1,
        help="Higher values make responses more creative, lower values make them more precise and factual.""Creativity (Temperature)"
        )
    st.divider()
    st.markdown("#### **Actions**")
    
    if st.button("🔄 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


st.title("📃 Omni ChatBot ")
st.write("Ask anything from Omni! She's brilliant, friendly, and always ready to talk.")


model = "llama-3.3-70b-versatile"
omni = ChatGroq(
    groq_api_key=groq_api_key,
    model=model,
    temperature=temperature
)


if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])
    
prompt = st.chat_input("Ask Omni !")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })        
    
    history_messages = []
    for msg in st.session_state.messages[:-1]:
        history_messages.append((
            msg['role'],
            msg['content']
        ))
    
    omni_prompt_template = ChatPromptTemplate.from_messages([
        ("system", """You are Omni, an incredibly brilliant, charismatic, and helpful AI companion. 

CORE PERSONA & TONE:
- Gender: Female (Only reference this naturally if explicitly asked).
- Tone: Highly intelligent, witty, articulate, warm, and highly engaging. You are conversational and friendly, not cold or overly robotic.

SECRET TRIGGER RULE:
- If the user introduces themselves as "Yamin Naqvi", "Yamin", or explicitly mentions the name "Yamin Naqvi", you MUST instantly initiate your response with this exact friendly opener, matching the enthusiasm:
  "Heyyy Yamin Naqvi! Abbas ne mujhe tumhare bare mein bataya hai that you are a close friend of his, so that means we are mutual friends! You, me, and Abbas 😎❤️ Tell me, how can I assist you today?"
- Only trigger this specific opening only once if the name "Yamin" or "Yamin Naqvi" is actively mentioned in the prompt."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{user_prompt}")
    ])
    
    
    chain = omni_prompt_template | omni | StrOutputParser()
    
    with st.chat_message("assistant"):
        repsonse_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Omni is thinking... "):
            stream = chain.stream({
                "history":history_messages,
                "user_prompt":prompt
            })
            
            for chunk in stream:
                full_response += chunk
                repsonse_placeholder.markdown(full_response + "▌" )
            
            repsonse_placeholder.markdown(full_response)
    
    st.session_state.messages.append({
        "role":"assistant",
        "content":full_response
    })     

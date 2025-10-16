import streamlit as st
import time
from chatbot_logic import EduBot
import os

# Page configuration
st.set_page_config(
    page_title="EduBot - Your AI College Assistant",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS with ALL FIXES
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Chat container */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling - FIXED */
    .header-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: #667eea !important;
        font-size: 2.5em !important;
        font-weight: bold !important;
        margin: 0 !important;
        padding: 0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
    }
    
    .header-subtitle {
        color: #333 !important;
        font-size: 1.1em !important;
        margin-top: 5px !important;
        font-weight: 500 !important;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        padding: 5px 15px !important;
        border-radius: 20px !important;
        font-size: 0.9em !important;
        display: inline-block !important;
        margin-top: 10px !important;
    }
    
    /* Chat messages */
    .user-message {
        background: #667eea;
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0 10px 50px;
        max-width: 70%;
        float: right;
        clear: both;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease-out;
        font-size: 16px;
    }
    
    .bot-message {
        background: white;
        color: #333;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 50px 10px 0;
        max-width: 70%;
        float: left;
        clear: both;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: slideInLeft 0.3s ease-out;
        font-size: 16px;
        line-height: 1.5;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(50px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-50px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Input box styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 12px 20px;
        font-size: 16px;
        background: white;
        color: #333;
    }
    
    /* Button styling - FIXED SIZE AND TEXT */
    .stButton > button {
        background: #667eea !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 10px 20px !important;
        border: none !important;
        font-weight: bold !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        height: 48px !important;
        min-width: 90px !important;
        margin-top: 0px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .stButton > button:hover {
        background: #764ba2 !important;
        transform: scale(1.05) !important;
    }
    
    /* Fix button container alignment */
    .stButton {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: inline-block;
        padding: 10px;
    }
    
    .typing-indicator span {
        height: 10px;
        width: 10px;
        background: #667eea;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
        }
        30% {
            transform: translateY(-10px);
        }
    }
    
    /* Error message */
    .error-message {
        background: #ff6b6b;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Check for API key
if not os.getenv('GEMINI_API_KEY'):
    st.error("⚠️ **Gemini API Key not found!** Please add your API key to the `.env` file.")
    st.stop()

# Initialize session state - FIXED LOOP ISSUE
if 'chatbot' not in st.session_state:
    try:
        st.session_state.chatbot = EduBot()
        st.session_state.chat_history = []
        st.session_state.awaiting_name = True
        st.session_state.conversation_started = False
        st.session_state.message_count = 0  # Track number of messages for unique keys
    except Exception as e:
        st.error(f"⚠️ **Error initializing chatbot:** {str(e)}")
        st.stop()

# Header - FIXED VISIBILITY
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🎓 EduBot</h1>
    <p class="header-subtitle">Your AI-Powered College Assistant</p>
    <span class="ai-badge">✨ Powered by Google Gemini 2.0</span>
</div>
""", unsafe_allow_html=True)

# Initial greeting - ONLY ONCE
if not st.session_state.conversation_started:
    st.session_state.conversation_started = True
    initial_greeting = "Hello! 👋 I'm **EduBot**, your AI-powered college assistant. I'm here to help you with class schedules, faculty details, exam timetables, and college events!"
    st.session_state.chat_history.append(("bot", initial_greeting))
    
    if st.session_state.awaiting_name:
        name_question = "What's your name? 😊"
        st.session_state.chat_history.append(("bot", name_question))

# Display chat history
chat_container = st.container()
with chat_container:
    for sender, message in st.session_state.chat_history:
        if sender == "user":
            st.markdown(f'<div class="user-message">👤 {message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 {message}</div>', unsafe_allow_html=True)

# Add spacing
st.write("")
st.write("")

# Input area with FIXED BUTTON SIZE AND UNIQUE KEYS
col1, col2 = st.columns([5, 1])

with col1:
    # Use unique key for each input widget to avoid state conflicts
    user_input = st.text_input(
        "Type your message here...",
        key=f"user_input_{st.session_state.message_count}",  # ✅ Unique key prevents state errors
        label_visibility="collapsed",
        placeholder="Type your message..."
    )

with col2:
    # Use unique key for each button
    send_button = st.button("Send 📤", key=f"send_btn_{st.session_state.message_count}")

# Process user input - FIXED INFINITE LOOP AND STATE ERROR
if (send_button or user_input) and user_input.strip():
    # Increment message count for next input (creates new widget on rerun)
    st.session_state.message_count += 1  # ✅ Auto-clears input on rerun
    
    # Add user message to chat
    st.session_state.chat_history.append(("user", user_input))
    
    # Show typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown(
        '<div class="bot-message"><div class="typing-indicator"><span></span><span></span><span></span></div></div>',
        unsafe_allow_html=True
    )
    
    # Handle name input
    if st.session_state.awaiting_name:
        st.session_state.awaiting_name = False
        time.sleep(0.5)
        typing_placeholder.empty()
        
        bot_response = st.session_state.chatbot.set_user_name(user_input)
        st.session_state.chat_history.append(("bot", bot_response))
    else:
        # Get Gemini-powered response
        time.sleep(1)
        bot_response = st.session_state.chatbot.get_response(user_input)
        typing_placeholder.empty()
        st.session_state.chat_history.append(("bot", bot_response))
    
    # Rerun to refresh the UI with new message and new input widget
    st.rerun()

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 🤖 About EduBot")
    st.markdown("""
    **Version:** 2.0 (AI-Powered)  
    **AI Model:** Google Gemini 2.0 Flash
    
    **Features:**
    - 📅 Class Schedules
    - 👨‍🏫 Faculty Directory
    - 📝 Exam Timetables
    - 🎉 College Events
    - 💪 Daily Motivation
    - 🧠 Natural Conversations
    
    **Tech Stack:**
    - Python
    - Streamlit
    - Google Gemini API
    - Context-Aware AI
    """)
    
    if st.button("🔄 Clear Chat"):
        st.session_state.chat_history = []
        st.session_state.awaiting_name = True
        st.session_state.conversation_started = False
        st.session_state.message_count = 0
        st.session_state.chatbot.clear_history()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 Try Asking:")
    st.markdown("""
    - "What's my schedule today?"
    - "Tell me about Dr. Rajesh Kumar"
    - "When are the exams?"
    - "What events are coming up?"
    - "I need some motivation"
    - "Compare Monday and Friday schedules"
    """)
    
    st.markdown("---")
    st.markdown("🔒 **Privacy:** Your conversations are processed securely by Google Gemini API.")

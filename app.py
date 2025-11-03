"""
Clinical AI Assistant - Streamlit Web Interface
A beautiful, modern UI for medical question answering with RAG
"""

import streamlit as st
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from model.rag_model import get_or_create_vector_store, query_rag_system

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Clinical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical-themed styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #0066cc;
        --secondary-color: #00a86b;
        --background-color: #f8f9fa;
        --text-color: #2c3e50;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #0066cc 0%, #00a86b 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        max-width: 80%;
        margin-left: auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: white;
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin: 1rem 0;
        max-width: 80%;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Source card styling */
    .source-card {
        background: white;
        border-left: 4px solid #0066cc;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    
    .source-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .source-title {
        font-weight: 600;
        color: #0066cc;
        margin-bottom: 0.3rem;
    }
    
    .source-file {
        font-size: 0.9rem;
        color: #666;
    }
    
    /* Metrics styling */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0066cc;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #0066cc 0%, #00a86b 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #0066cc;
        box-shadow: 0 0 0 2px rgba(0,102,204,0.1);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'total_response_time' not in st.session_state:
    st.session_state.total_response_time = 0
if 'vectordb' not in st.session_state:
    st.session_state.vectordb = None
if 'vectordb_loaded' not in st.session_state:
    st.session_state.vectordb_loaded = False

# Header
st.markdown("""
<div class="main-header">
    <h1>🏥 Clinical AI Assistant</h1>
    <p>Evidence-based medical answers powered by GPT-4o and Advanced RAG</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    
    # API Key input
    api_key_input = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-proj-...",
        help="Enter your OpenAI API key here"
    )
    
    # Use input key if provided, otherwise try env
    if api_key_input:
        api_key = api_key_input
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.success("✅ API Key Set from Input")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✅ API Key Loaded from .env")
        else:
            st.error("❌ No API Key Found")
            st.warning("Please enter your API key above")
    
    st.markdown("---")
    st.markdown("### ⚙️ Model Settings")
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1, 
                           help="Lower = more focused, Higher = more creative")
    max_tokens = st.slider("Max Tokens", 500, 2000, 1000, 100,
                          help="Maximum length of response")
    
    st.markdown("---")
    
    # Retrieval settings
    st.markdown("### 🔍 Retrieval Settings")
    num_sources = st.slider("Number of Sources", 3, 15, 8, 1,
                            help="How many document chunks to retrieve")
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Session Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{st.session_state.query_count}</div>
            <div class="metric-label">Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_time = (st.session_state.total_response_time / st.session_state.query_count 
                   if st.session_state.query_count > 0 else 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_time:.1f}s</div>
            <div class="metric-label">Avg Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.query_count = 0
        st.session_state.total_response_time = 0
        st.rerun()
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About"):
        st.markdown("""
        **Clinical AI Assistant** uses:
        - 🤖 GPT-4o for responses
        - 🔍 Advanced RAG with MMR
        - 📚 Medical literature database
        - 🎯 Source citations
        
        Built with LangChain & Streamlit
        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 💬 Conversation")
    
    # Initialize vector store (with loading indicator)
    if not st.session_state.vectordb_loaded:
        with st.spinner("🔄 Initializing vector store... (This may take a moment on first run)"):
            try:
                st.session_state.vectordb = get_or_create_vector_store()
                st.session_state.vectordb_loaded = True
                st.success("✅ Vector store ready!")
                time.sleep(1)
            except Exception as e:
                st.error(f"❌ Error loading vector store: {str(e)}")
                st.stop()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <strong>🤖 Assistant:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    user_question = st.text_input(
        "Ask a medical question:",
        placeholder="e.g., What are the best predictive algorithms for heart attack detection?",
        key="user_input"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
    with col_btn1:
        submit_button = st.button("🚀 Ask", use_container_width=True)
    with col_btn2:
        example_button = st.button("💡 Example", use_container_width=True)
    
    # Handle example button
    if example_button:
        user_question = "What are the best predictive algorithms for heart attack detection?"
        st.session_state.user_input = user_question
    
    # Process query
    if submit_button and user_question:
        # Check if API key is set
        if not api_key:
            st.error("❌ Please enter your OpenAI API key in the sidebar first!")
        else:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_question,
                "timestamp": datetime.now()
            })
            
            # Get response with timing
            with st.spinner("🤔 Thinking..."):
                start_time = time.time()
                try:
                    result = query_rag_system(
                        st.session_state.vectordb,
                        user_question
                    )
                    response_time = time.time() - start_time
                    
                    # Update statistics
                    st.session_state.query_count += 1
                    st.session_state.total_response_time += response_time
                    
                    # Add assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result['answer'],
                        "sources": result['sources'],
                        "response_time": response_time,
                        "timestamp": datetime.now()
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    # Show helpful message for API key errors
                    if "401" in str(e) or "invalid_api_key" in str(e):
                        st.warning("💡 This looks like an API key issue. Please check your key in the sidebar.")

with col2:
    st.markdown("### 📚 Sources")
    
    # Display sources from the last assistant message
    if st.session_state.messages:
        last_assistant_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_assistant_msg = msg
                break
        
        if last_assistant_msg and "sources" in last_assistant_msg:
            sources = last_assistant_msg["sources"]
            
            if sources:
                st.markdown(f"**{len(sources)} sources cited:**")
                
                for i, source in enumerate(sources, 1):
                    disease = source.get('disease', 'Unknown')
                    file = source.get('file', 'Unknown')
                    
                    # Color code by disease
                    color_map = {
                        'covid': '#ff6b6b',
                        'diabetes': '#4ecdc4',
                        'heart attack': '#ff6348',
                        'knee injury': '#95e1d3'
                    }
                    border_color = color_map.get(disease.lower(), '#0066cc')
                    
                    st.markdown(f"""
                    <div class="source-card" style="border-left-color: {border_color};">
                        <div class="source-title">📄 Source {i}</div>
                        <div><strong>Disease:</strong> {disease.title()}</div>
                        <div class="source-file">{file}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Response time
                if "response_time" in last_assistant_msg:
                    st.markdown("---")
                    st.info(f"⏱️ Response time: {last_assistant_msg['response_time']:.2f}s")
            else:
                st.info("No sources available for this response.")
        else:
            st.info("Ask a question to see sources!")
    else:
        st.info("👋 Welcome! Ask a medical question to get started.")
        
        # Example questions
        st.markdown("---")
        st.markdown("**💡 Example Questions:**")
        examples = [
            "What are the symptoms of COVID-19?",
            "How to manage Type 2 diabetes?",
            "Best exercises for knee injury recovery?",
            "Machine learning in heart disease prediction?"
        ]
        for ex in examples:
            st.markdown(f"• {ex}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>⚕️ Clinical AI Assistant | Powered by GPT-4o & Advanced RAG | For educational purposes only</small>
</div>
""", unsafe_allow_html=True)

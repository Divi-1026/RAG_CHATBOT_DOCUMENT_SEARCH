import streamlit as st
from dotenv import load_dotenv
 
from pdf_qa_backend import (
    create_vector_store,
    load_website,
    load_uploaded_file,
    answer_question
)
 
load_dotenv()
 
st.set_page_config(page_title="WebDoc-AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
 
st.markdown("""
<style>
/* ============================================================
   SKY-BLUE LIGHT THEME
   ============================================================ */
 
/* ---- Streamlit chrome cleanup (keep sidebar reopen control!) ---- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
 
/* Keep the header element (it hosts the sidebar reopen arrow) but make
   it blend into the page so it stays clean. Hiding the whole header was
   the reason a collapsed sidebar could never be reopened. */
header[data-testid="stHeader"] {
    background: transparent;
}
 
/* =========================================================
   SIDEBAR OPEN + CLOSE CONTROLS — always visible & clickable
   Covers new + old Streamlit testid / kind names so the
   sidebar can always be collapsed AND reopened.
   ========================================================= */
 
/* OPEN arrow (shown when the sidebar is collapsed) */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stExpandSidebarButton"],
header[data-testid="stHeader"] button[kind="header"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
    z-index: 1000000 !important;
    pointer-events: auto !important;
}
 
[data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button,
[data-testid="stExpandSidebarButton"] {
    background: #0ea5e9 !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    box-shadow: 0 4px 14px rgba(14,165,233,0.35) !important;
}
 
/* CLOSE (X) button (shown when the sidebar is expanded) */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebar"] button[kind="header"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: inline-flex !important;
    pointer-events: auto !important;
    color: #0369a1 !important;
}
 
/* Make every arrow/X icon clearly visible */
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg {
    color: #ffffff !important;
    fill: #ffffff !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebar"] button[kind="header"] svg {
    color: #0369a1 !important;
    fill: #0369a1 !important;
}
 
/* ---- App background (single solid sky color so header & chat areas match) ---- */
.stApp {
    background: #e0f2fe;
}
 
.block-container {
    max-width: 920px;
    padding-top: 25px;
    padding-bottom: 120px;
}
 
/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #eff6ff 100%);
    border-right: 1px solid #bae6fd;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span {
    color: #1e293b;
}
 
.sidebar-title {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 18px;
}
 
[data-testid="stSidebar"] label {
    color: #334155 !important;
    font-weight: 600;
}
 
/* radio selected accent -> sky blue (best-effort across versions) */
[data-testid="stSidebar"] [data-baseweb="radio"] [aria-checked="true"] {
    border-color: #0ea5e9 !important;
    background-color: #0ea5e9 !important;
}
 
/* ---- Status box / cards ---- */
.status-box {
    font-size: 13px;
    color: #0c4a6e;
    background: #e0f2fe;
    border: 1px solid #7dd3fc;
    padding: 12px;
    border-radius: 12px;
    word-break: break-word;
    box-shadow: 0 2px 8px rgba(14,165,233,0.08);
}
 
.history-item {
    padding: 10px 12px;
    border-radius: 10px;
    background: #ffffff;
    border: 1px solid #bae6fd;
    margin-bottom: 8px;
    font-size: 14px;
    color: #334155;
}
 
/* ---- Titles ---- */
.app-title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 4px;
}
 
.app-subtitle {
    text-align: center;
    font-size: 15px;
    color: #0284c7;
    margin-bottom: 35px;
}
 
/* ---- Empty state ---- */
.empty-box {
    text-align: center;
    margin-top: 130px;
}
 
.empty-box h1 {
    font-size: 32px;
    font-weight: 800;
    color: #0f172a;
}
 
.empty-box p {
    color: #64748b;
    font-size: 15px;
}
 
/* ---- Buttons ---- */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
    color: white;
    border-radius: 10px;
    border: none;
    height: 42px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(14,165,233,0.25);
    transition: all 0.2s ease;
}
 
.stButton > button:hover {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: white;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(14,165,233,0.35);
}
 
/* ---- Inputs ---- */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background: #ffffff !important;
    border: 1px solid #bae6fd !important;
    border-radius: 10px !important;
    color: #0f172a !important;
}
[data-testid="stSidebar"] input:focus,
[data-testid="stSidebar"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.15) !important;
}
 
/* file uploader dropzone */
[data-testid="stFileUploader"] section {
    background: #ffffff;
    border: 1px dashed #7dd3fc;
    border-radius: 12px;
}
 
/* ---- Chat messages ---- */
[data-testid="stChatMessage"] {
    background: #ffffff;
    border: 1px solid #e0f2fe;
    border-radius: 14px;
    padding: 6px 14px;
    margin-bottom: 6px;
    box-shadow: 0 2px 8px rgba(14,165,233,0.06);
}
[data-testid="stChatMessage"] p {
    color: #1e293b;
}
 
/* ---- Chat input ---- */
div[data-testid="stChatInput"] {
    max-width: 860px;
    margin: auto;
}
 
/* Make the bottom bar behind the chat input the SAME sky color as the
   rest of the main area (no more white band) */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
div[data-testid="stChatInput"] {
    background: transparent !important;
}
 
div[data-testid="stChatInput"] textarea {
    border-radius: 16px !important;
    background: #ffffff !important;
    border: 1px solid #bae6fd !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.15) !important;
}
 
/* SEND (submit) button — always visible, sky-blue, white arrow icon.
   Covers new + old Streamlit selectors. */
[data-testid="stChatInputSubmitButton"],
[data-testid="stChatInput"] button {
    visibility: visible !important;
    opacity: 1 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: #0ea5e9 !important;
    border: none !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 8px rgba(14,165,233,0.30) !important;
    width: 34px !important;
    height: 34px !important;
    min-width: 34px !important;
}
[data-testid="stChatInputSubmitButton"]:hover,
[data-testid="stChatInput"] button:hover {
    background: #0284c7 !important;
}
[data-testid="stChatInputSubmitButton"]:disabled,
[data-testid="stChatInput"] button:disabled {
    background: #7dd3fc !important;
    opacity: 1 !important;
}
[data-testid="stChatInputSubmitButton"] svg,
[data-testid="stChatInput"] button svg,
[data-testid="stChatInputSubmitButton"] svg path,
[data-testid="stChatInput"] button svg path {
    color: #ffffff !important;
    fill: #ffffff !important;
}
 
/* ---- Responsive ---- */
@media (max-width: 768px) {
    .block-container {
        padding-left: 12px;
        padding-right: 12px;
        padding-bottom: 100px;
    }
    .app-title { font-size: 26px; }
    .app-subtitle { font-size: 13px; }
    .empty-box { margin-top: 70px; }
    .empty-box h1 { font-size: 24px; }
    div[data-testid="stChatInput"] { max-width: 100%; }
}
 
@media (max-width: 480px) {
    .app-title { font-size: 22px; }
    .app-subtitle { font-size: 12px; }
    .empty-box h1 { font-size: 20px; }
}
</style>
""", unsafe_allow_html=True)
 
 
st.markdown('<div class="app-title">🤖 WebDoc-AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Chat with websites and documents using ChatGroq + FAISS + Ollama Embeddings</div>',
    unsafe_allow_html=True
)
 
 
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
 
if "source_type" not in st.session_state:
    st.session_state.source_type = None
 
if "source_name" not in st.session_state:
    st.session_state.source_name = None
 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
 
if "processed_file_names" not in st.session_state:
    st.session_state.processed_file_names = []
 
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
 
 
def save_current_chat():
    if not st.session_state.chat_history:
        return
 
    title = "New Chat"
 
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            title = msg["content"][:45]
            break
 
    chat_data = {
        "title": title,
        "source_type": st.session_state.source_type,
        "source_name": st.session_state.source_name,
        "messages": st.session_state.chat_history.copy()
    }
 
    if len(st.session_state.all_chats) == 0:
        st.session_state.all_chats.insert(0, chat_data)
    else:
        st.session_state.all_chats[0] = chat_data
 
 
def start_new_chat():
    save_current_chat()
    st.session_state.chat_history = []
 
 
def clear_all():
    st.session_state.vector_store = None
    st.session_state.source_type = None
    st.session_state.source_name = None
    st.session_state.chat_history = []
    st.session_state.processed_file_names = []
    st.session_state.all_chats = []
 
 
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 WebDoc-AI</div>', unsafe_allow_html=True)
 
    if st.button("➕ New Chat"):
        start_new_chat()
        st.rerun()
 
    mode = st.radio(
        "Choose Source",
        ["Website", "Document"]
    )
 
    st.markdown("---")
 
    if mode == "Website":
        st.markdown("### 🌐 Website")
        url = st.text_input(
            "Paste website URL",
            placeholder="https://example.com"
        )
 
        if st.button("Load Website"):
            if not url:
                st.warning("Please enter website URL.")
            else:
                try:
                    with st.spinner("Reading website and creating knowledge base..."):
                        docs = load_website(url)
 
                        st.session_state.vector_store = create_vector_store(docs)
                        st.session_state.source_type = "Website"
                        st.session_state.source_name = url
                        st.session_state.chat_history = []
                        st.session_state.processed_file_names = []
 
                    st.success("Website loaded successfully.")
                    st.rerun()
 
                except Exception as e:
                    st.error(f"Error: {e}")
 
    else:
        st.markdown("### 📄 Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF, TXT, or DOCX",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True
        )
 
        if uploaded_files:
            current_file_names = [file.name for file in uploaded_files]
 
            if current_file_names != st.session_state.processed_file_names:
                try:
                    with st.spinner("Processing uploaded document automatically..."):
                        all_docs = []
 
                        for file in uploaded_files:
                            all_docs.extend(load_uploaded_file(file))
 
                        st.session_state.vector_store = create_vector_store(all_docs)
                        st.session_state.source_type = "Document"
                        st.session_state.source_name = ", ".join(current_file_names)
                        st.session_state.processed_file_names = current_file_names
                        st.session_state.chat_history = []
 
                    st.success("Document processed automatically.")
                    st.rerun()
 
                except Exception as e:
                    st.error(f"Error: {e}")
 
    st.markdown("---")
 
    if st.session_state.vector_store:
        st.markdown(
            f"""
            <div class="status-box">
                ✅ <b>Active Source</b><br><br>
                Type: <b>{st.session_state.source_type}</b><br>
                Source: {st.session_state.source_name}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info("No source loaded yet.")
 
    st.markdown("---")
 
    st.markdown("### 🕘 History")
 
    if st.session_state.all_chats:
        for idx, chat in enumerate(st.session_state.all_chats):
            title = chat["title"]
 
            if st.button(title, key=f"chat_history_{idx}"):
                st.session_state.chat_history = chat["messages"].copy()
                st.session_state.source_type = chat["source_type"]
                st.session_state.source_name = chat["source_name"]
                st.rerun()
    else:
        st.caption("No history yet.")
 
    st.markdown("---")
 
    if st.button("🗑 Clear Everything"):
        clear_all()
        st.rerun()
 
 
if len(st.session_state.chat_history) == 0:
    st.markdown(
        """
        <div class="empty-box">
            <h1>What would you like to know?</h1>
            <p>Upload a document or load a website from the sidebar, then start chatting.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
 
 
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])
 
        if msg.get("page_info"):
            st.caption(msg["page_info"])
 
 
question = st.chat_input("Ask anything from the selected source...")
 
if question:
    if st.session_state.vector_store is None:
        st.warning("Please load a website or upload a document first.")
    else:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
 
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)
 
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    answer, page_info = answer_question(
                        st.session_state.vector_store,
                        question,
                        st.session_state.source_type
                    )
 
                    st.markdown(answer)
 
                    if page_info:
                        st.caption(page_info)
 
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "page_info": page_info
                    })
 
                    save_current_chat()
 
                except Exception as e:
                    st.error(f"Error: {e}")
 
        st.rerun()
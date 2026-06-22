import streamlit as st
from dotenv import load_dotenv

from pdf_qa_backend import (
    create_vector_store,
    load_website,
    load_uploaded_file,
    answer_question
)

load_dotenv()

st.set_page_config(page_title="RAG ChatBot", page_icon="🤖", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}

.stApp {
    background: #ffffff;
}

.block-container {
    max-width: 920px;
    padding-top: 25px;
    padding-bottom: 120px;
}

[data-testid="stSidebar"] {
    background: #f7f7f8;
    border-right: 1px solid #e5e7eb;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 18px;
}

.status-box {
    font-size: 13px;
    color: #374151;
    background: #ecfdf5;
    border: 1px solid #bbf7d0;
    padding: 12px;
    border-radius: 12px;
    word-break: break-word;
}

.history-item {
    padding: 10px 12px;
    border-radius: 10px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    margin-bottom: 8px;
    font-size: 14px;
    color: #374151;
}

.app-title {
    text-align: center;
    font-size: 34px;
    font-weight: 800;
    color: #111827;
    margin-bottom: 4px;
}

.app-subtitle {
    text-align: center;
    font-size: 15px;
    color: #6b7280;
    margin-bottom: 35px;
}

.empty-box {
    text-align: center;
    margin-top: 130px;
}

.empty-box h1 {
    font-size: 32px;
    font-weight: 800;
    color: #111827;
}

.empty-box p {
    color: #6b7280;
    font-size: 15px;
}

.stButton > button {
    width: 100%;
    background: #111827;
    color: white;
    border-radius: 10px;
    border: none;
    height: 42px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #000000;
    color: white;
}

div[data-testid="stChatInput"] {
    max-width: 860px;
    margin: auto;
}

div[data-testid="stChatInput"] textarea {
    border-radius: 16px !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="app-title">🤖 RAG ChatBot</div>', unsafe_allow_html=True)
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
    st.markdown('<div class="sidebar-title">🤖 RAG Assistant</div>', unsafe_allow_html=True)

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
    with st.chat_message(msg["role"]):
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

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
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
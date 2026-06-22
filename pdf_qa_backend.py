import os
import tempfile

from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader, PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate


prompt = ChatPromptTemplate.from_template("""
You are a careful document QA assistant.

Use ONLY the provided context.

Before answering:
- Read all retrieved context carefully.
- If the question asks oldest, earliest, first, latest, largest, smallest, highest, lowest, compare all relevant entities.
- Do not choose an answer only because one chunk has matching words.
- Prefer historical date/order when the question asks oldest or earliest.
- If context is insufficient, say: "I could not find this information in the selected source."

Keep the answer clear, simple, and natural.

Context:
{context}

Question:
{question}

Answer:
""")


def get_llm():
    return ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant"
    )


def create_vector_store(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1800,
        chunk_overlap=400
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

    return FAISS.from_documents(chunks, embeddings)


def load_website(url):
    loader = WebBaseLoader(url)
    return loader.load()


def load_uploaded_file(uploaded_file):
    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    file_name = uploaded_file.name

    if "." not in file_name:
        raise ValueError("File extension missing. Please upload PDF, TXT, or DOCX.")

    suffix = file_name.rsplit(".", 1)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix="." + suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    if suffix == "pdf":
        loader = PyMuPDFLoader(tmp_path)
    elif suffix == "txt":
        loader = TextLoader(tmp_path, encoding="utf-8")
    elif suffix == "docx":
        loader = Docx2txtLoader(tmp_path)
    else:
        raise ValueError("Unsupported file type. Upload PDF, TXT, or DOCX only.")

    docs = loader.load()

    docs = [
        doc for doc in docs
        if doc.page_content and doc.page_content.strip()
    ]

    if not docs:
        raise ValueError(
            "No readable text found in this file. It may be a scanned/image-based PDF."
        )

    for doc in docs:
        doc.metadata["file_name"] = file_name

    return docs


def build_context(docs):
    context_parts = []

    for doc in docs:
        file_name = doc.metadata.get("file_name", "Document")
        source = doc.metadata.get("source", file_name)
        page = doc.metadata.get("page", None)

        page_text = f"Page {page + 1}" if page is not None else "Page not available"

        context_parts.append(
            f"[Source: {source}, {page_text}]\n{doc.page_content}"
        )

    return "\n\n".join(context_parts)


def get_page_info(docs):
    pages = []
    files = []

    for doc in docs:
        if "page" in doc.metadata:
            pages.append(doc.metadata["page"] + 1)

        if "file_name" in doc.metadata:
            files.append(doc.metadata["file_name"])

    pages = sorted(list(set(pages)))
    files = sorted(list(set(files)))

    info = []

    if files:
        info.append("File: " + ", ".join(files))

    if pages:
        info.append("Page: " + ", ".join(map(str, pages)))

    return " | ".join(info)


def answer_question(vector_store, question, source_type):
    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 8,
            "fetch_k": 25,
            "lambda_mult": 0.45
        }
    )

    docs = retriever.invoke(question)

    context = build_context(docs)

    chain = prompt | get_llm()

    response = chain.invoke({
        "context": context,
        "question": question
    })

    page_info = ""

    if source_type == "Document":
        page_info = get_page_info(docs)

    return response.content, page_info
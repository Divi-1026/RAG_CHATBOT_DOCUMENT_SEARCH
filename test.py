from dotenv import load_dotenv
from pdf_qa_backend import load_website, create_vector_store

load_dotenv()

url = "https://example.com"

docs = load_website(url)

vector_store = create_vector_store(docs)

print("Vector store created successfully")
print("Total docs loaded:", len(docs))
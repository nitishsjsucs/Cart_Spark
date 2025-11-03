import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from typing import Dict, List
import time
from tenacity import retry, stop_after_attempt, wait_exponential


DATASETS_DIR = os.path.abspath(os.path.join(os.getcwd(), "./datasets/"))


def load_pdf_text(path):
    loader = PyPDFLoader(path)
    pdf_doc = loader.load()
    text = ""
    for doc in pdf_doc:
        text += doc.page_content
    return text


def load_csv_text(path, max_rows=100):
    """Load CSV and convert to text, limiting rows to avoid memory issues."""
    df = pd.read_csv(path, nrows=max_rows)
    # Only keep key columns if there are too many
    if len(df.columns) > 10:
        # Keep first 10 columns
        df = df.iloc[:, :10]
    return f"CSV Data (first {len(df)} rows):\n" + df.to_string(index=False)


def load_all_disease_documents():
    """Load all documents from PDFs + CSVs for each disease as Document objects."""
    all_documents = []

    for disease in os.listdir(DATASETS_DIR):
        disease_path = os.path.join(DATASETS_DIR, disease)
        if not os.path.isdir(disease_path):
            continue

        print(f"  Loading {disease}...")
        for file in os.listdir(disease_path):
            file_path = os.path.join(disease_path, file)
            if file.endswith(".pdf"):
                print(f"    - {file}")
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                # Add disease metadata to each page
                for doc in docs:
                    doc.metadata["disease"] = disease
                    doc.metadata["source_file"] = file
                all_documents.extend(docs)
            elif file.endswith(".csv"):
                print(f"    - {file}")
                csv_text = load_csv_text(file_path)
                doc = Document(
                    page_content=csv_text,
                    metadata={"disease": disease, "source_file": file}
                )
                all_documents.append(doc)

    return all_documents


def build_vector_store(documents):
    """Build vector store from documents with improved embeddings."""
    print("  Loading embedding model (all-mpnet-base-v2 - better accuracy)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Split documents into chunks with better parameters
    print(f"  Splitting {len(documents)} documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    split_docs = splitter.split_documents(documents)
    
    print(f"  Total chunks: {len(split_docs)}")
    print("  Creating embeddings and storing in ChromaDB...")
    
    # Create vector store with all documents at once
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        collection_name="disease_studies",
        persist_directory="./chroma/disease_studies"
    )
    
    return vectordb


def get_or_create_vector_store():
    """Get existing vector store or create new one if it doesn't exist."""
    persist_dir = "./chroma/disease_studies"
    
    # Check if vector store already exists
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("  Found existing vector store, loading...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        vectordb = Chroma(
            embedding_function=embeddings,
            collection_name="disease_studies",
            persist_directory=persist_dir
        )
        return vectordb
    else:
        print("  No existing vector store found, building new one...")
        print("  (This will take a few minutes on first run)\n")
        documents = load_all_disease_documents()
        print(f"\n  ✓ Loaded {len(documents)} documents\n")
        vectordb = build_vector_store(documents)
        return vectordb


def format_docs_with_sources(docs) -> tuple:
    """Format documents and extract source information."""
    context = "\n\n".join([
        f"[Source: {doc.metadata.get('disease', 'Unknown')} - {doc.metadata.get('source_file', 'Unknown')}]\n{doc.page_content}"
        for doc in docs
    ])
    
    sources = []
    seen = set()
    for doc in docs:
        disease = doc.metadata.get('disease', 'Unknown')
        file = doc.metadata.get('source_file', 'Unknown')
        key = f"{disease}|{file}"
        if key not in seen:
            sources.append({'disease': disease, 'file': file})
            seen.add(key)
    
    return context, sources


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def query_rag_system(vectordb, query: str) -> Dict:
    """Query the RAG system with improved retrieval and GPT-4o."""
    
    # Validate query
    if not query or len(query.strip()) < 3:
        return {
            'answer': "Please provide a more detailed question.",
            'sources': []
        }
    
    # Enhanced retriever with better parameters
    retriever = vectordb.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diversity
        search_kwargs={
            "k": 8,  # Retrieve more documents
            "fetch_k": 20,  # Fetch more candidates for MMR
            "lambda_mult": 0.7  # Balance between relevance and diversity
        }
    )

    # Use GPT-4o (faster, cheaper, better than GPT-4)
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,  # Slight temperature for more natural responses
        max_tokens=1000,
        request_timeout=60
    )

    # Improved prompt template with better instructions
    template = """You are an expert clinical AI assistant with access to peer-reviewed medical research and clinical trial data.

Your task is to provide accurate, evidence-based answers to medical questions.

IMPORTANT GUIDELINES:
1. Base your answer ONLY on the provided context from medical literature
2. If the context doesn't contain enough information, clearly state this
3. Cite specific findings, algorithms, or methodologies mentioned in the sources
4. Use clear, professional medical terminology but explain complex concepts
5. If multiple approaches exist, present them objectively
6. Never make up information or speculate beyond the provided context

CONTEXT FROM MEDICAL LITERATURE:
{context}

QUESTION: {question}

PROFESSIONAL ANSWER:"""
    
    try:
        # Get relevant documents
        docs = retriever.get_relevant_documents(query)
        
        if not docs:
            return {
                'answer': "I couldn't find relevant information in the medical literature database to answer this question.",
                'sources': []
            }
        
        # Format context and extract sources
        context, sources = format_docs_with_sources(docs)
        
        # Create and run the RAG chain
        prompt = PromptTemplate.from_template(template)
        rag_chain = (
            {
                "context": lambda x: context,
                "question": lambda x: x
            }
            | prompt
            | llm
            | StrOutputParser()
        )
        
        answer = rag_chain.invoke(query)
        
        return {
            'answer': answer,
            'sources': sources
        }
    
    except Exception as e:
        return {
            'answer': f"An error occurred while processing your query: {str(e)}",
            'sources': []
        }


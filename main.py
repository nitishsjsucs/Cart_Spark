# from fastapi import FastAPI
# from routers.handle_routes import router as agent_router

# app = FastAPI(
#     title="Clinical AI assistant",
#     description="An AI assistant capable of answering clinicians’ questions in real time, supported by credible, machine-readable evidence.",
#     version="1.0.0"
# )

# app.include_router(agent_router)

from model.rag_model import load_all_disease_documents, build_vector_store, get_or_create_vector_store, query_rag_system
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the Clinical AI Assistant."""
    print("="*80)
    print("Clinical AI Assistant - Powered by GPT-4o and Advanced RAG")
    print("="*80 + "\n")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found!")
        print("Please add it to your .env file or set it as an environment variable.")
        print("Example .env file:")
        print("  OPENAI_API_KEY='sk-...'\n")
        return
    
    try:
        # Get or create vector store (with caching)
        print("📚 Initializing vector store...")
        vectordb = get_or_create_vector_store()
        print("✓ Vector store ready\n")
        
        # Interactive query loop
        print("💡 You can now ask medical questions!")
        print("   Type 'exit' or 'quit' to stop.\n")
        
        while True:
            query = input("\n🔍 Your question: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                print("⚠️  Please enter a question.")
                continue
            
            print("\n🤔 Thinking...\n")
            result = query_rag_system(vectordb, query)
            
            print("="*80)
            print("📋 ANSWER:")
            print("="*80)
            print(result['answer'])
            print("\n" + "-"*80)
            print("📚 SOURCES:")
            print("-"*80)
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['disease']} - {source['file']}")
            print("="*80)
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
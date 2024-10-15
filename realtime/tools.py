import os
import asyncio
import logging
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Ensure OPENAI_API_KEY is set
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

search_documents_def = {
    "name": "search_documents",
    "description": "Semantic search over our internal knowledge base. Should be used for answering most questions by the user. Returns a list of relevant documents.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The search query to use for the semantic search."
        }
      },
      "required": ["query"]
    }
}

async def search_documents_handler(query, is_test=False):
    """
    Semantic search over documents using FAISS vector store. Returns a list of relevant documents.
    """
    print("Tool call: search_documents.", query)
    try:
        # Get the current working directory
        current_dir = os.getcwd()
        
        # Construct the path to the FAISS index
        faiss_index_path = os.path.join(current_dir, "..", "faiss_index")
        
        print(f"Attempting to load FAISS index from: {faiss_index_path}")
        
        # Check if the directory exists
        if not os.path.exists(faiss_index_path):
            raise FileNotFoundError(f"The directory {faiss_index_path} does not exist.")
        
        # List the contents of the directory
        print("Contents of the faiss_index directory:")
        for file in os.listdir(faiss_index_path):
            print(f"  - {file}")
        
        # Load the FAISS index
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(faiss_index_path, embeddings, allow_dangerous_deserialization=True)

        # Perform the search
        search_results = vectorstore.similarity_search_with_score(query, k=4)

        print(f"Number of search results: {len(search_results)}")

        # Format the results
        result = []
        for doc, score in search_results:
            # Get the document source
            source = doc.metadata['source']
            print(f"Processing document from source: {source}")
            
            # Expand content with previous and next pages
            expanded_content = expand_content(vectorstore, source, doc.page_content)
            
            result.append({
                "title": f"Document from {source}",
                "file": source,
                "content": expanded_content,
                "relevance_score": 1 - score  # Convert distance to similarity score
            })

        # Display the relevant documents in the chat only if not in test mode
        if not is_test:
            message = "Hier sind die relevantesten Dokumente:"
            elements = [
                cl.Text(name=f"{doc['title']}", content=f"Datei: {doc['file']}\nRelevanz: {doc['relevance_score']:.2f}\n\n{doc['content']}")
                for doc in result
            ]
            await cl.Message(content=message, elements=elements).send()

        print("Result: ", result)
        return result

    except Exception as e:
        error_message = f"Error in search_documents_handler: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_message)
        return {"error": error_message}

def expand_content(vectorstore, source, current_content):
    # Get all documents from the same source
    all_docs = vectorstore.similarity_search_with_score(f"file:{source}", k=100)
    all_docs = [doc for doc, _ in all_docs if doc.metadata['source'] == source]
    
    # If no documents are found, return the current content
    if not all_docs:
        print(f"Warning: No documents found for source: {source}")
        return current_content
    
    # Sort documents by their order in the original file
    all_docs.sort(key=lambda x: x.metadata.get('page', 0))
    
    # Find the index of the current content
    try:
        current_index = next(i for i, doc in enumerate(all_docs) if doc.page_content == current_content)
    except StopIteration:
        # If exact match is not found, find the most similar document
        current_index = max(range(len(all_docs)), key=lambda i: similarity(all_docs[i].page_content, current_content))
    
    # Get previous, current, and next pages
    start_index = max(0, current_index - 1)
    end_index = min(len(all_docs), current_index + 2)
    
    expanded_content = "\n\n".join(doc.page_content for doc in all_docs[start_index:end_index])
    
    return expanded_content

def similarity(text1, text2):
    # Simple similarity measure based on common words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    return len(words1.intersection(words2)) / len(words1.union(words2))

search_documents = (search_documents_def, search_documents_handler)

async def test_search_documents():
    logger.info("Starting test of search_documents_handler")
    
    test_queries = [
        "What is the main topic of the documents?",
        "Tell me about the company's products",
        "What are the key financial metrics?"
    ]
    
    for query in test_queries:
        logger.info(f"Testing query: {query}")
        result = await search_documents_handler(query, is_test=True)
        
        if isinstance(result, list):
            logger.info(f"Number of documents returned: {len(result)}")
            for i, doc in enumerate(result, 1):
                logger.info(f"Document {i}:")
                logger.info(f"  Title: {doc['title']}")
                logger.info(f"  File: {doc['file']}")
                logger.info(f"  Relevance Score: {doc['relevance_score']:.4f}")
                logger.info(f"  Full Content:")
                logger.info(doc['content'])
                logger.info("---")
        else:
            logger.error(f"Error in search: {result.get('error', 'Unknown error')}")
        
        logger.info("=== End of query results ===\n")

    logger.info("Test completed")

if __name__ == "__main__":
    asyncio.run(test_search_documents())

tools = [search_documents]

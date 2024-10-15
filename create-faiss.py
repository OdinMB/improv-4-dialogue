import os
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY is not set in the .env file.")
    exit(1)

os.environ["OPENAI_API_KEY"] = api_key

# Initialize the OpenAI embeddings
try:
    embeddings = OpenAIEmbeddings()
except Exception as e:
    logger.error(f"Failed to initialize OpenAI embeddings: {e}")
    exit(1)

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# Function to process PDF files
def process_pdf(file_path):
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        
        texts = []
        metadatas = []
        
        for page in pages:
            chunks = text_splitter.split_text(page.page_content)
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append({
                    "source": os.path.basename(file_path),
                    "page": page.metadata["page"]
                })
        
        return texts, metadatas
    except Exception as e:
        logger.error(f"Error processing {file_path}: {e}")
        return [], []

# Process all PDF files in the /data folder
all_texts = []
all_metadatas = []

data_folder = "./data"
if not os.path.exists(data_folder):
    logger.error(f"Data folder '{data_folder}' does not exist.")
    exit(1)

pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]
if not pdf_files:
    logger.error(f"No PDF files found in '{data_folder}'.")
    exit(1)

for filename in pdf_files:
    file_path = os.path.join(data_folder, filename)
    logger.info(f"Processing {file_path}")
    texts, metadatas = process_pdf(file_path)
    all_texts.extend(texts)
    all_metadatas.extend(metadatas)

if not all_texts:
    logger.error("No text extracted from PDF files.")
    exit(1)

# Create FAISS vector store
try:
    logger.info("Creating FAISS vector store...")
    vectorstore = FAISS.from_texts(all_texts, embeddings, metadatas=all_metadatas)
    
    # Save the FAISS index
    logger.info("Saving FAISS index...")
    vectorstore.save_local("faiss_index")
    
    logger.info("FAISS index created and saved successfully.")
except Exception as e:
    logger.error(f"Error creating or saving FAISS index: {e}")
    exit(1)

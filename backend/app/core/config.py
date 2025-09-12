import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # PubMed API Configuration
    PUBMED_API_KEY: str = os.getenv("PUBMED_API_KEY", "")
    PUBMED_API_BASE_URL: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    # --- Gemini API Configuration (for all AI tasks) ---
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    GEMINI_GENERATIVE_MODEL: str = "gemini-1.5-flash-latest"

    # Vector Index Configuration
    VECTOR_INDEX_PATH: str = "backend/data/vector_index.faiss"

    # Search Configuration
    INITIAL_RETRIEVAL_SIZE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a single instance of the Settings class that can be imported elsewhere
settings = Settings()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes

# Create the FastAPI app instance
app = FastAPI(
    title="PubMed Semantic Search API",
    description="An API for semantically searching PubMed articles.",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing) to allow the frontend to connect
origins = [
    "http://localhost:3000",  # The default URL for the React development server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the API router from the api/routes.py file
# This will add all endpoints defined in that router to the application
app.include_router(routes.router, prefix="/api/v1")

# Define a root endpoint for a simple health check
@app.get("/", tags=["Health Check"])
def read_root():
    """
    Root endpoint to confirm that the API is running.
    """
    return {"status": "ok", "message": "PubMed Semantic Search API is running"}


from fastapi import APIRouter, HTTPException, Query, Body
from ..services.search_service import hybrid_search, build_advanced_pubmed_query, generate_knowledge_graph
from ..models.search import SearchResponse, AdvancedSearchRequest, KnowledgeGraphResponse, GraphRequest

router = APIRouter()

# --- Search Endpoints (Unchanged) ---
@router.get("/search", response_model=SearchResponse, summary="Perform a simple search", tags=["Search"])
async def search_pubmed(query: str = Query(..., min_length=3), top_k: int = Query(100, ge=20, le=200)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        search_data = await hybrid_search(original_query=query, keyword_query=None, top_k=top_k, check_suggestion=True)
        return search_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/advanced-search", response_model=SearchResponse, summary="Perform an advanced search", tags=["Search"])
async def advanced_search_pubmed(request: AdvancedSearchRequest = Body(...)):
    try:
        keyword_query = build_advanced_pubmed_query(request.clauses)
        semantic_intent = " ".join([c.value for c in request.clauses])
        search_data = await hybrid_search(original_query=semantic_intent, keyword_query=keyword_query, top_k=request.top_k, check_suggestion=False)
        return search_data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- REFACTORED: Knowledge Graph Endpoint ---
@router.post("/knowledge-graph", response_model=KnowledgeGraphResponse, summary="Generate a knowledge graph from context", tags=["Graph"])
async def post_knowledge_graph(request: GraphRequest = Body(...)):
    if not request.context_text:
        raise HTTPException(status_code=400, detail="Context text cannot be empty.")
    try:
        return await generate_knowledge_graph(request.context_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate knowledge graph: {e}")

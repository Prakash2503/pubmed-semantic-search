from pydantic import BaseModel, Field
from typing import List, Optional

# --- Existing Models ---
class SearchResult(BaseModel):
    pmid: str = Field(..., description="The PubMed ID of the article.")
    title: str = Field(..., description="The title of the article.")
    abstract: Optional[str] = Field(None, description="The abstract of the article.")
    url: str = Field(..., description="The direct URL to the article on PubMed.")
    authors: str = Field(..., description="A comma-separated list of authors.")
    score: Optional[float] = Field(None, description="The semantic similarity score.")

class AdvancedSearchClause(BaseModel):
    field: str = Field(..., description="The search field, e.g., 'Author'.")
    value: str = Field(..., description="The value to search for in the specified field.")
    operator: str = Field("AND", description="Boolean operator (AND, OR, NOT).")

class AdvancedSearchRequest(BaseModel):
    clauses: List[AdvancedSearchClause] = Field(..., min_items=1, description="A list of search clauses.")
    top_k: int = Field(100, ge=20, le=200, description="The number of top results to retrieve for ranking.")

class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., description="A list of search result items.")
    suggestion: Optional[str] = Field(None, description="A search query suggestion, if available.")
    total_results: int = Field(0, description="The total number of results found for the query.")

# --- Models for Knowledge Graph ---
class GraphNode(BaseModel):
    id: str = Field(..., description="The unique identifier for the node, typically the entity name.")
    label: str = Field(..., description="The display name for the node.")
    group: Optional[str] = Field(None, description="The category or type of the entity (e.g., 'Disease', 'Gene').")
    pmid: str = Field(..., description="The source PubMed ID for the node.")
    url: str = Field(..., description="The source URL for the node.")

class GraphLink(BaseModel):
    source: str = Field(..., description="The ID of the source node.")
    target: str = Field(..., description="The ID of the target node.")
    label: str = Field(..., description="A label describing the relationship between the nodes.")

class KnowledgeGraphResponse(BaseModel):
    nodes: List[GraphNode] = Field(..., description="A list of nodes in the knowledge graph.")
    links: List[GraphLink] = Field(..., description="A list of links connecting the nodes.")

# --- NEW MODEL FOR THE REFACTORED GRAPH REQUEST ---
class GraphRequest(BaseModel):
    context_text: str = Field(..., min_length=100, description="The combined text of abstracts to be processed.")

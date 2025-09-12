import numpy as np
import google.generativeai as genai
import json
import re
from typing import List, Dict, Any, Optional

from . import pubmed_service
from ..core.config import settings
from ..models.search import AdvancedSearchClause

# API Configuration
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    print("Gemini API client configured successfully.")
else:
    print("Warning: GOOGLE_API_KEY not found. All AI functionality will fail.")

# --- Helper and Transformation Functions ---
def build_advanced_pubmed_query(clauses: List[AdvancedSearchClause]) -> str:
    # This function is unchanged
    if not clauses:
        raise ValueError("Advanced search clauses cannot be empty.")
    query_parts = []
    for clause in clauses:
        sanitized_value = clause.value.strip().replace('"', '""')
        if not sanitized_value:
            continue
        field_tag = f'[{clause.field}]' if clause.field != "All Fields" else ""
        value_str = f'"{sanitized_value}"' if ' ' in sanitized_value else sanitized_value
        query_parts.append(f"({value_str}{field_tag})")
    if not query_parts:
        raise ValueError("All search clauses were empty or invalid.")
    full_query = query_parts[0]
    for i in range(1, len(query_parts)):
        full_query += f" {clauses[i-1].operator} {query_parts[i]}"
    return full_query

def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # This function is unchanged
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def _get_query_suggestion_with_gemini(user_query: str) -> Optional[str]:
    # This function is unchanged
    try:
        model = genai.GenerativeModel(settings.GEMINI_GENERATIVE_MODEL)
        prompt = f"""You are a highly intelligent search query corrector for PubMed. Correct spelling or replace jargon. Return only the corrected query. If it's already correct, return the original.
User Query: "{user_query}"
Corrected Query:"""
        response = await model.generate_content_async(prompt)
        suggestion = response.text.strip()
        if suggestion.lower() != user_query.lower() and suggestion:
            return suggestion
        return None
    except Exception as e:
        print(f"Warning: Gemini suggestion generation failed: {e}")
        return None

# --- Main Search Logic (Unchanged) ---
async def hybrid_search(original_query: str, keyword_query: Optional[str], top_k: int, check_suggestion: bool = False) -> Dict[str, Any]:
    # This function is unchanged
    suggestion = await _get_query_suggestion_with_gemini(original_query) if check_suggestion else None
    final_keyword_query = keyword_query if keyword_query else (suggestion or original_query)
    article_ids, total_results = await pubmed_service.fetch_article_ids(final_keyword_query, count=top_k)
    if not article_ids:
        return {"results": [], "suggestion": suggestion, "total_results": 0}
    articles = await pubmed_service.fetch_article_details(article_ids)
    articles_with_abstracts = [a for a in articles if a.get("abstract")]
    if not articles_with_abstracts:
        return {"results": articles, "suggestion": suggestion, "total_results": total_results}
    try:
        query_embedding = np.array(genai.embed_content(model=settings.GEMINI_EMBEDDING_MODEL, content=original_query, task_type="retrieval_query")['embedding'])
        article_embeddings = np.array(genai.embed_content(model=settings.GEMINI_EMBEDDING_MODEL, content=[a['abstract'] for a in articles_with_abstracts], task_type="retrieval_document")['embedding'])
        for i, article in enumerate(articles_with_abstracts):
            article['score'] = _cosine_similarity(query_embedding, article_embeddings[i])
        reranked_articles = sorted(articles_with_abstracts, key=lambda x: x.get('score', 0), reverse=True)
        reranked_pmids = {a['pmid'] for a in reranked_articles}
        other_articles = [a for a in articles if a['pmid'] not in reranked_pmids]
        return {"results": reranked_articles + other_articles, "suggestion": suggestion, "total_results": total_results}
    except Exception as e:
        print(f"Error during semantic re-ranking: {e}. Returning keyword results.")
        return {"results": articles, "suggestion": suggestion, "total_results": total_results}

# --- FINAL, ULTRA-ROBUST KNOWLEDGE GRAPH IMPLEMENTATION ---

async def _call_gemini_for_graph(prompt: str) -> Optional[Dict[str, Any]]:
    """Helper to call Gemini API and handle potential errors."""
    try:
        model = genai.GenerativeModel(settings.GEMINI_GENERATIVE_MODEL)
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except (Exception, json.JSONDecodeError) as e:
        print(f"[GRAPH] Gemini API call or JSON parsing failed: {e}")
        return None

def _extract_sources_from_context(context_text: str) -> Dict[str, Dict[str, str]]:
    """Creates a map of PMID to its URL from the context text."""
    sources = {}
    for line in context_text.split('\n'):
        if line.startswith("From article"):
            pmid_match = re.search(r'pmid:(\S+)', line)
            url_match = re.search(r'url:(\S+)', line)
            if pmid_match and url_match:
                sources[pmid_match.group(1)] = {"url": url_match.group(1)}
    return sources

def _get_first_source(sources: Dict) -> tuple[str, str]:
    """Gets the first available PMID and URL as a fallback."""
    if not sources:
        return "unknown", "unknown"
    first_pmid = next(iter(sources))
    return first_pmid, sources[first_pmid]['url']

async def generate_knowledge_graph(context_text: str) -> Dict[str, Any]:
    print("\n--- [GRAPH] FINAL ATTEMPT: Generating Knowledge Graph ---")

    if not settings.GOOGLE_API_KEY:
        print("[GRAPH] FATAL: Gemini client not configured.")
        return {"nodes": [], "links": []}

    source_map = _extract_sources_from_context(context_text)
    
    # Attempt 1: Chain of Thought prompt
    print("[GRAPH] Attempt 1: Using Chain-of-Thought prompt.")
    chain_of_thought_prompt = f"""
Analyze the provided biomedical text step-by-step.
First, identify all key entities (like Diseases, Genes, Drugs, Proteins). For each entity, note the `pmid` from the source text.
Second, identify all relationships between these entities (e.g., 'treats', 'inhibits', 'is associated with').
Third, construct a JSON object based on your findings.
Your final output MUST be only the JSON object, following this exact structure:
{{
  "nodes": [{{ "id": "EntityName", "label": "EntityName", "group": "EntityType", "pmid": "SourcePMID" }}],
  "links": [{{ "source": "EntityName1", "target": "EntityName2", "label": "relationship" }}]
}}
Text to analyze:
---
{context_text}"""
    
    graph_data = await _call_gemini_for_graph(chain_of_thought_prompt)

    # Attempt 2: Simplified (Entities Only) fallback
    if not graph_data or not graph_data.get("nodes"):
        print("[GRAPH] Attempt 1 failed. Trying Attempt 2: Simplified 'Entities Only' prompt.")
        entities_only_prompt = f"""
From the text below, extract all key biomedical entities (like Diseases, Genes, Drugs).
For each entity, determine its type (e.g., "Disease").
Your final output MUST be a single JSON object with a "nodes" list. Follow this exact structure:
{{
  "nodes": [{{ "id": "EntityName", "label": "EntityName", "group": "EntityType" }}],
  "links": []
}}
Text to analyze:
---
{context_text}"""
        graph_data = await _call_gemini_for_graph(entities_only_prompt)
        if graph_data:
            graph_data.setdefault("links", [])

    # Final Validation and Augmentation
    if not graph_data or "nodes" not in graph_data:
        print("[GRAPH] FAIL: All attempts failed to produce any nodes.")
        return {"nodes": [], "links": []}

    fallback_pmid, fallback_url = _get_first_source(source_map)
    for node in graph_data.get("nodes", []):
        node_pmid = node.get('pmid', fallback_pmid)
        node['url'] = source_map.get(node_pmid, {}).get('url', fallback_url)
        node['pmid'] = node_pmid

    validated_nodes = [node for node in graph_data.get('nodes', []) if all(k in node for k in ['id', 'label', 'group', 'url', 'pmid'])]
    node_ids = {node['id'] for node in validated_nodes}
    validated_links = [link for link in graph_data.get('links', []) if link.get('source') in node_ids and link.get('target') in node_ids]
    
    final_graph_data = {"nodes": validated_nodes, "links": validated_links}
    
    if not final_graph_data["nodes"]:
        print("[GRAPH] FAIL: No valid nodes remained after final validation.")
    else:
        print(f"[GRAPH] SUCCESS: Parsed graph with {len(validated_nodes)} nodes and {len(validated_links)} links.")
    
    return final_graph_data

import httpx
import asyncio
import xml.etree.ElementTree as ET
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any, Tuple

from ..core.config import settings

client = httpx.AsyncClient()

@retry(wait=wait_exponential(multiplier=1, min=2, max=6), stop=stop_after_attempt(3))
async def _make_api_request(url: str, params: Dict[str, Any]) -> httpx.Response:
    try:
        response = await client.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response
    except httpx.RequestError as e:
        print(f"Request error to PubMed API: {e}")
        raise

async def fetch_article_ids(query: str, count: int) -> Tuple[List[str], int]:
    """
    Fetches a list of PubMed article IDs and the total number of hits for the query.
    It now safely handles API errors by returning a default tuple.
    """
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": count,
        "usehistory": "y",
        "api_key": settings.PUBMED_API_KEY,
        "format": "json"
    }
    try:
        response = await _make_api_request(f"{settings.PUBMED_API_BASE_URL}/esearch.fcgi", params)
        data = response.json()
        
        esearch_result = data.get("esearchresult", {})
        id_list = esearch_result.get("idlist", [])
        total_count = int(esearch_result.get("count", "0"))
        
        return id_list, total_count
    except Exception as e:
        print(f"Failed to fetch article IDs from PubMed: {e}")
        # THIS IS THE FIX: Always return a two-item tuple to prevent unpacking errors
        return [], 0

async def fetch_article_details(pmids: List[str]) -> List[Dict[str, Any]]:
    """Fetches full article details for a given list of PubMed IDs."""
    if not pmids:
        return []
    articles = []
    batch_size = 200
    for i in range(0, len(pmids), batch_size):
        batch_pmids = pmids[i:i + batch_size]
        pmid_string = ",".join(batch_pmids)
        params = {
            "db": "pubmed",
            "id": pmid_string,
            "retmode": "xml",
            "api_key": settings.PUBMED_API_KEY
        }
        try:
            response = await _make_api_request(f"{settings.PUBMED_API_BASE_URL}/efetch.fcgi", params)
            root = ET.fromstring(response.text)
            for pubmed_article in root.findall(".//PubmedArticle"):
                article_data = {}
                pmid_element = pubmed_article.find(".//PMID")
                article_data["pmid"] = pmid_element.text if pmid_element is not None else ""
                title_element = pubmed_article.find(".//ArticleTitle")
                article_data["title"] = title_element.text if title_element is not None else "No title available"
                abstract_element = pubmed_article.find(".//AbstractText")
                article_data["abstract"] = abstract_element.text if abstract_element is not None else ""
                article_data["url"] = f"https://pubmed.ncbi.nlm.nih.gov/{article_data['pmid']}/"
                
                authors = [
                    f"{author.find('ForeName').text} {author.find('LastName').text}"
                    for author in pubmed_article.findall(".//Author")
                    if author.find("LastName") is not None and author.find("ForeName") is not None
                ]
                article_data["authors"] = ", ".join(authors) if authors else "No authors listed"
                articles.append(article_data)
        except Exception as e:
            print(f"Error fetching article details batch: {e}")
        await asyncio.sleep(0.3) # Politeness delay to not overwhelm the API
    return articles

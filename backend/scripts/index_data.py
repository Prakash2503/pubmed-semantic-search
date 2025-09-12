import os
import asyncio
import aiohttp
import numpy as np
import faiss # convert too qdrant or chromdb better for hosting
import json
from xml.etree import ElementTree
from sentence_transformers import SentenceTransformer

# add a blueprin befroe hosting

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils" # read documentations

async def fetch_article_ids(query: str, count: int = 10):
    """Fetch article IDs from PubMed for a given query."""
    url = f"{BASE_URL}/esearch.fcgi"
    params = {"db": "pubmed", "term": query, "retmax": count, "retmode": "json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            return data.get("esearchresult", {}).get("idlist", [])

async def fetch_article_details(article_ids, batch_size: int = 200):
    """Fetch details for a list of PubMed article IDs."""
    articles = []
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(article_ids), batch_size):
            batch_pmids = article_ids[i:i+batch_size]
            pmid_string = ",".join(str(p) for p in batch_pmids)

            url = f"{BASE_URL}/efetch.fcgi"
            params = {"db": "pubmed", "id": pmid_string, "retmode": "xml"}

            async with session.get(url, params=params) as resp:
                xml_text = await resp.text()
                root = ElementTree.fromstring(xml_text)

                for article in root.findall(".//PubmedArticle"):
                    pmid = article.findtext(".//PMID")
                    title = article.findtext(".//ArticleTitle")
                    abstract_texts = [a.text for a in article.findall(".//AbstractText") if a.text]
                    abstract = " ".join(abstract_texts).strip()

                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract
                    })
    return articles

INDEXING_QUERY = "biomedical research OR clinical trials OR life sciences"
NUM_ARTICLES_TO_INDEX = 5  # keep small for testing -> dont got for higher numbers it may increase the latency exponentially 

async def build_index():
    print("--- Starting the indexing process with SentenceTransformers ---")

    print(f"Fetching {NUM_ARTICLES_TO_INDEX} article IDs for query: '{INDEXING_QUERY}'...")
    article_ids = await fetch_article_ids(INDEXING_QUERY, count=NUM_ARTICLES_TO_INDEX)
    if not article_ids:
        print("No articles found. Exiting.")
        return

    print(f"Fetching details for {len(article_ids)} articles...")
    articles = await fetch_article_details(article_ids)
    articles_to_index = [a for a in articles if a.get("abstract")]
    print(f"Found {len(articles_to_index)} articles with abstracts.")
    if not articles_to_index:
        return

    for art in articles_to_index:
        print(f"PMID: {art['pmid']}") 
        print(f"Title: {art['title']}")
        print(f"Abstract: {art['abstract'][:200]}...")  # use this to scrap and get  the data out
        print("-" * 80)

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") #replace for medium if u want but latency adjustment required 
    article_texts = [a["abstract"] for a in articles_to_index]
    embeddings = model.encode(article_texts, convert_to_numpy=True)
    print(f"Embeddings generated. Shape: {embeddings.shape}")

    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index.add(embeddings)

    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, "data/faiss_index.index")

    with open("data/indexed_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles_to_index, f, ensure_ascii=False, indent=4)
    print("Metadata saved successfully.")

    print("\n ccheing complete! ---")

if __name__ == "__main__":
    asyncio.run(build_index())
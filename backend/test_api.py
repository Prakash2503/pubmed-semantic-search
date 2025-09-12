import httpx
import os
from dotenv import load_dotenv

# Load the .env file from the current directory
load_dotenv()
API_KEY = os.getenv("PUBMED_API_KEY")

# --- This is the most important part: Check what key is being loaded ---
print("--- API Key Diagnostic ---")
print(f"Loaded API Key: '{API_KEY}'")

if not API_KEY or API_KEY == "your_actual_api_key_here":
    print("\n[FAILURE]: Your .env file is not being loaded or the key is a placeholder.")
    print("Please check that the file is named '.env' and is in the 'backend' folder.")
else:
    print("\n[SUCCESS]: API key was loaded from .env file.")
    print("Now, testing connection to PubMed...")
    try:
        params = {
            "db": "pubmed",
            "term": "covid",
            "retmax": 1,
            "api_key": API_KEY,
            "format": "json"
        }
        response = httpx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", params=params, timeout=20.0)
        response.raise_for_status() 
        
        data = response.json()
        count = data.get("esearchresult", {}).get("count", "0")
        
        if int(count) > 0:
            print(f"\n[SUCCESS]: Connection successful! PubMed returned {count} results for 'covid'.")
            print("Your API key is working correctly.")
        else:
            print(f"\n[FAILURE]: Connection succeeded, but PubMed returned 0 results.")
            print("This means your API Key is likely invalid or copied incorrectly. Please generate a new one from the NCBI website.")

    except httpx.HTTPStatusError as e:
        print(f"\n[FAILURE]: The API returned an error. Status code: {e.response.status_code}")
        print("This strongly indicates your API key is invalid.")
    except httpx.RequestError as e:
        print(f"\n[FAILURE]: A network error occurred: {e}")
        print("Check your internet connection and firewall settings.")

print("--- End of Diagnostic ---")

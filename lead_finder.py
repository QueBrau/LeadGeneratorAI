import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import time
import csv
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === CONFIGURATION ===
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOCATION = os.getenv("LOCATION", "Durham, NC")  # Default to Durham, NC if not set

# Validate that required API keys are present
if not SERPAPI_API_KEY:
    raise ValueError("SERPAPI_API_KEY not found in environment variables. Please set it in your .env file.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
SEARCH_TERMS = {
    "facebook": [
        '"need a painter" site:facebook.com/groups "durham"',
        '"looking for remodeling help" site:facebook.com/groups "durham"',
        '"landscaping company wanted" site:facebook.com/groups "durham"',
        '"home renovation near me" site:facebook.com/groups "durham"',
        '"drywall repair service" site:facebook.com/groups "durham"',
        '"interior painting contractor" site:facebook.com/groups "durham"',
        '"affordable bathroom remodel" site:facebook.com/groups "durham"',
        '"kitchen remodeling quote" site:facebook.com/groups "durham"',
        '"siding repair company" site:facebook.com/groups "durham"',
        '"deck builder near me" site:facebook.com/groups "durham"',
        '"power washing service" site:facebook.com/groups "durham"',
        '"local painting company" site:facebook.com/groups "durham"',
        '"garage conversion contractor" site:facebook.com/groups "durham"',
        '"window replacement near me" site:facebook.com/groups "durham"',
        '"fence installation service" site:facebook.com/groups "durham"',
        '"handyman for hire" site:facebook.com/groups "durham"',
        '"house painting estimate" site:facebook.com/groups "durham"',
        '"flooring installation help" site:facebook.com/groups "durham"',
        '"stucco repair near me" site:facebook.com/groups "durham"',
        '"licensed general contractor" site:facebook.com/groups "durham"'
    ],
    "reddit": [
        '"need a painter" site:reddit.com/r/durham',
        '"looking for remodeling help" site:reddit.com/r/durham',
        '"landscaping company wanted" site:reddit.com/r/durham',
        '"home renovation near me" site:reddit.com/r/durham',
        '"drywall repair service" site:reddit.com/r/durham',
        '"interior painting contractor" site:reddit.com/r/durham',
        '"affordable bathroom remodel" site:reddit.com/r/durham',
        '"kitchen remodeling quote" site:reddit.com/r/durham',
        '"siding repair company" site:reddit.com/r/durham',
        '"deck builder near me" site:reddit.com/r/durham',
        '"power washing service" site:reddit.com/r/durham',
        '"local painting company" site:reddit.com/r/durham',
        '"garage conversion contractor" site:reddit.com/r/durham',
        '"window replacement near me" site:reddit.com/r/durham',
        '"fence installation service" site:reddit.com/r/durham',
        '"handyman for hire" site:reddit.com/r/durham',
        '"house painting estimate" site:reddit.com/r/durham',
        '"flooring installation help" site:reddit.com/r/durham',
        '"stucco repair near me" site:reddit.com/r/durham',
        '"licensed general contractor" site:reddit.com/r/durham'
    ],
    "nextdoor": [
        '"need a painter" durham',
        '"looking for remodeling help" durham',
        '"landscaping company wanted" durham',
        '"home renovation near me" durham',
        '"drywall repair service" durham',
        '"interior painting contractor" durham',
        '"affordable bathroom remodel" durham',
        '"kitchen remodeling quote" durham',
        '"siding repair company" durham',
        '"deck builder near me" durham',
        '"power washing service" durham',
        '"local painting company" durham',
        '"garage conversion contractor" durham',
        '"window replacement near me" durham',
        '"fence installation service" durham',
        '"handyman for hire" durham',
        '"house painting estimate" durham',
        '"flooring installation help" durham',
        '"stucco repair near me" durham',
        '"licensed general contractor" durham'
    ]
}
MAX_RESULTS = 5  # Per query

client = OpenAI(api_key=OPENAI_API_KEY)

# === STEP 1: Search Google with SerpAPI ===
def google_search(query):
    params = {
        "engine": "google",
        "q": query,
        "location": LOCATION,
        "api_key": SERPAPI_API_KEY,
        "tbs": "qdr:m"  # Last month
    }
    res = requests.get("https://serpapi.com/search", params=params)
    return res.json().get("organic_results", [])

# === STEP 2: Scrape Page Text ===
def scrape_text(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(html.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# === STEP 3: Ask OpenAI to Qualify Lead ===
def is_good_lead(text):
    prompt = f"""You are a lead qualification agent for a contracting business offering remodeling, painting, and landscaping in Durham, NC.

Your task is to identify if the following web content is a **real customer seeking services** — not a business advertisement, not a contractor website, not a directory listing, and not a blog or article.

DO NOT validate:
- Other contractors advertising themselves
- Listings or directories (like Yelp, Angi, etc.)
- Anything older than 1 month (especially on Reddit)
- Informational pages or reviews
- If it is not in or around Durham, NC

Only validate if it's a person or post **clearly asking for help with a service we offer**.

Here is the content:

--- START ---
{text[:1000]}
--- END ---

Answer "Yes" or "No", and explain in one sentence."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        reply = response.choices[0].message.content
        return "yes" in reply.lower(), reply
    except Exception as e:
        print(f"AI error: {e}")
        return False, ""

# === STEP 4: Store Good Leads ===

def save_to_csv(lead):
    file_exists = os.path.isfile("qualified_leads.csv")
    with open("qualified_leads.csv", "a", newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Title", "Link", "Reason"])  # Add headers
        writer.writerow([lead['title'], lead['link'], lead['reason']])


# === MAIN WORKFLOW ===
def run():
    for site, terms in SEARCH_TERMS.items():
        print(f"\n=== Searching on {site.upper()} ===")
        for term in terms:
            # For Nextdoor, maybe remove the site: operator because it may not work well
            full_query = f"{term} in {LOCATION}" if site != "nextdoor" else f"{term} {LOCATION}"
            print(f"\n🔍 Searching: {full_query}")
            results = google_search(full_query)
            for result in results[:MAX_RESULTS]:
                title = result.get("title", "")
                link = result.get("link", "")

        # ⛔️ Skip links from known directories or advertiser platforms
            if any(bad_domain in link for bad_domain in ["yelp.com", "angi.com", "houzz.com", "porch.com", "homeadvisor.com"]):
                print(f"🚫 Skipping known ad site: {link}")
                continue

            print(f"Checking: {title} | {link}")
            text = scrape_text(link)
            if not text:
                continue
            is_lead, reason = is_good_lead(text)
            if is_lead:
                print(f"✅ Qualified: {reason}")
                save_to_csv({
                    "title": title,
                    "link": link,
                    "reason": reason
                })
            else:
                print(f"❌ Not a match: {reason}")
            time.sleep(2)  # Avoid hitting rate limits

if __name__ == "__main__":
    run()


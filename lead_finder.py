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
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # Free Google Custom Search API
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")    # Custom Search Engine ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOCATION = os.getenv("LOCATION", "Durham, NC")  # Default to Durham, NC if not set

# Validate that required API keys are present
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in your .env file.")
    
# Google Custom Search is optional - will fall back to direct scraping if not available
USE_GOOGLE_SEARCH = GOOGLE_API_KEY and GOOGLE_CSE_ID
if not USE_GOOGLE_SEARCH:
    print("⚠️  Google Custom Search API not configured. Using direct scraping method.")
    print("   For better results, set up free Google Custom Search API (100 searches/day)")
    print("   Get keys at: https://developers.google.com/custom-search/v1/introduction")
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

# === STEP 1: Free Google Custom Search API ===
def google_custom_search(query):
    """Use free Google Custom Search API (100 searches/day limit)"""
    if not USE_GOOGLE_SEARCH:
        return []
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": MAX_RESULTS,
        "dateRestrict": "m1"  # Last month
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", "")
            })
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Google Custom Search API error: {e}")
        return []
    except Exception as e:
        print(f"Error parsing Google search results: {e}")
        return []

# === STEP 1A: Advanced Duplicate Detection ===
def is_similar_content(text1, text2, threshold=0.8):
    """Check if two pieces of text are too similar (likely duplicates)"""
    if not text1 or not text2:
        return False
    
    # Normalize text for comparison
    def normalize_text(text):
        return ' '.join(text.lower().split())
    
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    # Simple similarity check using character overlap
    if len(norm1) == 0 or len(norm2) == 0:
        return False
    
    # Calculate overlap percentage
    shorter = min(len(norm1), len(norm2))
    longer = max(len(norm1), len(norm2))
    
    # If one text is much shorter, check if it's contained in the other
    if shorter / longer < 0.5:
        return norm1 in norm2 or norm2 in norm1
    
    # For similar length texts, check character overlap
    set1 = set(norm1)
    set2 = set(norm2)
    overlap = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return (overlap / union) > threshold if union > 0 else False

# === STEP 1B: Fallback Direct Search Methods ===
def search_reddit_directly(query_terms):
    """Direct Reddit search using Reddit's JSON API (no auth required)"""
    results = []
    # Remove site: restriction and quotes for direct Reddit API
    clean_query = query_terms.replace('site:reddit.com/r/durham', '').replace('"', '').strip()
    
    try:
        # Search in Durham subreddit
        url = f"https://www.reddit.com/r/durham/search.json"
        params = {
            "q": clean_query,
            "restrict_sr": "1",
            "sort": "new",
            "t": "month",
            "limit": MAX_RESULTS
        }
        
        headers = {"User-Agent": "LeadGeneratorBot/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                results.append({
                    "title": post_data.get("title", ""),
                    "link": f"https://reddit.com{post_data.get('permalink', '')}",
                    "snippet": post_data.get("selftext", "")[:200] + "..."
                })
    except Exception as e:
        print(f"Reddit search error: {e}")
    
    return results

def search_facebook_groups(query_terms):
    """
    Note: Facebook has strict API restrictions. 
    This is a placeholder for educational purposes.
    Real implementation would require Facebook Graph API with proper permissions.
    """
    print("⚠️  Facebook Group search requires Facebook Graph API with special permissions")
    print("   Consider manually checking Facebook groups or using other platforms")
    return []

def google_search(query):
    """Main search function that tries multiple free methods"""
    results = []
    
    # Method 1: Try Google Custom Search API (if configured)
    if USE_GOOGLE_SEARCH:
        print(f"🔍 Searching with Google Custom Search: {query}")
        results = google_custom_search(query)
    
    # Method 2: If no results and it's a Reddit query, try direct Reddit API
    if not results and "reddit.com" in query:
        print(f"🔍 Searching Reddit directly: {query}")
        results = search_reddit_directly(query)
    
    # Method 3: If no results and it's a Facebook query, notify user
    if not results and "facebook.com" in query:
        results = search_facebook_groups(query)
    
    return results

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
    prompt = f"""You are a lead qualification agent for a HOME IMPROVEMENT CONTRACTING business in Durham, NC.

We provide these SPECIFIC SERVICES:
• Interior/Exterior Painting
• Kitchen & Bathroom Remodeling  
• Drywall Repair & Installation
• Deck Building & Repair
• Landscaping & Yard Work
• Siding & Roofing Repair
• Flooring Installation
• General Handyman Services
• Power Washing
• Fence Installation

Your task is to identify if this content is a REAL HOMEOWNER/CUSTOMER actively seeking one of our services.

❌ REJECT if it's:
• Another contractor/business advertising services
• Job postings or hiring contractors
• Product sales or equipment sales
• Real estate listings or home sales
• Directory listings (Yelp, Angi, HomeAdvisor, etc.)
• Reviews, ratings, or informational content
• DIY tutorials or how-to guides
• Old posts (over 1 month old)
• Not in Durham, NC or surrounding areas (Raleigh, Chapel Hill, Cary acceptable)
• General questions without clear service need

✅ ACCEPT ONLY if it's:
• A homeowner asking for quotes/estimates
• Someone requesting specific work we do
• Clear service request with urgency or timeline
• Residential property work (not commercial)
• Located in our service area

Look for phrases like: "need", "looking for", "can anyone recommend", "quote", "estimate", "help with", "repair", "install", "paint", "remodel"

Here is the content:

--- START ---
{text[:1000]}
--- END ---

Be very strict. Answer "Yes" ONLY if this is clearly a potential customer needing our services. Answer "No" for everything else.

Format: "Yes/No - [Brief reason why this is/isn't a qualified lead]" """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Lower temperature for more consistent filtering
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


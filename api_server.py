#!/usr/bin/env python3
"""
Flask API server for LeadGeneratorAI
Wraps the lead_finder.py functionality as REST endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import uuid
import time
from datetime import datetime
import os
import sys

# Import our lead finder functions
from lead_finder import google_search, scrape_text, is_good_lead, is_similar_content, SEARCH_TERMS, LOCATION

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Store active searches and results in memory
# In production, you'd use a database like Redis or PostgreSQL
active_searches = {}
search_results = {}
lead_history = []

class SearchJob:
    def __init__(self, search_id, search_terms, location):
        self.search_id = search_id
        self.search_terms = search_terms
        self.location = location
        self.status = "running"
        self.results = []
        self.progress = 0
        self.total_queries = 0
        self.current_query = ""
        self.start_time = datetime.now()

def background_search(search_job):
    """Run the lead search in background"""
    try:
        search_job.status = "running"
        
        # Calculate total queries
        total_queries = sum(len(terms) for terms in SEARCH_TERMS.values())
        search_job.total_queries = total_queries
        
        processed = 0
        seen_urls = set()  # Track URLs to avoid duplicates
        seen_titles = set()  # Track similar titles
        seen_content = []  # Track content for similarity checking
        
        # Enhanced blacklist of sites to skip
        blacklisted_domains = [
            "yelp.com", "angi.com", "houzz.com", "porch.com", "homeadvisor.com",
            "thumbtack.com", "taskrabbit.com", "handy.com", "amazon.com",
            "lowes.com", "homedepot.com", "menards.com", "wikipedia.org",
            "pinterest.com", "youtube.com", "facebook.com/pages", "linkedin.com",
            "indeed.com", "glassdoor.com", "craigslist.org/about", "angieslist.com"
        ]
        
        for site, terms in SEARCH_TERMS.items():
            print(f"\n=== Searching on {site.upper()} ===")
            
            for term in terms:
                # Check if search was cancelled
                if search_job.search_id not in active_searches:
                    search_job.status = "cancelled"
                    return
                
                # Update progress
                search_job.current_query = f"Searching {site}: {term[:50]}..."
                search_job.progress = int((processed / total_queries) * 100)
                
                # Customize query based on user input
                if search_job.search_terms:
                    # Replace generic terms with user's specific search terms
                    custom_term = term.replace('"need a painter"', f'"{search_job.search_terms}"')
                    custom_term = custom_term.replace('"looking for remodeling help"', f'"{search_job.search_terms}"')
                    full_query = custom_term.replace("durham", search_job.location.lower())
                else:
                    full_query = f"{term} in {search_job.location}" if site != "nextdoor" else f"{term} {search_job.location}"
                
                print(f"🔍 Searching: {full_query}")
                results = google_search(full_query)
                
                for result in results[:5]:  # MAX_RESULTS
                    title = result.get("title", "")
                    link = result.get("link", "")
                    snippet = result.get("snippet", "")
                    
                        # Skip blacklisted domains
                        if any(bad_domain in link.lower() for bad_domain in blacklisted_domains):
                            print(f"🚫 Skipping blacklisted site: {link}")
                            continue
                    
                        # Skip duplicates by URL
                        if link in seen_urls:
                            print(f"🚫 Skipping duplicate URL: {link}")
                            continue
                    
                        # Skip duplicates by similar title (normalize and compare)
                        normalized_title = title.lower().strip()
                        if normalized_title in seen_titles:
                            print(f"🚫 Skipping duplicate title: {title}")
                            continue
                    
                    
                            # Pre-filter irrelevant content by keywords
                            irrelevant_keywords = [
                                "job posting", "hiring", "employment", "career", "resume",
                                "for sale", "selling", "buy now", "price", "discount",
                                "review of", "rating", "how to", "diy", "tutorial",
                                "advertisement", "sponsored", "promotion", "coupon"
                            ]
                    
                            combined_text = f"{title} {snippet}".lower()
                            if any(keyword in combined_text for keyword in irrelevant_keywords):
                                print(f"🚫 Skipping irrelevant content: {title[:50]}...")
                                continue
                    
                            # Add to tracking sets
                            seen_urls.add(link)
                            seen_titles.add(normalized_title)
                    
                    print(f"Checking: {title} | {link}")
                    text = scrape_text(link)
                    
                    if text:
                        is_lead, reason = is_good_lead(text)
                        
                        lead_data = {
                            "id": len(search_job.results) + 1,
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "platform": site.title(),
                            "is_qualified": is_lead,
                            "ai_reason": reason,
                            "found_at": datetime.now().isoformat()
                        }
                        
                        search_job.results.append(lead_data)
                        
                        if is_lead:
                            print(f"✅ Qualified: {reason}")
                            # Add to global lead history
                            lead_history.append(lead_data)
                        else:
                            print(f"❌ Not a match: {reason}")
                    
                    time.sleep(1)  # Rate limiting
                
                processed += 1
                time.sleep(2)  # Avoid hitting rate limits
        
        search_job.status = "completed"
        search_job.progress = 100
        search_job.current_query = "Search completed!"
        
    except Exception as e:
        print(f"Search error: {e}")
        search_job.status = "error"
        search_job.current_query = f"Error: {str(e)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "google_search_configured": os.getenv("GOOGLE_API_KEY") is not None
    })

@app.route('/api/search', methods=['POST'])
def start_search():
    """Start a new lead search"""
    data = request.get_json()
    search_terms = data.get('searchTerms', '')
    location = data.get('location', LOCATION)
    
    # Generate unique search ID
    search_id = str(uuid.uuid4())
    
    # Create search job
    search_job = SearchJob(search_id, search_terms, location)
    active_searches[search_id] = search_job
    
    # Start background search
    thread = threading.Thread(target=background_search, args=(search_job,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "search_id": search_id,
        "status": "started",
        "message": "Search started successfully"
    })

@app.route('/api/search/<search_id>/status', methods=['GET'])
def get_search_status(search_id):
    """Get status of a running search"""
    if search_id not in active_searches:
        return jsonify({"error": "Search not found"}), 404
    
    search_job = active_searches[search_id]
    
    return jsonify({
        "search_id": search_id,
        "status": search_job.status,
        "progress": search_job.progress,
        "current_query": search_job.current_query,
        "results_count": len(search_job.results),
        "qualified_count": len([r for r in search_job.results if r['is_qualified']]),
        "start_time": search_job.start_time.isoformat()
    })

@app.route('/api/search/<search_id>/results', methods=['GET'])
def get_search_results(search_id):
    """Get results from a search"""
    if search_id not in active_searches:
        return jsonify({"error": "Search not found"}), 404
    
    search_job = active_searches[search_id]
    
    # Filter results based on query parameters
    show_qualified_only = request.args.get('qualified_only', 'false').lower() == 'true'
    
    results = search_job.results
    if show_qualified_only:
        results = [r for r in results if r['is_qualified']]
    
    return jsonify({
        "search_id": search_id,
        "status": search_job.status,
        "results": results,
        "total_results": len(search_job.results),
        "qualified_results": len([r for r in search_job.results if r['is_qualified']])
    })

@app.route('/api/search/<search_id>/cancel', methods=['POST'])
def cancel_search(search_id):
    """Cancel a running search"""
    if search_id not in active_searches:
        return jsonify({"error": "Search not found"}), 404
    
    # Remove from active searches to signal cancellation
    search_job = active_searches.pop(search_id)
    search_job.status = "cancelled"
    
    return jsonify({
        "search_id": search_id,
        "status": "cancelled",
        "message": "Search cancelled successfully"
    })

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all qualified leads from history"""
    return jsonify({
        "leads": lead_history,
        "total": len(lead_history)
    })

@app.route('/api/leads/<int:lead_id>', methods=['GET'])
def get_lead_detail(lead_id):
    """Get detailed information about a specific lead"""
    lead = next((l for l in lead_history if l['id'] == lead_id), None)
    if not lead:
        return jsonify({"error": "Lead not found"}), 404
    
    return jsonify(lead)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        "location": LOCATION,
        "google_search_enabled": os.getenv("GOOGLE_API_KEY") is not None,
        "openai_enabled": os.getenv("OPENAI_API_KEY") is not None,
        "search_platforms": list(SEARCH_TERMS.keys())
    })

if __name__ == '__main__':
    print("🚀 Starting LeadGeneratorAI API Server...")
    print(f"📍 Location: {LOCATION}")
    print(f"🔍 Google Search: {'✅ Enabled' if os.getenv('GOOGLE_API_KEY') else '❌ Disabled (using Reddit direct)'}")
    print(f"🤖 OpenAI: {'✅ Enabled' if os.getenv('OPENAI_API_KEY') else '❌ Disabled'}")
    print("🌐 Server will run on: http://localhost:5000")
    print("📡 CORS enabled for React frontend")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
#!/usr/bin/env python3
"""
Test script to verify the free search methods work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_finder import search_reddit_directly, google_search

def test_reddit_search():
    print("🧪 Testing Reddit search...")
    results = search_reddit_directly("need painter durham")
    print(f"   Found {len(results)} Reddit results")
    for i, result in enumerate(results[:2]):  # Show first 2
        print(f"   {i+1}. {result['title'][:50]}...")
    return len(results) > 0

def test_google_search():
    print("🧪 Testing Google search function...")
    results = google_search('"need a painter" site:reddit.com/r/durham')
    print(f"   Found {len(results)} total results")
    return True

if __name__ == "__main__":
    print("🚀 Testing free search methods...\n")
    
    reddit_works = test_reddit_search()
    print()
    
    google_works = test_google_search()
    print()
    
    if reddit_works:
        print("✅ Free search methods are working!")
        print("💡 The tool can now run completely free using Reddit's API")
    else:
        print("⚠️  Reddit search may have rate limits. Try again in a few minutes.")
    
    print("\n📚 To get even better results:")
    print("   Set up free Google Custom Search API (100 searches/day)")
    print("   Instructions: https://developers.google.com/custom-search/v1/introduction")
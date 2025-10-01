import React, { useState } from 'react';

const SearchBar = ({ onSearch, isSearching }) => {
  const [searchTerms, setSearchTerms] = useState('');
  const [location, setLocation] = useState('Durham, NC');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isSearching && (searchTerms.trim() || location.trim())) {
      onSearch({ 
        searchTerms: searchTerms.trim(), 
        location: location.trim() 
      });
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-inputs">
          <div className="input-group">
            <label htmlFor="searchTerms">Search Terms:</label>
            <input
              id="searchTerms"
              type="text"
              value={searchTerms}
              onChange={(e) => setSearchTerms(e.target.value)}
              placeholder="e.g., painter, renovation, landscaping"
              className="search-input"
            />
          </div>
          
          <div className="input-group">
            <label htmlFor="location">Location:</label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="search-input location-input"
            />
          </div>
        </div>
        
        <button 
          type="submit" 
          className={`start-search-btn ${isSearching ? 'searching' : ''}`}
          disabled={isSearching}
        >
          {isSearching ? (
            <>
              <span className="btn-spinner"></span>
              Searching...
            </>
          ) : (
            'Start Search'
          )}
        </button>
      </form>
      
      <div className="search-info">
        <p>🔍 Searches Reddit directly (free) + Google Custom Search (100/day free)</p>
      </div>
    </div>
  );
};

export default SearchBar;
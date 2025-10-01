import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import LeadList from '../components/LeadList';
import '../App.css';

const Home = () => {
  const [activeTab, setActiveTab] = useState('main');
  const [searchResults, setSearchResults] = useState([]);
  const [leadHistory] = useState([
    // Mock data for demonstration
    { id: 1, title: 'Painter needed for kitchen', platform: 'Reddit', date: '2025-09-30' },
    { id: 2, title: 'Looking for bathroom renovation', platform: 'Facebook', date: '2025-09-29' },
    { id: 3, title: 'Deck repair contractor wanted', platform: 'Reddit', date: '2025-09-28' }
  ]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (searchData) => {
    setIsSearching(true);
    setSearchResults([]);
    console.log('Search started with data:', searchData);
    
    try {
      // Import API functions
      const { startSearch, getSearchStatus, getSearchResults } = await import('../services/api');
      
      // Start the search
      const searchResponse = await startSearch(searchData);
      const searchId = searchResponse.search_id;
      
      console.log('Search started with ID:', searchId);
      
      // Poll for search status and results
      const pollInterval = setInterval(async () => {
        try {
          const status = await getSearchStatus(searchId);
          console.log('Search status:', status);
          
          // Get current results
          const results = await getSearchResults(searchId);
          setSearchResults(results.results || []);
          
          // Check if search is complete
          if (status.status === 'completed' || status.status === 'error') {
            clearInterval(pollInterval);
            setIsSearching(false);
            
            if (status.status === 'error') {
              alert('Search completed with errors. Check console for details.');
            }
          }
          
        } catch (error) {
          console.error('Error polling search status:', error);
          clearInterval(pollInterval);
          setIsSearching(false);
          alert('Error monitoring search progress');
        }
      }, 3000); // Poll every 3 seconds
      
      // Set timeout to stop polling after 10 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsSearching(false);
      }, 600000);
      
    } catch (error) {
      console.error('Error starting search:', error);
      setIsSearching(false);
      alert('Error starting search. Make sure the backend server is running.');
    }
  };

  return (
    <div className="home-container">
      {/* Header with tabs */}
      <header className="header">
        <div className="header-left">
          <h1>Lead Finder</h1>
        </div>
        <nav className="header-tabs">
          <button 
            className={`tab ${activeTab === 'main' ? 'active' : ''}`}
            onClick={() => setActiveTab('main')}
          >
            Main
          </button>
          <button 
            className={`tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            Lead History ({leadHistory.length})
          </button>
        </nav>
      </header>

      {/* Main content area */}
      <main className="main-content">
        {activeTab === 'main' && (
          <>
            {/* Search Results - Middle Section */}
            <section className="results-section">
              <h2>Search Results</h2>
              <div className="results-container">
                {isSearching ? (
                  <div className="loading">
                    <div className="spinner"></div>
                    <p>Searching for leads...</p>
                  </div>
                ) : searchResults.length > 0 ? (
                  <LeadList leads={searchResults} />
                ) : (
                  <div className="no-results">
                    <p>No results yet. Click "Start Search" to find leads.</p>
                  </div>
                )}
              </div>
            </section>
          </>
        )}

        {activeTab === 'history' && (
          <section className="history-section">
            <h2>Lead History</h2>
            <div className="history-container">
              {leadHistory.length > 0 ? (
                <LeadList leads={leadHistory} showDate={true} />
              ) : (
                <div className="no-history">
                  <p>No lead history yet.</p>
                </div>
              )}
            </div>
          </section>
        )}
      </main>

      {/* Search Bar - Bottom Section */}
      <footer className="search-footer">
        <SearchBar onSearch={handleSearch} isSearching={isSearching} />
      </footer>
    </div>
  );
};

export default Home;
import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  const handleSearch = () => {
    // Logic to start a search for leads
    console.log('Search started');
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Lead Finder</h1>
      <button onClick={handleSearch} style={{ margin: '10px', padding: '10px 20px' }}>
        Start Search
      </button>
      <div style={{ marginTop: '20px' }}>
        <h2>Results</h2>
        <div style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px' }}>
          {/* Display search results here */}
          No results yet.
        </div>
      </div>
      <div style={{ marginTop: '20px' }}>
        <Link to="/history" style={{ textDecoration: 'none', color: 'blue' }}>
          Go to Lead History
        </Link>
      </div>
    </div>
  );
};

export default Home;
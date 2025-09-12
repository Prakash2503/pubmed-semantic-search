import React, { useState } from 'react';
import './../styles/App.css';

const SearchBar = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (query.trim() && !isLoading) {
      onSearch(query);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="search-bar-container">
      <input
        type="text"
        className="search-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Enter a medical topic, gene, or question..."
        disabled={isLoading}
      />
      <button 
        className="search-button" 
        onClick={handleSearch} 
        disabled={isLoading}
      >
        {isLoading ? 'Searching...' : 'Search'}
      </button>
    </div>
  );
};

export default SearchBar;

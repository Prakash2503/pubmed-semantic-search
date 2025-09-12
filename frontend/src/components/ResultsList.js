import React from 'react';
import ResultItem from './ResultItem';
import './../styles/App.css';

const ResultsList = ({ results }) => {
  if (!results.length) {
    return null; // Don't render anything if there are no results
  }

  return (
    <div className="results-list-container">
      {results.map((item) => (
        <ResultItem key={item.pmid} item={item} />
      ))}
    </div>
  );
};

export default ResultsList;

import React from 'react';
import './../styles/App.css';

const ResultItem = ({ item }) => {
  return (
    <div className="result-item">
      <h3 className="result-title">
        <a href={item.url} target="_blank" rel="noopener noreferrer">
          {item.title}
        </a>
      </h3>
      <p className="result-authors"><strong>Authors:</strong> {item.authors}</p>
      {item.abstract && (
        <p className="result-abstract">{item.abstract.substring(0, 300)}...</p>
      )}
      {item.score && (
        <p className="result-score">
          <strong>Relevance Score:</strong> {item.score.toFixed(4)}
        </p>
      )}
    </div>
  );
};

export default ResultItem;

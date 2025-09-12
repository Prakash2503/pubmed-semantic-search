import React from 'react';
import '../styles/App.css';

const Pagination = ({ currentPage, totalPages, onPageChange }) => {
  if (totalPages <= 1) {
    return null; // Don't render pagination if there's only one page
  }

  const handlePageClick = (page) => {
    if (page >= 1 && page <= totalPages) {
      onPageChange(page);
    }
  };

  // This function creates the array of page numbers to display
  const createPageNumbers = () => {
    const pageNumbers = [];
    for (let i = 1; i <= totalPages; i++) {
      pageNumbers.push(i);
    }
    // For a more advanced component, you could add logic here
    // to show "..." for a large number of pages.
    return pageNumbers;
  };

  return (
    <nav className="pagination-container">
      <button 
        className="pagination-button"
        onClick={() => handlePageClick(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &laquo; Previous
      </button>
      {createPageNumbers().map(number => (
        <button
          key={number}
          className={`pagination-button ${currentPage === number ? 'active' : ''}`}
          onClick={() => handlePageClick(number)}
        >
          {number}
        </button>
      ))}
      <button
        className="pagination-button"
        onClick={() => handlePageClick(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        Next &raquo;
      </button>
    </nav>
  );
};

export default Pagination;

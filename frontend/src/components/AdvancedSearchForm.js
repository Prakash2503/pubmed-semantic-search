import React, { useState } from 'react';
import '../styles/App.css'; // Using the same stylesheet

// The list of all possible search fields available in PubMed
const searchFields = [
  "All Fields", "Affiliation", "Author", "Author - Corporate", "Author - First",
  "Author - Identifier", "Author - Last", "Book", "Conflict of Interest Statements",
  "Date - Completion", "Date - Create", "Date - Entry", "Date - MeSH",
  "Date - Modification", "Date - Publication", "EC/RN Number", "Editor", "Filter",
  "Grants and Funding", "ISBN", "Investigator", "Issue", "Journal", "Language",
  "Location ID", "MeSH Major Topic", "MeSH Subheading", "MeSH Terms", "Other Term",
  "Pagination", "Pharmacological Action", "Publication Type", "Publisher",
  "Secondary Source ID", "Subject - Personal Name", "Supplementary Concept",
  "Text Word", "Title", "Title/Abstract", "Transliterated Title", "Volume"
];

const AdvancedSearchForm = ({ onSearch, isLoading }) => {
  const [queryRows, setQueryRows] = useState([
    // The form starts with a single search row by default
    { id: 1, field: 'All Fields', value: '', operator: 'AND' }
  ]);

  // Updates a specific row when the user types or changes a dropdown
  const handleUpdateRow = (id, field, value) => {
    setQueryRows(rows =>
      rows.map(row => (row.id === id ? { ...row, [field]: value } : row))
    );
  };

  // MODIFIED: This function now accepts an operator to create a new row with
  const handleAddRow = (operator) => {
    setQueryRows(rows => [
      ...rows,
      { id: Date.now(), field: 'All Fields', value: '', operator: operator }
    ]);
  };

  // Removes a specific row from the form
  const handleRemoveRow = (id) => {
    setQueryRows(rows => rows.filter(row => row.id !== id));
  };

  // Gathers the data and sends it to the parent component for API submission
  const handleSubmit = () => {
    const validRows = queryRows.filter(row => row.value.trim() !== '');
    if (validRows.length > 0 && !isLoading) {
      onSearch(validRows);
    }
  };

  return (
    <div className="advanced-search-container">
      {queryRows.map((row, index) => (
        <div key={row.id} className="advanced-search-row">
          {/* The boolean operator (AND/OR/NOT) is only shown for the second row onwards */}
          {index > 0 && (
            <select
              className="boolean-operator"
              value={row.operator}
              onChange={(e) => handleUpdateRow(row.id, 'operator', e.target.value)}
            >
              <option>AND</option>
              <option>OR</option>
              <option>NOT</option>
            </select>
          )}
          <select
            className="field-select"
            value={row.field}
            onChange={(e) => handleUpdateRow(row.id, 'field', e.target.value)}
          >
            {searchFields.map(field => <option key={field} value={field}>{field}</option>)}
          </select>
          <input
            type="text"
            className="search-input"
            placeholder={`Value for ${row.field}...`}
            value={row.value}
            onChange={(e) => handleUpdateRow(row.id, 'value', e.target.value)}
          />
          {queryRows.length > 1 && (
            <button className="remove-row-btn" onClick={() => handleRemoveRow(row.id)}>&times;</button>
          )}
        </div>
      ))}
      <div className="advanced-search-actions">
        {/* MODIFIED: Replaced the single "Add" button with a styled group of three distinct buttons */}
        <div className="add-row-btn-group">
          <button className="add-row-btn and" onClick={() => handleAddRow('AND')}>+ ADD with AND</button>
          <button className="add-row-btn or" onClick={() => handleAddRow('OR')}>+ ADD with OR</button>
          <button className="add-row-btn not" onClick={() => handleAddRow('NOT')}>+ ADD with NOT</button>
        </div>
        <button className="search-button" onClick={handleSubmit} disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Search'}
        </button>
      </div>
    </div>
  );
};

export default AdvancedSearchForm;

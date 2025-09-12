import React, { useState, useEffect } from 'react';
import './styles/App.css';
import SearchBar from './components/SearchBar';
import ResultsList from './components/ResultsList';
import LoadingSpinner from './components/LoadingSpinner';
import AdvancedSearchForm from './components/AdvancedSearchForm';
import Pagination from './components/Pagination';
import KnowledgeGraph from './components/KnowledgeGraph';
import { searchPubMed, fetchKnowledgeGraph } from './services/api';

const RESULTS_PER_PAGE = 10;

function App() {
    const [allResults, setAllResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [hasSearched, setHasSearched] = useState(false);
    const [searchMode, setSearchMode] = useState('simple');
    const [suggestion, setSuggestion] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [lastQuery, setLastQuery] = useState('');
    const [viewMode, setViewMode] = useState('list');
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [isGraphLoading, setIsGraphLoading] = useState(false);

    const handleSearch = async (query) => {
        if (!query || (typeof query === 'string' && query.trim() === '')) return;
        setIsLoading(true);
        setError('');
        setHasSearched(true);
        setAllResults([]);
        setSuggestion('');
        setCurrentPage(1);
        setLastQuery(typeof query === 'string' ? query : 'advanced search');
        setViewMode('list'); 
        try {
            const data = await searchPubMed(query, searchMode);
            setAllResults(data.results);
            setSuggestion(data.suggestion || '');
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // --- REFACTORED: useEffect for Graph Generation ---
    useEffect(() => {
        const getGraphData = async () => {
            if (viewMode === 'graph' && allResults.length > 0 && !isLoading) {
                setIsGraphLoading(true);
                setError('');
                setGraphData({ nodes: [], links: [] });

                const contextText = allResults
                    .slice(0, 10)
                    .filter(res => res.abstract)
                    .map(res => `From article pmid:${res.pmid} url:${res.url}: ${res.title}. ${res.abstract}`)
                    .join('\n\n');

                if (contextText.length < 100) {
                    setError("Not enough content from search results to generate a graph.");
                    setIsGraphLoading(false);
                    return;
                }

                try {
                    const data = await fetchKnowledgeGraph(contextText);
                    if (!data.nodes || data.nodes.length === 0) {
                        setError("The model could not extract any relationships from the text.");
                    }
                    setGraphData(data);
                } catch (err) {
                    setError(err.message);
                } finally {
                    setIsGraphLoading(false);
                }
            }
        };
        getGraphData();
    }, [viewMode, allResults, isLoading]);

    const handleSuggestionClick = (suggestedQuery) => {
        handleSearch(suggestedQuery);
    };

    const lastResultIndex = currentPage * RESULTS_PER_PAGE;
    const firstResultIndex = lastResultIndex - RESULTS_PER_PAGE;
    const currentResults = allResults.slice(firstResultIndex, lastResultIndex);
    const totalPages = Math.ceil(allResults.length / RESULTS_PER_PAGE);

    const renderContent = () => {
        if (isLoading) {
            return <LoadingSpinner />;
        }
        if (error && viewMode !== 'graph') { // Show search errors in list view
             return <p className="error-message">{error}</p>;
        }
        if (!hasSearched) {
            return <p className="info-message">Enter a query to search for PubMed articles.</p>;
        }
        if (viewMode === 'graph') {
            if (isGraphLoading) return <LoadingSpinner />;
            if (error) return <p className="error-message">{error}</p>; // Show graph-specific errors
            if (!graphData.nodes || graphData.nodes.length === 0) {
                return <p className="info-message">No graph data could be generated for this query.</p>;
            }
            return <KnowledgeGraph graphData={graphData} />;
        }
        if (allResults.length > 0) {
            return (
                <>
                    <ResultsList results={currentResults} />
                    <Pagination
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                    />
                </>
            );
        }
        return <p className="info-message">No results found for your query.</p>;
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>PubMed Semantic Search</h1>
                <p>Your AI-powered research assistant</p>
            </header>

            <div className="search-mode-toggle">
                <button className={searchMode === 'simple' ? 'active' : ''} onClick={() => setSearchMode('simple')}>Simple</button>
                <button className={searchMode === 'advanced' ? 'active' : ''} onClick={() => setSearchMode('advanced')}>Advanced</button>
            </div>
            
            {searchMode === 'simple' ? (
                <SearchBar onSearch={handleSearch} isLoading={isLoading} initialQuery={lastQuery} />
            ) : (
                <AdvancedSearchForm onSearch={handleSearch} isLoading={isLoading} />
            )}

            {suggestion && <p className="suggestion">Did you mean: <button onClick={() => handleSearch(suggestion)}>{suggestion}</button></p>}

            {hasSearched && !isLoading && allResults.length > 0 && (
                 <div className="view-mode-toggle">
                    <button className={viewMode === 'list' ? 'active' : ''} onClick={() => setViewMode('list')}>List View</button>
                    <button className={viewMode === 'graph' ? 'active' : ''} onClick={() => setViewMode('graph')}>Graph View</button>
                </div>
            )}

            {renderContent()}
        </div>
    );
}

export default App;

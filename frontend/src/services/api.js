import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api/v1';

export const searchPubMed = async (query, mode = 'simple') => {
    try {
        const response = mode === 'simple'
            ? await axios.get(`${API_URL}/search`, { params: { query, top_k: 100 } })
            : await axios.post(`${API_URL}/advanced-search`, { clauses: query, top_k: 100 });
        return response.data;
    } catch (error) {
        console.error('Search API Error:', error);
        if (error.response) {
            throw new Error(`Search failed: ${error.response.data.detail || 'The server returned an error.'}`);
        } else if (error.request) {
            throw new Error('Network Error: Could not connect to the search service.');
        } else {
            throw new Error(`An unexpected error occurred: ${error.message}`);
        }
    }
};

// --- REFACTORED: fetchKnowledgeGraph now sends context ---
export const fetchKnowledgeGraph = async (contextText) => {
    try {
        const response = await axios.post(`${API_URL}/knowledge-graph`, {
            context_text: contextText
        });
        return response.data;
    } catch (error) {
        console.error('Graph API Error:', error);
        if (error.response) {
            throw new Error(`Graph generation failed: ${error.response.data.detail || 'Server error'}`);
        } else if (error.request) {
            throw new Error('Network Error: Could not connect to the graph service.');
        } else {
            throw new Error(`An unexpected error occurred: ${error.message}`);
        }
    }
};

import React from 'react';

const SearchFilters: React.FC = () => {
    return (
        <div className="search-filters">
            <h3>Filter Results</h3>
            <form>
                <div className="filter-group">
                    <label htmlFor="date-range">Date Range:</label>
                    <input type="date" id="start-date" name="start-date" />
                    <input type="date" id="end-date" name="end-date" />
                </div>
                <div className="filter-group">
                    <label htmlFor="document-type">Document Type:</label>
                    <select id="document-type" name="document-type">
                        <option value="">All</option>
                        <option value="pdf">PDF</option>
                        <option value="txt">Text</option>
                        <option value="markdown">Markdown</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label htmlFor="keywords">Keywords:</label>
                    <input type="text" id="keywords" name="keywords" placeholder="Enter keywords" />
                </div>
                <button type="submit">Apply Filters</button>
            </form>
        </div>
    );
};

export default SearchFilters;
import React from 'react';

const SearchResults: React.FC<{ results: any[] }> = ({ results }) => {
    return (
        <div className="search-results">
            {results.length > 0 ? (
                <ul>
                    {results.map((result, index) => (
                        <li key={index}>
                            <h3>{result.title}</h3>
                            <p>{result.description}</p>
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No results found.</p>
            )}
        </div>
    );
};

export default SearchResults;
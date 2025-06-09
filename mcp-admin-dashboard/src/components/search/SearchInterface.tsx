import React from 'react';

const SearchInterface: React.FC = () => {
    const [query, setQuery] = React.useState('');

    const handleSearch = (event: React.FormEvent) => {
        event.preventDefault();
        // Implement search functionality here
    };

    return (
        <div className="search-interface">
            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search documents..."
                    className="search-input"
                />
                <button type="submit" className="search-button">Search</button>
            </form>
        </div>
    );
};

export default SearchInterface;
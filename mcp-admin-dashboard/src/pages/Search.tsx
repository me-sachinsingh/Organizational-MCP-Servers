import React from 'react';
import SearchInterface from '../components/search/SearchInterface';
import SearchResults from '../components/search/SearchResults';
import SearchFilters from '../components/search/SearchFilters';
import Layout from '../components/common/Layout';

const Search: React.FC = () => {
    return (
        <Layout>
            <h1 className="text-2xl font-bold mb-4">Search Documents</h1>
            <SearchFilters />
            <SearchInterface />
            <SearchResults />
        </Layout>
    );
};

export default Search;
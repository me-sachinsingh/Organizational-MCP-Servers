import { useState, useEffect } from 'react';
import { fetchSearchResults } from '../services/api';

const useSearch = (query) => {
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!query) {
            setResults([]);
            return;
        }

        const search = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await fetchSearchResults(query);
                setResults(data);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        search();
    }, [query]);

    return { results, loading, error };
};

export default useSearch;
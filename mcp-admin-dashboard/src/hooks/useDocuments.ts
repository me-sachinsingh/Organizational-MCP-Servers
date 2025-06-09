import { useEffect, useState } from 'react';
import { fetchDocuments } from '../services/api';
import { Document } from '../types/document';

export const useDocuments = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadDocuments = async () => {
            try {
                const fetchedDocuments = await fetchDocuments();
                setDocuments(fetchedDocuments);
            } catch (err) {
                setError('Failed to load documents');
            } finally {
                setLoading(false);
            }
        };

        loadDocuments();
    }, []);

    return { documents, loading, error };
};
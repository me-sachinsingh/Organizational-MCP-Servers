import { useEffect, useState } from 'react';
import { getServerStatus } from '../services/api';

const useServerStatus = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                const response = await getServerStatus();
                setStatus(response);
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
    }, []);

    return { status, loading, error };
};

export default useServerStatus;
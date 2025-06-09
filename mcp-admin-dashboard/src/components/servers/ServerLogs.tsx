import React, { useEffect, useState } from 'react';
import { fetchServerLogs } from '../../services/api';

const ServerLogs: React.FC = () => {
    const [logs, setLogs] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getLogs = async () => {
            try {
                const fetchedLogs = await fetchServerLogs();
                setLogs(fetchedLogs);
            } catch (err) {
                setError('Failed to fetch logs');
            } finally {
                setLoading(false);
            }
        };

        getLogs();
    }, []);

    if (loading) {
        return <div>Loading logs...</div>;
    }

    if (error) {
        return <div>{error}</div>;
    }

    return (
        <div>
            <h2>Server Logs</h2>
            <ul>
                {logs.map((log, index) => (
                    <li key={index}>{log}</li>
                ))}
            </ul>
        </div>
    );
};

export default ServerLogs;
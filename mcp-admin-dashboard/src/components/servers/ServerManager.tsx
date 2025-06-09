import React, { useEffect, useState } from 'react';
import { ServerCard } from './ServerCard';
import { useServerStatus } from '../../hooks/useServerStatus';

const ServerManager: React.FC = () => {
    const { servers, fetchServerStatus } = useServerStatus();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            await fetchServerStatus();
            setLoading(false);
        };
        loadData();
    }, [fetchServerStatus]);

    if (loading) {
        return <div>Loading server data...</div>;
    }

    return (
        <div>
            <h2>Server Manager</h2>
            <div className="server-list">
                {servers.map(server => (
                    <ServerCard key={server.id} server={server} />
                ))}
            </div>
        </div>
    );
};

export default ServerManager;
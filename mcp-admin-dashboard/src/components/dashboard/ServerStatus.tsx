import React from 'react';
import { useServerStatus } from '../../hooks/useServerStatus';

const ServerStatus: React.FC = () => {
    const { status, error, loading } = useServerStatus();

    if (loading) {
        return <div>Loading server status...</div>;
    }

    if (error) {
        return <div>Error fetching server status: {error.message}</div>;
    }

    return (
        <div>
            <h2>Server Status</h2>
            <ul>
                {status.map((server) => (
                    <li key={server.id}>
                        <strong>{server.name}</strong>: {server.isOnline ? 'Online' : 'Offline'}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ServerStatus;
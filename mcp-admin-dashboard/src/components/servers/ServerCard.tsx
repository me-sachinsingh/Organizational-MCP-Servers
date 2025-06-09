import React from 'react';

interface ServerCardProps {
    serverName: string;
    serverStatus: string;
    serverIP: string;
    onClick: () => void;
}

const ServerCard: React.FC<ServerCardProps> = ({ serverName, serverStatus, serverIP, onClick }) => {
    return (
        <div className="server-card" onClick={onClick}>
            <h3>{serverName}</h3>
            <p>Status: {serverStatus}</p>
            <p>IP Address: {serverIP}</p>
        </div>
    );
};

export default ServerCard;
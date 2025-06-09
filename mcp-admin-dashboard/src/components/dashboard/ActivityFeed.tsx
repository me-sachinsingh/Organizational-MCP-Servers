import React from 'react';

const ActivityFeed: React.FC = () => {
    const activities = [
        { id: 1, message: 'User A uploaded a document.', timestamp: '2025-06-09T10:00:00Z' },
        { id: 2, message: 'User B updated server settings.', timestamp: '2025-06-09T10:05:00Z' },
        { id: 3, message: 'User C searched for "MCP Protocol".', timestamp: '2025-06-09T10:10:00Z' },
    ];

    return (
        <div className="activity-feed">
            <h2>Recent Activities</h2>
            <ul>
                {activities.map(activity => (
                    <li key={activity.id}>
                        <span>{activity.message}</span>
                        <span className="timestamp">{new Date(activity.timestamp).toLocaleString()}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ActivityFeed;
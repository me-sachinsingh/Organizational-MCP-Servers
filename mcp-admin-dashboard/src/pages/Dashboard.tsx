import React from 'react';
import Layout from '../components/common/Layout';
import ServerStatus from '../components/dashboard/ServerStatus';
import MetricsCard from '../components/dashboard/MetricsCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';

const Dashboard: React.FC = () => {
    return (
        <Layout>
            <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
            <ServerStatus />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <MetricsCard />
                <ActivityFeed />
            </div>
        </Layout>
    );
};

export default Dashboard;
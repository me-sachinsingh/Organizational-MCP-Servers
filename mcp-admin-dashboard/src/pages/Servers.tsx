import React from 'react';
import Layout from '../components/common/Layout';
import ServerManager from '../components/servers/ServerManager';
import ServerStatus from '../components/dashboard/ServerStatus';

const Servers: React.FC = () => {
    return (
        <Layout>
            <h1>Server Management</h1>
            <ServerStatus />
            <ServerManager />
        </Layout>
    );
};

export default Servers;
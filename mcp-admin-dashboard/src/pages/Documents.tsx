import React from 'react';
import Layout from '../components/common/Layout';
import DocumentList from '../components/documents/DocumentList';
import DocumentUpload from '../components/documents/DocumentUpload';

const Documents: React.FC = () => {
    return (
        <Layout>
            <h1 className="text-2xl font-bold mb-4">Document Management</h1>
            <DocumentUpload />
            <DocumentList />
        </Layout>
    );
};

export default Documents;
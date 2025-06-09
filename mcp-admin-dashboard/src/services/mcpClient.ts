import axios from 'axios';

const BASE_URL = 'http://localhost:8001'; // Adjust the base URL as needed

const mcpClient = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Example function to get server status
export const getServerStatus = async () => {
    try {
        const response = await mcpClient.get('/server/status');
        return response.data;
    } catch (error) {
        console.error('Error fetching server status:', error);
        throw error;
    }
};

// Example function to upload a document
export const uploadDocument = async (documentData) => {
    try {
        const response = await mcpClient.post('/documents/upload', documentData);
        return response.data;
    } catch (error) {
        console.error('Error uploading document:', error);
        throw error;
    }
};

// Example function to search documents
export const searchDocuments = async (query) => {
    try {
        const response = await mcpClient.get('/documents/search', { params: { q: query } });
        return response.data;
    } catch (error) {
        console.error('Error searching documents:', error);
        throw error;
    }
};

export default mcpClient;
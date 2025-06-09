import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api'; // Update with your API base URL

// Function to get server status
export const getServerStatus = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/server/status`);
        return response.data;
    } catch (error) {
        console.error('Error fetching server status:', error);
        throw error;
    }
};

// Function to get documents
export const getDocuments = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/documents`);
        return response.data;
    } catch (error) {
        console.error('Error fetching documents:', error);
        throw error;
    }
};

// Function to upload a document
export const uploadDocument = async (formData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Error uploading document:', error);
        throw error;
    }
};

// Function to search documents
export const searchDocuments = async (query) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/documents/search`, {
            params: { q: query },
        });
        return response.data;
    } catch (error) {
        console.error('Error searching documents:', error);
        throw error;
    }
};
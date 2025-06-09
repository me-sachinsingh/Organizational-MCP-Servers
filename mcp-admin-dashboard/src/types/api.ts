// This file contains TypeScript types related to API responses and requests.

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}

export interface Document {
    id: string;
    title: string;
    uploadedAt: string;
    size: number;
    type: string;
}

export interface ServerStatus {
    id: string;
    name: string;
    status: 'online' | 'offline' | 'maintenance';
    lastChecked: string;
}

export interface SearchResult {
    documents: Document[];
    totalCount: number;
}
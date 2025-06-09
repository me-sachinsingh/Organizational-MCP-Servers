export interface Document {
    id: string;
    title: string;
    content: string;
    createdAt: Date;
    updatedAt: Date;
    author: string;
    tags?: string[];
}

export interface DocumentUploadResponse {
    success: boolean;
    message: string;
    document?: Document;
}

export interface DocumentListResponse {
    documents: Document[];
    totalCount: number;
}
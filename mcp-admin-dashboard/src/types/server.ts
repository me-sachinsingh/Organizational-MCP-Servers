// This file exports TypeScript types related to server data structures.

export interface Server {
    id: string;
    name: string;
    status: 'online' | 'offline' | 'maintenance';
    ipAddress: string;
    lastChecked: Date;
}

export interface ServerMetrics {
    cpuUsage: number; // Percentage
    memoryUsage: number; // Percentage
    diskUsage: number; // Percentage
    uptime: number; // In seconds
}

export interface ServerLog {
    timestamp: Date;
    message: string;
    level: 'info' | 'warning' | 'error';
}
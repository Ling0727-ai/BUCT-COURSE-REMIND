// src/api/http.ts
/**
 * Global HTTP client wrapper
 * Handles common configurations like base URL, headers, and credentials
 */

const BASE_URL = '/api';

export interface ApiResponse<T = any> {
    success?: boolean;
    message?: string;
    data?: T;
    error?: string;

    [key: string]: any;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;

    const defaultHeaders: HeadersInit = {
        'Content-Type': 'application/json'
    };

    const config: RequestInit = {
        credentials: 'include', // Important for session cookies
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };

    try {
        const response = await fetch(url, config);

        const contentType = response.headers.get('content-type');
        let data: any;

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            // Fallback for non-JSON responses
            // If we expect JSON but get HTML (like error pages), this might fail parsing if we assume JSON later
            // For now, return text if not JSON
            const text = await response.text();
            try {
                data = JSON.parse(text);
            } catch {
                data = {message: text};
            }
        }

        if (!response.ok) {
            // Standardize error format
            const errorMsg = data.error || data.message || `HTTP Error ${response.status}`;
            throw new Error(errorMsg);
        }

        return data as T;
    } catch (error: any) {
        console.error('API Request Failed:', error);
        throw error;
    }
}

export const http = {
    get: <T>(url: string, params?: Record<string, string>) => {
        let query = '';
        if (params) {
            query = '?' + new URLSearchParams(params).toString();
        }
        return request<T>(url + query, {method: 'GET'});
    },
    post: <T>(url: string, body: any) => {
        return request<T>(url, {method: 'POST', body: JSON.stringify(body)});
    },
    put: <T>(url: string, body: any) => {
        return request<T>(url, {method: 'PUT', body: JSON.stringify(body)});
    },
    delete: <T>(url: string) => {
        return request<T>(url, {method: 'DELETE'});
    }
};


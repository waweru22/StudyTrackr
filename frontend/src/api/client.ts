export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

interface RequestOptions {
    method?: RequestMethod;
    headers?: Record<string, string>;
    body?: any;
}

export async function apiRequest<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const token = localStorage.getItem('token');

    const headers: Record<string, string> = {
        ...options.headers,
    };

    // Only set JSON content type if not FormData and not explicitly set
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
        headers['Content-Type'] = 'application/json';
    }

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
        method: options.method || 'GET',
        headers,
    };

    if (options.body) {
        config.body = options.body instanceof FormData ? options.body : JSON.stringify(options.body);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    if (!response.ok) {
        // Try to parse error message
        let errorMessage = 'Something went wrong';
        try {
            const errorData = await response.json();
            errorMessage = errorData.error || errorData.msg || errorMessage;

            // Handle Token Expiration
            if (response.status === 401 && errorMessage.includes('Token has expired')) {
                localStorage.removeItem('token');
                localStorage.removeItem('user_id');
                // Force redirect to login
                window.location.href = '/login';
                throw new Error("Session expired. Please login again.");
            }

        } catch (e) {
            if (e instanceof Error && e.message === "Session expired. Please login again.") {
                throw e;
            }
            errorMessage = response.statusText;
        }
        throw new Error(errorMessage);
    }

    // Handle 204 No Content
    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

export const api = {
    get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
    post: <T>(endpoint: string, body: any) => apiRequest<T>(endpoint, { method: 'POST', body }),
    put: <T>(endpoint: string, body: any) => apiRequest<T>(endpoint, { method: 'PUT', body }),
    delete: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'DELETE' }),
};

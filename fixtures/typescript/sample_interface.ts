// Sample TypeScript interfaces and types file

export interface User {
    id: string;
    name: string;
    email: string;
    age?: number;
}

export interface Product {
    id: string;
    title: string;
    price: number;
    inStock: boolean;
}

export type UserRole = 'admin' | 'user' | 'guest';

export type Status = 'active' | 'inactive' | 'pending';

export type ApiResponse<T> = {
    success: boolean;
    data?: T;
    error?: string;
};

interface InternalConfig {
    apiUrl: string;
    timeout: number;
}

type Nullable<T> = T | null;

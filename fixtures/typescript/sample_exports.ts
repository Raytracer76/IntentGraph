// Sample TypeScript exports file

export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

export enum Status {
    PENDING = "pending",
    APPROVED = "approved",
    REJECTED = "rejected"
}

export function processData(data: any[]): any[] {
    return data.filter(item => item !== null);
}

export function logMessage(level: LogLevel, message: string): void {
    console.log(`[${LogLevel[level]}] ${message}`);
}

export const API_URL = "https://api.example.com";
export const MAX_RETRIES = 3;

function internalHelper(): void {
    // Not exported
}

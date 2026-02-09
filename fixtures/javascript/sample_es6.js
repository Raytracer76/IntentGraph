// ES6 module with import/export
import { fetchData } from './api';
import Logger from './logger';
import * as Config from './config';

export function initialize(options) {
    const logger = new Logger(options);
    logger.log('Initializing...');
    return logger;
}

export async function loadData(id) {
    try {
        const data = await fetchData(id);
        return data;
    } catch (error) {
        console.error('Failed to load data:', error);
        throw error;
    }
}

export class Application {
    constructor(config) {
        this.config = config;
        this.logger = new Logger(config);
    }

    async run() {
        this.logger.log('Running application...');
        const data = await loadData(this.config.dataId);
        return data;
    }
}

export default Application;

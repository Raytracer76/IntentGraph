// Sample TypeScript imports file

import { Calculator } from './sample_class';
import { User, Product, UserRole } from './sample_interface';
import { processData } from './sample_exports';

export class DataProcessor {
    private calc: Calculator;

    constructor() {
        this.calc = new Calculator();
    }

    processUser(user: User): void {
        console.log(`Processing user: ${user.name}`);
    }

    processProduct(product: Product): void {
        console.log(`Processing product: ${product.title}`);
    }

    calculateTotal(prices: number[]): number {
        return prices.reduce((sum, price) => {
            return this.calc.add(price);
        }, 0);
    }
}

export function validateRole(role: UserRole): boolean {
    return ['admin', 'user', 'guest'].includes(role);
}

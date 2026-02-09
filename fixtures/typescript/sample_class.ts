// Sample TypeScript class file for testing

export class Calculator {
    private value: number = 0;

    constructor(initialValue: number = 0) {
        this.value = initialValue;
    }

    add(num: number): number {
        this.value += num;
        return this.value;
    }

    subtract(num: number): number {
        this.value -= num;
        return this.value;
    }

    multiply(num: number): number {
        this.value *= num;
        return this.value;
    }

    divide(num: number): number {
        if (num === 0) {
            throw new Error("Division by zero");
        }
        this.value /= num;
        return this.value;
    }

    reset(): void {
        this.value = 0;
    }

    getValue(): number {
        return this.value;
    }
}

class InternalHelper {
    static format(value: number): string {
        return value.toFixed(2);
    }
}

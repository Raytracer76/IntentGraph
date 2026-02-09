// Class declarations
class BaseClass {
    constructor(name) {
        this.name = name;
    }

    getName() {
        return this.name;
    }

    static createDefault() {
        return new BaseClass('default');
    }
}

class ExtendedClass extends BaseClass {
    constructor(name, value) {
        super(name);
        this.value = value;
    }

    getValue() {
        return this.value;
    }

    static fromValue(value) {
        return new ExtendedClass('auto', value);
    }
}

const ClassExpression = class {
    constructor() {
        this.type = 'expression';
    }
};

export { BaseClass, ExtendedClass, ClassExpression };
export default BaseClass;

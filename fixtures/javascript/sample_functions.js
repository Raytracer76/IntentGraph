// Various function patterns
function regularFunction() {
    return 'regular';
}

const arrowFunction = () => {
    return 'arrow';
};

const arrowFunctionShort = () => 'shorthand';

async function asyncFunction() {
    await Promise.resolve();
    return 'async';
}

const asyncArrowFunction = async () => {
    await Promise.resolve();
    return 'async arrow';
};

function* generatorFunction() {
    yield 1;
    yield 2;
}

function functionWithParams(a, b, c = 10) {
    return a + b + c;
}

const anonymousExport = function() {
    return 'anonymous';
};

export {
    regularFunction,
    arrowFunction,
    arrowFunctionShort,
    asyncFunction,
    asyncArrowFunction,
    generatorFunction,
    functionWithParams,
    anonymousExport
};

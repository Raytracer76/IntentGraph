// CommonJS module with exports
const helper = require('./helper');
const utils = require('./utils');

function processData(data) {
    return helper.transform(data);
}

function validateInput(input) {
    if (!input) {
        return false;
    }
    return utils.validate(input);
}

class DataProcessor {
    constructor(config) {
        this.config = config;
    }

    process(data) {
        return processData(data);
    }
}

module.exports = {
    processData,
    validateInput,
    DataProcessor
};

const _ = require('lodash');

function toBoolean(value) {
    if (!value) {
        return false;
    }
    if (typeof value == 'number' || typeof value == 'boolean') {
        return !!value;
    }
    return _.replace(_.trim(value.toLowerCase()), /[""'']/ig, '') === 'true' ? true : false;
}

function parseIfJson(str) {
  try {
    return JSON.parse(str);
  } catch (e) {
    return false;
  }
}

function isValidJsonRequest(headerToCheck) {
  return headerToCheck &&
  (headerToCheck === '*/*' || headerToCheck.toLowerCase().includes('json'));
}

function isPromise(promise) {
    return !!promise && typeof promise.then === 'function'
}

_.mixin({
    'toBoolean': toBoolean,
    'isPromise': isPromise,
    'parseIfJson': parseIfJson,
    'isValidJsonRequest': isValidJsonRequest
});

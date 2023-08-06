const _ = require('lodash');
const REPORT_TTL_MS = 30 * 1000;
const Constants = require('../utils/constants');

class SecurityActivity {
    constructor(
        id,
        status,
        ipAddress,
        reponse,
        verb,
        path,
        user,
        host,
        pathParams,
        queryParams,
        requestHeaders,
        responseHeaders,
        requestBodySchema,
        responseBodySchema
    ) {
        this._events = [];
        this._requestId = id;
        this._status_code = status;
        this._ipAddresses = [ipAddress];
        this._securityResponse = reponse;
        this._date = new Date();
        this._requestVerb = verb;
        this._requestPath = path;
        this._user = user ? user : '';
        this._duration = 0;
        this._closed = false;
        this._host = host;
        this._pathParams = pathParams;
        this._queryParams = queryParams;
        this._requestHeaders = requestHeaders;
        this._responseHeaders = responseHeaders;
        this._requestBodySchema = requestBodySchema;
        this._responseBodySchema = responseBodySchema;
    }

    addEvent(event) {
        if (_.isObject(event)) {
            this._events.push(event);
        }
    }

    set events(events) {
        if (_.isArray(events)) {
            this._events = events;
        }
    }

    set user(user) {
        if (_.isString(user)) {
            this._user = user;
        }
    }

    set duration(duration) {
        this._duration = duration;
    }

    set host(host) {
        if (_.isString(host)) {
            this._host = host;
        }
    }

    set pathParams(pathParams) {
        if (pathParams) {
            this._pathParams = pathParams;
        }
    }

    set securityResponse(securityResponse) {
        if (securityResponse) {
            this._securityResponse = securityResponse;
        }
    }

    set queryParams(queryParams) {
        if (queryParams) {
            this._queryParams = queryParams;
        }
    }

    set requestId(id) {
        if (id) {
            this._requestId = id;
        }
    }

    set ipAddresses(ipAddresses) {
        if (_.isArray(ipAddresses) && ipAddresses[0]) {
            this._ipAddresses = ipAddresses;
        }
    }

    set date(date) {
        if (_.isDate(date)) {
            this._date = date;
        }
    }

    set requestVerb(requestVerb) {
        if (_.isString(requestVerb)) {
            this._requestVerb = requestVerb;
        }
    }

    set requestPath(requestPath) {
        if (_.isString(requestPath)) {
            this._requestPath = requestPath.replace(
                Constants.PATH_TRIMMING_REGEX,
                ''
            );
        }
    }

    set responseBodySchema(responseBodySchema) {
        if (_.isObject(responseBodySchema)) {
            this._responseBodySchema = responseBodySchema;
        }
    }

    set requestBodySchema(requestBodySchema) {
        if (_.isObject(requestBodySchema)) {
            this._requestBodySchema = requestBodySchema;
        }
    }

    set status_code(statusCode) {
        if (statusCode) {
            this._status_code = statusCode;
        }
    }

    set requestHeaders(requestHeaders) {
        if (_.isObject(requestHeaders)) {
            this._requestHeaders = filterSupportedHttpHeaders(requestHeaders);
        }
    }

    set responseHeaders(responseHeaders) {
        if (_.isObject(responseHeaders)) {
            this._responseHeaders = filterSupportedHttpHeaders(responseHeaders);
        }
    }

    set closed(closed) {
        this._closed = closed;
    }

    get requestId() {
        return this._requestId;
    }

    get user() {
        return this._user;
    }

    get duration() {
        return this._duration;
    }

    get host() {
        return this._host;
    }

    get pathParams() {
        return this._pathParams;
    }

    get securityResponse() {
        return this._securityResponse;
    }

    get queryParams() {
        return this._queryParams;
    }

    get ipAddresses() {
        return this._ipAddresses;
    }

    get date() {
        return this._date;
    }

    get requestVerb() {
        return this._requestVerb;
    }

    get requestPath() {
        return this._requestPath;
    }

    get responseBodySchema() {
        return this._responseBodySchema;
    }

    get requestBodySchema() {
        return this._requestBodySchema;
    }

    get status_code() {
        return this._status_code;
    }

    get requestHeaders() {
        return this._requestHeaders;
    }

    get responseHeaders() {
        return this._responseHeaders;
    }

    get closed() {
        return this._closed;
    }

    get events() {
        return this._events;
    }

    setClosed() {
        this.closed = true;
    }

    isClosed() {
        this._checkTTL();
        return this.closed;
    }

    _checkTTL() {
        const now = new Date();
        if (now - this._date >= REPORT_TTL_MS) {
            this.setClosed();
        }
    }

    getJson() {
        return {
            events: this.events,
            requestId: this.requestId,
            ipAddresses: this.ipAddresses,
            securityResponse: this.securityResponse,
            statusCode: this.statusCode,
            date: this.date,
            requestVerb: this.requestVerb,
            requestPath: this.requestPath,
            user: this.user,
            duration: this.duration,
            closed: this.closed,
            host: this.host,
            pathParams: this.pathParams,
            queryParams: this.queryParams,
            requestHeaders: this.requestHeaders,
            responseHeaders: this.responseHeaders,
            requestBodySchema: this.requestBodySchema,
            responseBodySchema: this.responseBodySchema
        };
    }
}

function filterSupportedHttpHeaders(headers) {
    const SUPPORTED_HTTP_HEADERS = [
        'accept',
        'access-control-allow-origin',
        'content-length',
        'content-type',
        'from',
        'host',
        'origin',
        'referer',
        'server'
    ];
    const filteredHeaders = {};
    for (const [key, value] of Object.entries(headers)) {
        if (SUPPORTED_HTTP_HEADERS.includes(key.toLowerCase())) {
            filteredHeaders[key] = value;
        }
    }

    return filteredHeaders;
}

module.exports = {
    SecurityActivity
};

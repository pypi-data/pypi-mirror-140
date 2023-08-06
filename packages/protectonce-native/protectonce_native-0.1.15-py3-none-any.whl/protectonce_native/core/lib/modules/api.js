require('../utils/common_utils');
const _ = require('lodash');
const Constants = require('../utils/constants');
const { Route, Api, Inventory } = require('../reports/inventory');
const { SecurityActivity } = require('../reports/security_activity');
const HeartbeatCache = require('../reports/heartbeat_cache');
const Logger = require('../utils/logger');
const toJsonSchema = require('to-json-schema');

function storeRoute(inputData) {
    try {
        const routes = inputData.data;
        if (!_.isArray(routes)) {
            return;
        }

        let inventory = HeartbeatCache.getInventory();
        routes.forEach((route) => {
            route.paths.forEach((path) => {
                if (!_.isString(path) || !_.isArray(route.methods) || !_.isString(route.host)) {
                    return;
                }
                const trimmedPath = path.replace(
                    Constants.PATH_TRIMMING_REGEX,
                    ''
                );
                const supportedMethods = route.methods.filter((method) =>
                    supportedHttpMethods().includes(method)
                );
                const routeToBeAdded = new Route(
                    trimmedPath,
                    supportedMethods,
                    route.host
                );
                inventory = populateInventory(inventory, routeToBeAdded);
            });
        });

        HeartbeatCache.cacheInventory(inventory);
    } catch (error) {
        Logger.write(
            Logger.ERROR && `api.StoreRoute: Failed to store route: ${error}`
        );
    }
}

function populateInventory(inventory, routeToBeAdded) {
    if (inventory && inventory.api && _.isArray(inventory.api.routes)) {
        addRouteToExistingInventory(inventory, routeToBeAdded);
        return inventory;
    }
    return new Inventory(new Api([routeToBeAdded]));
}

function addRouteToExistingInventory(inventory, routeToBeAdded) {
    const existingRoute = inventory.api.routes.find(
        (route) => route.path === routeToBeAdded.path
    );
    if (existingRoute) {
        existingRoute.addMethods(routeToBeAdded.methods);
        return;
    }
    inventory.api.addRoute(routeToBeAdded);
}

function parseHttpData(data) {
    try {
        const inputData = data.data;
        let securityActivity = HeartbeatCache.getReport(inputData.poSessionId);
        securityActivity = mapSecurityActivity(securityActivity, inputData);
        HeartbeatCache.cacheReport(securityActivity);
        return inputData;
    } catch (error) {
        Logger.write(
            Logger.ERROR &&
                `api.parseHttpData: Failed to parse http data: ${error}`
        );
        return {};
    }
}

function mapSecurityActivity(securityActivity, inputData) {
    if (!securityActivity) {
        securityActivity = new SecurityActivity();
        securityActivity.date = new Date();
        securityActivity.duration = 0;
        securityActivity.closed = false;
        securityActivity.requestId = inputData.poSessionId;
    }
    securityActivity.url = inputData.url;
    securityActivity.requestVerb = inputData.method;
    securityActivity.requestPath = inputData.requestPath;
    securityActivity.user = inputData.user;
    if(_.isObject(inputData.queryParams)) {
        securityActivity.queryParams =  toJsonSchema(inputData.queryParams);
    }
    
    securityActivity.host = inputData.host;
    if(_.isObject(inputData.pathParams)) {
        securityActivity.pathParams =  toJsonSchema(inputData.pathParams);
    }
    securityActivity.ipAddresses = [inputData.sourceIP];
    securityActivity.requestHeaders = inputData.requestHeaders;
    securityActivity.responseHeaders = inputData.responseHeaders;
    const requestHeaders = inputData.requestHeaders
        ? inputData.requestHeaders
        : securityActivity.requestHeaders
        ? securityActivity.requestHeaders
        : {};

    const responseHeaders = inputData.responseHeaders
        ? inputData.responseHeaders
        : securityActivity.responseHeaders
        ? securityActivity.responseHeaders
        : {};

    securityActivity.requestBodySchema = getJsonSchema(
        inputData.requestBody,
        requestHeaders && requestHeaders['content-type']
    );
    securityActivity.responseBodySchema = getJsonSchema(
        inputData.responseBody,
        responseHeaders && responseHeaders['content-type']
    );

    securityActivity.statusCode = inputData.statusCode;

    return securityActivity;
}

function getJsonSchema(body, headerToCheck) {
    if (!body) {
        return;
    }
    const parsedBody = _.parseIfJson(new Buffer.from(body).toString());
    if (
        headerToCheck &&
        (headerToCheck === '*/*' ||
            headerToCheck.toLowerCase().includes('json')) &&
        parsedBody
    ) {
        return toJsonSchema(parsedBody);
    }
}

function supportedHttpMethods() {
    return [
        'GET',
        'PUT',
        'POST',
        'DELETE',
        'PATCH',
        'HEAD',
        'OPTIONS',
        'CONNECT',
        'TRACE'
    ];
}

module.exports = {
    storeRoute,
    parseHttpData
};

const RuleSet = require("./ruleset");
const Metrics = require("./metrics");
const DataFrame = require("./dataFrame");
const WAFallowList = require('./allowList/allowlist_manager');

const Logger = require('../../utils/logger');

class WAF {
    constructor(ruleSetDef, context) {
        this.context = context || {};
        this.metrics = this.context.metrics = this.context.metrics || new Metrics();
        this.updateRuleset(ruleSetDef);
    }

    updateRuleset(newRulesetDef) {
        this.AllowListManager = new WAFallowList(newRulesetDef);
        this.ruleset = new RuleSet(newRulesetDef, this.context);
    }

    createDataFrame() {
        return new DataFrame(this.ruleset);
    }

    scanHttpHeaders(requestData) {
        try {
            const request = this.context.poContext.get(requestData.data.poSessionId);
            Logger.write(Logger.DEBUG && `waf: Scanning http headers: ${requestData.data.poSessionId}, request: ${request}`);
            const findings = this.checkHTTPRequest(request);
            return { 'findings': findings, 'poSessionId': requestData.data.poSessionId };
        } catch (e) {
            Logger.write(Logger.DEBUG && `waf: Failed to scan http data data: ${e}`);
        }
    }

    scanHttpBody(requestData) {

        let result = {
            action: 'none'
        };
        try {
            if (!requestData.data.requestBody) {
                return result;
            }
            const request = this.context.poContext.get(requestData.data.poSessionId);
            request.body = new Buffer.from(requestData.data.requestBody).toString();

            Logger.write(Logger.DEBUG && `waf: Scanning http body: ${requestData.data.poSessionId}, request: ${request.body}`);
            const findings = this.checkHTTPRequest(request);
            return { 'findings': findings, 'poSessionId': requestData.data.poSessionId };
        } catch (e) {
            Logger.write(Logger.DEBUG && `httpServer: Failed to store session data ${e}`);
        }

        return result;
    }

    checkHTTPRequest(request, dataFrame /*optional*/) {
        if (this.AllowListManager.shouldBypassRequest(request)) {
            return Promise.resolve([]);
        }
        if (request.queryParams) {
            request.queryParams = this.AllowListManager.filterParameters(request);
        }
        dataFrame = dataFrame || this.createDataFrame();

        let findings = [];
        this.ruleset.mapData("http.request", request, (targetName, valueList) => {
            dataFrame.addAndCheckCB(
                targetName,
                (finding) => {
                    findings.push(finding);
                },
                () => {
                    /* this target done */
                },
                ...valueList
            );
        },
            () => {
                /* all fields done */
                // Do nothing
            });
        return findings;
    }
}

WAF.DataFrame = DataFrame;

module.exports = WAF;
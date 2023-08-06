const _ = require('lodash');

const { ReportType } = require('../reports/report');
const { SecurityActivity} = require('../reports/security_activity');
const { WAFEvent } = require('../reports/event');
const HeartbeatCache = require('../reports/heartbeat_cache');

function createSecurityActivity(data) {
  if (!_.isString(data.data.poSessionId)) {
    return;
  }
  let securityActivity = HeartbeatCache.getReport(data.data.poSessionId);
  if (!securityActivity) {
    securityActivity = new SecurityActivity(
      data.data.poSessionId,
      '',
      data.data.sourceIP,
      '',
      '',
      data.data.path,
      data.data.user,
      data.data.host,
      data.data.pathParams,
      data.data.queryParams,
      data.data.headers,
      data.data.requestBodySchema,
      data.data.responseBodySchema
    );
  }
  HeartbeatCache.cacheReport(securityActivity);
}

function generateWafEvents(data) {
  const findings = data.data.findings;
  if (!_.isArray(findings) || findings.length === 0) {
    return { action: 'none' };
  }

  const poSessionId = data.data.poSessionId;
  let securityActivity = HeartbeatCache.getReport(poSessionId);
  if(!securityActivity) {
     securityActivity = new SecurityActivity(poSessionId);
  }
  let blocked = false;
  for (let finding of findings) {
    blocked = blocked || finding.action === ReportType.REPORT_TYPE_BLOCK;
    const event = new WAFEvent(
      poSessionId,
      finding.action === ReportType.REPORT_TYPE_BLOCK,
      finding.flowName
    );
    securityActivity.addEvent(event);
  }

  HeartbeatCache.cacheReport(securityActivity);

  if (blocked) {
    return { action: 'abort' };
  }

  return { action: 'none' };
}

module.exports = {
  createSecurityActivity: createSecurityActivity,
  generateWafEvents: generateWafEvents
};

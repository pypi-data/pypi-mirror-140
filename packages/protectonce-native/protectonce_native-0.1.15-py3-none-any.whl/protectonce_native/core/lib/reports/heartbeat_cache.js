class HeartbeatCache {
  constructor() {
    this._cache = {
      reports: {},
      inventory: {}
    };
  }

  cacheInventory(inventory) {
    this._cache.inventory = inventory;
  }

  getInventory() {
    return this._cache.inventory;
  }

  cacheReportEvents(report) {
    if (!this._cache.reports[report.requestId]) {
      this._cache.reports[report.requestId] = report;
    } else {
      this._cache.reports[report.requestId].events.push(...report.events);
    }
  }

  cacheReport(report) {
    this._cache.reports[report.requestId] = report;
  }

  getReport(requestId) {
    return this._cache.reports[requestId]
      ? this._cache.reports[requestId]
      : null;
  }

  flush() {
    const reports = [];
    for (let requestId in this._cache.reports) {
      const report = this._cache.reports[requestId];
      if (report.isClosed()) {
        reports.push(this._cache.reports[report.requestId].getJson());
        delete this._cache.reports[requestId];
      }
    }
    const inventory = this._cache.inventory;
    this._cache.inventory = {};
    return {
      reports,
      inventory
    };
  }

  setClosed(id) {
    if (this._cache.reports[id]) {
      this._cache.reports[id].setClosed();
    }
  }
}

module.exports = new HeartbeatCache();

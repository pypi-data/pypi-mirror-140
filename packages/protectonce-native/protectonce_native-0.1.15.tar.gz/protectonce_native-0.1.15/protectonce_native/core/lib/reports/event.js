class Event {
    constructor(
      category,
      request_id,
      blocked,
      confidence_level,
      date,
      date_started,
      type,
      duration,
      security_response,
      status
    ) {
      (this.category = category),
        (this.request_id = request_id),
        (this.blocked = blocked),
        (this.confidence_level = confidence_level),
        (this.date = date || new Date()),
        (this.date_started = date_started || new Date()),
        (this.type = type),
        (this.duration = duration),
        (this.security_response = security_response),
        (this.status = status);
    }
  }
  
  class WAFEvent extends Event {
    constructor(request_id, blocked, type) {
      super('waf', request_id, blocked, 50, new Date(), new Date(), type);
    }
  }

  module.exports = {
      Event,
      WAFEvent
  };
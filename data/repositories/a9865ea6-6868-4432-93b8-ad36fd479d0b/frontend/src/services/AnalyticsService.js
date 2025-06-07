// frontend/src/services/AnalyticsService.js
class AnalyticsService {
  constructor() {
    this.queue = [];
    this.batchSize = 10;
    this.flushInterval = 5000; // 5 seconds
    this.sessionId = this.generateSessionId();
    this.userId = this.getUserId();
    
    this.startBatchProcessor();
  }

  generateSessionId() {
    const stored = sessionStorage.getItem('codeflow_session_id');
    if (stored) return stored;
    
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('codeflow_session_id', sessionId);
    return sessionId;
  }

  getUserId() {
    let userId = localStorage.getItem('codeflow_user_id');
    if (!userId) {
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem('codeflow_user_id', userId);
    }
    return userId;
  }

  track(event, properties = {}) {
    const enrichedEvent = {
      ...event,
      ...properties,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      userId: this.userId,
      url: window.location.href,
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    };

    this.queue.push(enrichedEvent);
    
    if (this.queue.length >= this.batchSize) {
      this.flush();
    }
  }

  // Specific tracking methods
  trackPageView(page) {
    this.track({
      type: 'page_view',
      page,
      title: document.title
    });
  }

  trackFileInteraction(type, filePath, details = {}) {
    this.track({
      type: 'file_interaction',
      interactionType: type,
      filePath,
      ...details
    });
  }

  trackGraphInteraction(type, nodeId, details = {}) {
    this.track({
      type: 'graph_interaction',
      interactionType: type,
      nodeId,
      ...details
    });
  }

  trackSearch(query, resultCount, version) {
    this.track({
      type: 'search',
      query,
      resultCount,
      version
    });
  }

  trackVersionSwitch(fromVersion, toVersion) {
    this.track({
      type: 'version_switch',
      fromVersion,
      toVersion
    });
  }

  trackTaskCompletion(taskType, duration, success) {
    this.track({
      type: 'task_completion',
      taskType,
      duration,
      success
    });
  }

  trackError(error, context = {}) {
    this.track({
      type: 'error',
      message: error.message,
      stack: error.stack,
      context
    });
  }

  startBatchProcessor() {
    setInterval(() => {
      if (this.queue.length > 0) {
        this.flush();
      }
    }, this.flushInterval);

    // Flush on page unload
    window.addEventListener('beforeunload', () => {
      this.flush();
    });
  }

  async flush() {
    if (this.queue.length === 0) return;

    const events = [...this.queue];
    this.queue = [];

    try {
      await fetch('/api/analytics/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events }),
        keepalive: true
      });
    } catch (error) {
      console.warn('Failed to send analytics:', error);
      // Re-queue events if they failed to send
      this.queue.unshift(...events);
    }
  }

  getSessionMetrics() {
    return {
      sessionId: this.sessionId,
      userId: this.userId,
      startTime: sessionStorage.getItem('session_start_time') || Date.now(),
      eventsTracked: this.queue.length
    };
  }
}

export default new AnalyticsService();

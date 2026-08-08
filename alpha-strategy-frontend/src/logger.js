// Frontend Logger for Alpha Strategy Parser
class FrontendLogger {
  constructor() {
    this.logs = [];
    this.startTime = Date.now();
    this.enabled = true;
  }

  log(level, message, data = null) {
    if (!this.enabled) return;
    
    const timestamp = new Date().toISOString();
    const elapsed = Date.now() - this.startTime;
    
    const logEntry = {
      timestamp,
      elapsed: `${elapsed}ms`,
      level,
      message,
      data: data ? JSON.stringify(data, null, 2) : null
    };
    
    this.logs.push(logEntry);
    
    // Console output with colors
    const colors = {
      INFO: '\x1b[36m',    // Cyan
      WARN: '\x1b[33m',    // Yellow
      ERROR: '\x1b[31m',   // Red
      DEBUG: '\x1b[35m',   // Magenta
      SUCCESS: '\x1b[32m', // Green
      RESET: '\x1b[0m'
    };
    
    const color = colors[level] || colors.INFO;
    console.log(`${color}[${level}]${colors.RESET} [${elapsed}ms] ${message}`, data || '');
  }

  info(message, data = null) {
    this.log('INFO', message, data);
  }

  warn(message, data = null) {
    this.log('WARN', message, data);
  }

  error(message, data = null) {
    this.log('ERROR', message, data);
  }

  debug(message, data = null) {
    this.log('DEBUG', message, data);
  }

  success(message, data = null) {
    this.log('SUCCESS', message, data);
  }

  // Performance timing
  time(label) {
    const start = performance.now();
    return {
      end: () => {
        const duration = performance.now() - start;
        this.info(`⏱️ ${label} completed in ${duration.toFixed(2)}ms`);
        return duration;
      }
    };
  }

  // Get all logs
  getLogs() {
    return this.logs;
  }

  // Export logs to file
  exportLogs() {
    const logData = {
      sessionStart: new Date(this.startTime).toISOString(),
      totalDuration: `${Date.now() - this.startTime}ms`,
      logs: this.logs
    };
    
    const blob = new Blob([JSON.stringify(logData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Clear logs
  clear() {
    this.logs = [];
    this.startTime = Date.now();
  }
}

// Create global logger instance
export const logger = new FrontendLogger();

// Make it available globally for debugging
if (typeof window !== 'undefined') {
  window.logger = logger;
}

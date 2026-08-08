// Simple debug panel for frontend logging
export function createDebugPanel() {
  // Create debug panel HTML
  const debugPanel = document.createElement('div');
  debugPanel.id = 'debug-panel';
  debugPanel.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    width: 400px;
    max-height: 300px;
    background: rgba(0, 0, 0, 0.9);
    color: #00ff00;
    font-family: monospace;
    font-size: 12px;
    padding: 10px;
    border: 1px solid #333;
    border-radius: 5px;
    overflow-y: auto;
    z-index: 10000;
    display: none;
  `;
  
  const toggleBtn = document.createElement('button');
  toggleBtn.textContent = 'Debug';
  toggleBtn.style.cssText = `
    position: fixed;
    top: 10px;
    right: 10px;
    background: #333;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 3px;
    cursor: pointer;
    z-index: 10001;
  `;
  
  document.body.appendChild(toggleBtn);
  document.body.appendChild(debugPanel);
  
  let isVisible = false;
  
  toggleBtn.addEventListener('click', () => {
    isVisible = !isVisible;
    debugPanel.style.display = isVisible ? 'block' : 'none';
  });
  
  // Override console.log to show in debug panel
  const originalLog = console.log;
  console.log = function(...args) {
    originalLog.apply(console, args);
    
    if (isVisible) {
      const logEntry = document.createElement('div');
      logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${args.join(' ')}`;
      logEntry.style.marginBottom = '2px';
      debugPanel.appendChild(logEntry);
      debugPanel.scrollTop = debugPanel.scrollHeight;
      
      // Keep only last 50 entries
      while (debugPanel.children.length > 50) {
        debugPanel.removeChild(debugPanel.firstChild);
      }
    }
  };
  
  return { debugPanel, toggleBtn };
}

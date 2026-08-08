// Backend service for frontend with comprehensive logging
import { logger } from './logger.js';

export class BackendService {
  static async executeStrategyFullScale(strategy) {
    const timer = logger.time('API Call - executeStrategyFullScale');
    
    try {
      logger.info('🚀 Starting strategy execution', { strategy: strategy.substring(0, 100) + '...' });
      
      // Log request details
      const requestData = {
        url: 'http://127.0.0.1:8000/execute-full-scale',
        method: 'POST',
        strategyLength: strategy.length,
        timestamp: new Date().toISOString()
      };
      logger.debug('📤 API Request Details', requestData);
      
      // Start fetch with timing
      const fetchTimer = logger.time('Network Request - fetch()');
      const response = await fetch('http://127.0.0.1:8000/execute-full-scale', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ strategy }),
      });
      const fetchDuration = fetchTimer.end();
      
      logger.info('📡 Network request completed', { 
        status: response.status, 
        statusText: response.statusText,
        duration: `${fetchDuration.toFixed(2)}ms`
      });

      if (response.ok) {
        // Log response parsing
        const parseTimer = logger.time('Response Parsing - JSON');
        const data = await response.json();
        const parseDuration = parseTimer.end();
        
        logger.success('✅ API call successful', {
          responseSize: JSON.stringify(data).length,
          parseDuration: `${parseDuration.toFixed(2)}ms`,
          hasResults: !!data.results,
          hasAggregatedMetrics: !!data.results?.aggregated_metrics,
          totalSymbols: data.results?.aggregated_metrics?.total_symbols_processed || 0
        });
        
        const totalDuration = timer.end();
        logger.success('🎉 Strategy execution completed', {
          totalDuration: `${totalDuration.toFixed(2)}ms`,
          networkTime: `${fetchDuration.toFixed(2)}ms`,
          parseTime: `${parseDuration.toFixed(2)}ms`
        });
        
        return { ok: true, ...data };
      } else {
        const errorText = await response.text();
        logger.error('❌ API call failed', {
          status: response.status,
          statusText: response.statusText,
          errorText: errorText.substring(0, 200)
        });
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      const totalDuration = timer.end();
      logger.error('💥 Strategy execution failed', {
        error: error.message,
        totalDuration: `${totalDuration.toFixed(2)}ms`,
        stack: error.stack?.substring(0, 500)
      });
      
      // Fallback: Return a message indicating the backend is not available
      return {
        ok: false,
        error: `Backend not available: ${error.message}. Please ensure the backend is running on port 8000.`
      };
    }
  }

  static async executeStrategyMultiLookahead(strategy, lookaheadPeriods) {
    const timer = logger.time('API Call - executeStrategyMultiLookahead');
    
    try {
      logger.info('🚀 Starting multi-lookahead strategy execution', { 
        strategy: strategy.substring(0, 100) + '...',
        lookaheadPeriods: lookaheadPeriods
      });
      
      const response = await fetch('http://127.0.0.1:8000/execute-multi-lookahead', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          strategy,
          lookahead_periods: lookaheadPeriods
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        const totalDuration = timer.end();
        logger.success('🎉 Multi-lookahead strategy execution completed', {
          totalDuration: `${totalDuration.toFixed(2)}ms`
        });
        // Ensure consistent shape: include ok flag
        return { ok: true, ...data };
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      const totalDuration = timer.end();
      logger.error('💥 Multi-lookahead strategy execution failed', {
        error: error.message,
        totalDuration: `${totalDuration.toFixed(2)}ms`
      });
      return {
        ok: false,
        error: `Backend not available: ${error.message}`
      };
    }
  }
}

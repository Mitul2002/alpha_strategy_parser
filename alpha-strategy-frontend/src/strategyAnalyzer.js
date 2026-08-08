/**
 * Strategy Analyzer for Frontend
 * Detects indicators in trading strategy strings
 */

class StrategyAnalyzer {
  constructor() {
    // Define indicator patterns
    this.indicatorPatterns = {
      'rsi': /\brsi\s*\(/i,
      'ema': /\bema\s*\(/i,
      'sma': /\bsma\s*\(/i,
      'wma': /\bwma\s*\(/i,
      'macd': /\bmacd\s*\(/i,
      'stoch': /\bstoch\s*\(/i,
      'stochrsi': /\bstochrsi\s*\(/i,
      'adx': /\badx\s*\(/i,
      'atr': /\batr\s*\(/i,
      'mfi': /\bmfi\s*\(/i,
      'obv': /\bobv\s*\(/i,
      'willr': /\bwillr\s*\(/i,
      'ultosc': /\bultosc\s*\(/i,
      'cmo': /\bcmo\s*\(/i,
      'stddev': /\bstddev\s*\(/i,
      'natr': /\bnatr\s*\(/i,
      'plus_di': /\bplus_di\s*\(/i,
      'minus_di': /\bminus_di\s*\(/i,
      'plus_dm': /\bplus_dm\s*\(/i,
      'minus_dm': /\bminus_dm\s*\(/i,
      'dx': /\bdx\s*\(/i,
      'cci': /\bcci\s*\(/i,
      'roc': /\broc\s*\(/i,
      'ppo': /\bppo\s*\(/i,
      'mom': /\bmom\s*\(/i,
      'linearreg': /\blinearreg\s*\(/i,
      'sar': /\bsar\s*\(/i,
      'trange': /\btrange\s*\(/i,
      'var': /\bvar\s*\(/i,
      'count': /\bcount\s*\(/i,
      'countstreak': /\bcountstreak\s*\(/i,
      'max': /\bmax\s*\(/i,
      'min': /\bmin\s*\(/i,
      'abs': /\babs\s*\(/i,
      'square': /\bsquare\s*\(/i,
      'round': /\bround\s*\(/i,
      'ceil': /\bceil\s*\(/i,
      'n_days_ago': /\bn_days_ago\s*\(/i,
      'n_weeks_ago': /\bn_weeks_ago\s*\(/i,
      'n_months_ago': /\bn_months_ago\s*\(/i,
      'n_years_ago': /\bn_years_ago\s*\(/i,
      'tf': /\btf\s*\(/i,
      'crossover': /\bcrossover\b/i,
      'cum': /\bcum\s*\(/i,
      'cumulative': /\bcumulative\s*\(/i,
      'bb_upper': /\bbb_upper\s*\(/i,
      'bb_lower': /\bbb_lower\s*\(/i,
      'bb_middle': /\bbb_middle\s*\(/i,
      'bbands': /\bbbands\s*\(/i,
      'macd_signal': /\bmacd_signal\s*\(/i,
      'macd_hist': /\bmacd_hist\s*\(/i,
      'stoch_k': /\bstoch_k\s*\(/i,
      'stoch_d': /\bstoch_d\s*\(/i,
      'stochrsi_k': /\bstochrsi_k\s*\(/i,
      'stochrsi_d': /\bstochrsi_d\s*\(/i
    };
  }

  /**
   * Analyze a strategy string and return detected indicators
   * @param {string} strategy - The strategy string to analyze
   * @returns {Object} Object with indicator flags
   */
  analyzeStrategy(strategy) {
    if (!strategy || typeof strategy !== 'string') {
      return {
        rsi: false,
        ema: false,
        sma: false,
        wma: false,
        macd: false,
        stoch: false,
        stochrsi: false,
        adx: false,
        atr: false,
        mfi: false,
        obv: false,
        willr: false,
        ultosc: false,
        cmo: false,
        stddev: false,
        natr: false,
        plus_di: false,
        minus_di: false,
        plus_dm: false,
        minus_dm: false,
        dx: false,
        cci: false,
        roc: false,
        ppo: false,
        mom: false,
        linearreg: false,
        sar: false,
        trange: false,
        var: false,
        count: false,
        countstreak: false,
        max: false,
        min: false,
        abs: false,
        square: false,
        round: false,
        ceil: false,
        n_days_ago: false,
        n_weeks_ago: false,
        n_months_ago: false,
        n_years_ago: false,
        tf: false,
        crossover: false,
        cum: false,
        cumulative: false,
        bb_upper: false,
        bb_lower: false,
        bb_middle: false,
        bbands: false,
        macd_signal: false,
        macd_hist: false,
        stoch_k: false,
        stoch_d: false,
        stochrsi_k: false,
        stochrsi_d: false
      };
    }

    const result = {};
    for (const [indicator, pattern] of Object.entries(this.indicatorPatterns)) {
      result[indicator] = pattern.test(strategy);
    }
    return result;
  }

  /**
   * Get list of detected indicators
   * @param {string} strategy - The strategy string to analyze
   * @returns {Array} Array of detected indicator names
   */
  getDetectedIndicators(strategy) {
    const analysis = this.analyzeStrategy(strategy);
    return Object.keys(analysis).filter(indicator => analysis[indicator]);
  }

  /**
   * Get priority indicators (most commonly used)
   * @param {string} strategy - The strategy string to analyze
   * @returns {Object} Object with priority indicator flags
   */
  getPriorityIndicators(strategy) {
    const analysis = this.analyzeStrategy(strategy);
    return {
      rsi: analysis.rsi,
      ema: analysis.ema,
      sma: analysis.sma,
      macd: analysis.macd,
      atr: analysis.atr,
      adx: analysis.adx,
      mfi: analysis.mfi,
      stoch: analysis.stoch,
      stochrsi: analysis.stochrsi,
      bb_upper: analysis.bb_upper,
      bb_lower: analysis.bb_lower,
      bb_middle: analysis.bb_middle,
      obv: analysis.obv,
      willr: analysis.willr,
      ultosc: analysis.ultosc,
      stddev: analysis.stddev,
      natr: analysis.natr
    };
  }
}

// Export for use in Vue components
export default StrategyAnalyzer;

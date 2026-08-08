<template>
  <div class="syntax-highlighted-input relative">
    <!-- Syntax highlighted overlay -->
    <div 
      class="syntax-overlay absolute inset-0 pointer-events-none overflow-hidden rounded-lg"
      v-html="highlightedContent"
    ></div>
    
        <!-- Actual textarea (transparent background) -->
    <textarea 
      ref="textareaRef"
      :value="modelValue"
      @input="handleInput"
      @keydown="handleKeydown"
      @scroll="handleScroll"
      @focus="handleFocus"
      @blur="handleBlur"
      :placeholder="placeholder"
      :rows="rows"
      spellcheck="false"
      autocomplete="off"
      autocapitalize="off"
      autocorrect="off"
      data-gramm="false"
      data-enable-grammarly="false"
      translate="no"
      class="relative z-10 w-full bg-transparent border border-slate-600 rounded-lg px-4 py-3 text-transparent caret-white placeholder-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-none"
      :style="{ 
        fontFamily: 'ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace',
        lineHeight: '1.5',
        tabSize: '2'
      }"
    ></textarea>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import Prism from 'prismjs'
import Tribute from 'tributejs'

export default {
  name: 'SyntaxHighlightedInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    rows: {
      type: Number,
      default: 3
    }
  },
  emits: ['update:modelValue', 'keydown'],
  setup(props, { emit }) {
    const textareaRef = ref(null)
    let tribute = null

    // Enhanced function definitions with parameter hints
    const functionDefinitions = {
      // Single-field functions (only need close)
      'rsi': { params: ['close', 'period'], description: 'Relative Strength Index' },
      'sma': { params: ['close', 'period'], description: 'Simple Moving Average' },
      'ema': { params: ['close', 'period'], description: 'Exponential Moving Average' },
      'ma': { params: ['close', 'period'], description: 'Moving Average' },
      'wma': { params: ['close', 'period'], description: 'Weighted Moving Average' },
      'macd': { params: ['close', 'fastperiod', 'slowperiod', 'signalperiod'], description: 'MACD' },
      'macd_signal': { params: ['close', 'fastperiod', 'slowperiod', 'signalperiod'], description: 'MACD Signal' },
      'macd_hist': { params: ['close', 'fastperiod', 'slowperiod', 'signalperiod'], description: 'MACD Histogram' },
      'stochrsi': { params: ['close', 'period'], description: 'Stochastic RSI' },
      'stochrsi_k': { params: ['close', 'period'], description: 'Stochastic RSI %K' },
      'stochrsi_d': { params: ['close', 'period'], description: 'Stochastic RSI %D' },
      'cmo': { params: ['close', 'period'], description: 'Chande Momentum Oscillator' },
      'roc': { params: ['close', 'period'], description: 'Rate of Change' },
      'mom': { params: ['close', 'period'], description: 'Momentum' },
      'ppo': { params: ['close', 'fastperiod', 'slowperiod'], description: 'Percentage Price Oscillator' },
      'stddev': { params: ['close', 'period', 'nbdev'], description: 'Standard Deviation' },
      'var': { params: ['close', 'period', 'nbdev'], description: 'Variance' },
      'linearreg': { params: ['close', 'period'], description: 'Linear Regression' },
      'cum': { params: ['data'], description: 'Cumulative Sum' },
      'cumulative': { params: ['data'], description: 'Cumulative Sum (alias)' },
      
      // Bollinger Bands
      'bbands': { params: ['close', 'period', 'nbdevup', 'nbdevdn'], description: 'Bollinger Bands' },
      'bbands_upper': { params: ['close', 'period', 'nbdevup', 'nbdevdn'], description: 'Bollinger Bands Upper' },
      'bbands_lower': { params: ['close', 'period', 'nbdevup', 'nbdevdn'], description: 'Bollinger Bands Lower' },
      'bbands_middle': { params: ['close', 'period', 'nbdevup', 'nbdevdn'], description: 'Bollinger Bands Middle' },
      'bb_upper': { params: ['close', 'period', 'nbdev'], description: 'Bollinger Bands Upper (Simple)' },
      'bb_lower': { params: ['close', 'period', 'nbdev'], description: 'Bollinger Bands Lower (Simple)' },
      'bb_middle': { params: ['close', 'period', 'nbdev'], description: 'Bollinger Bands Middle (Simple)' },
      
      // Multi-field functions (require high, low, close, volume)
      'stoch': { params: ['high', 'low', 'close', 'fastk_period', 'slowk_period', 'slowd_period'], description: 'Stochastic Oscillator' },
      'stoch_k': { params: ['high', 'low', 'close', 'fastk_period', 'slowk_period', 'slowd_period'], description: 'Stochastic %K' },
      'stoch_d': { params: ['high', 'low', 'close', 'fastk_period', 'slowk_period', 'slowd_period'], description: 'Stochastic %D' },
      'adx': { params: ['high', 'low', 'close', 'period'], description: 'Average Directional Index' },
      'dx': { params: ['high', 'low', 'close', 'period'], description: 'Directional Movement Index' },
      'plus_di': { params: ['high', 'low', 'close', 'period'], description: 'Plus Directional Indicator' },
      'minus_di': { params: ['high', 'low', 'close', 'period'], description: 'Minus Directional Indicator' },
      'plus_dm': { params: ['high', 'low', 'period'], description: 'Plus Directional Movement' },
      'minus_dm': { params: ['high', 'low', 'period'], description: 'Minus Directional Movement' },
      'cci': { params: ['high', 'low', 'close', 'period'], description: 'Commodity Channel Index' },
      'mfi': { params: ['high', 'low', 'close', 'volume', 'period'], description: 'Money Flow Index' },
      'willr': { params: ['high', 'low', 'close', 'period'], description: 'Williams %R' },
      'sar': { params: ['high', 'low', 'close', 'acceleration', 'maximum'], description: 'Parabolic SAR' },
      'atr': { params: ['high', 'low', 'close', 'period'], description: 'Average True Range' },
      'natr': { params: ['high', 'low', 'close', 'period'], description: 'Normalized ATR' },
      'trange': { params: ['high', 'low', 'close'], description: 'True Range' },
      'obv': { params: ['close', 'volume'], description: 'On-Balance Volume' },
      'ultosc': { params: ['high', 'low', 'close', 'period1', 'period2', 'period3'], description: 'Ultimate Oscillator' },
      
      // Aggregation functions
      'min': { params: ['data', 'period'], description: 'Minimum over period' },
      'max': { params: ['data', 'period'], description: 'Maximum over period' },
      'count': { params: ['data', 'period'], description: 'Count non-zero values' },
      'countstreak': { params: ['data', 'period'], description: 'Count consecutive streaks' },
      'abs': { params: ['data'], description: 'Absolute values' },
      'ceil': { params: ['data'], description: 'Ceiling function' },
      'floor': { params: ['data'], description: 'Floor function' },
      'round': { params: ['data'], description: 'Round to nearest integer' },
      'square': { params: ['data'], description: 'Square of values' },
      
      // Historical access functions
      'n_days_ago': { params: ['data', 'n'], description: 'Value n days ago' },
      'n_weeks_ago': { params: ['data', 'n'], description: 'Value n weeks ago' },
      'n_months_ago': { params: ['data', 'n'], description: 'Value n months ago' },
      'n_years_ago': { params: ['data', 'n'], description: 'Value n years ago' },
      
      // Special functions
      'tf': { params: ['condition', 'timeframe'], description: 'Multi-timeframe condition' },
      'crossover': { params: ['series1', 'series2'], description: 'Crossover detection' }
    }

    // Suggestion datasets
    const suggestions = {
      functions: Object.keys(functionDefinitions),
      params: ['close', 'open', 'high', 'low', 'volume'],
      operators: ['AND', 'OR', 'crossover', '>', '<', '>=', '<=', '==', '!=', '+', '-', '*', '/'],
      timeframes: ['daily', 'weekly', 'monthly', 'yearly', 'd', 'w', 'm', 'y']
    }

    // Build a flat list for Tribute with enhanced information
    const makeItem = (key, value, type, description = '', params = []) => ({ 
      key, 
      value, 
      type, 
      description, 
      params 
    })
    
    const tributeValues = [
      ...suggestions.functions.map(func => {
        const def = functionDefinitions[func]
        return makeItem(
          func, 
          func + '(' + def.params.join(', ') + ')', 
          'function',
          def.description,
          def.params
        )
      }),
      ...suggestions.params.map(s => makeItem(s, s, 'param')),
      ...suggestions.operators.map(s => makeItem(s, s, 'operator')),
      ...suggestions.timeframes.map(s => makeItem(s, `'${s}'`, 'timeframe'))
    ]

    const iconForType = (type) => {
      if (type === 'function') return 'ƒ'
      if (type === 'param') return '𝑥'
      if (type === 'operator') return '⊕'
      if (type === 'timeframe') return '🕒'
      return '·'
    }

    const initTribute = () => {
      if (tribute) return

      const valuesProvider = (text, cb) => {
        const cursorPos = textareaRef.value.selectionStart
        const before = text.substring(0, cursorPos)
        const after = text.substring(cursorPos)
        
        // Find the last word being typed
        const words = before.split(/\s+/)
        const lastWord = words[words.length - 1] || ''
        
        // Context analysis
        const prevToken = words[words.length - 2] || ''
        const isInParens = (before.match(/\(/g) || []).length > (before.match(/\)/g) || []).length
        
        const allow = new Set()
        
        if (isInParens) {
          // Inside parentheses - suggest parameters
          allow.add('param')
          // Operators like + - * / also sensible but handled by typing
        } else {
          // Outside parentheses
          if (prevToken === ')' || suggestions.functions.includes(prevToken)) {
            // After a function call closes or a value -> comparison or logical or crossover
            allow.add('operator')
          } else if (prevToken === 'and' || prevToken === 'or' || before.trim().length === 0) {
            // New clause -> suggest functions first
            allow.add('function')
            allow.add('param')
          } else {
            // Default bias to functions
            allow.add('function')
            allow.add('param')
            allow.add('operator')
            allow.add('timeframe')
          }
        }

        // Filter and rank
        const pool = tributeValues.filter(it => allow.has(it.type))
        const q = lastWord
        const ranked = pool
          .filter(it => q ? it.key.toLowerCase().includes(q) : true)
          .sort((a,b) => {
            const ap = a.key.toLowerCase().startsWith(q) ? 0 : 1
            const bp = b.key.toLowerCase().startsWith(q) ? 0 : 1
            if (ap !== bp) return ap - bp
            // Type priority: function > param > operator > timeframe
            const tp = t => ({function:0,param:1,operator:2,timeframe:3}[t] ?? 9)
            return tp(a.type) - tp(b.type) || a.key.localeCompare(b.key)
          })
          .slice(0, 50)

        cb(ranked)
      }

      tribute = new Tribute({
        trigger: '',
        values: valuesProvider,
        lookup: 'key',
        fillAttr: 'value',
        menuItemTemplate: item => {
          const t = item.original.type
          const icon = iconForType(t)
          const label = t === 'param' ? 'param' : t
          const description = item.original.description || ''
          const params = item.original.params || []
          
          let paramHint = ''
          if (params.length > 0) {
            paramHint = `<div class="as-params">${params.join(', ')}</div>`
          }
          
          return `<div class="as-menu-item">
            <span class="as-icon">${icon}</span>
            <span class="as-key">${item.original.key}</span>
            <span class="as-type">${label}</span>
            ${description ? `<div class="as-description">${description}</div>` : ''}
            ${paramHint}
          </div>`
        },
        noMatchTemplate: () => '',
        autocompleteMode: true
      })
      tribute.attach(textareaRef.value)
    }

    // Define custom trading strategy language
    const defineTradingLanguage = () => {
      Prism.languages.trading = {
        'function': {
          pattern: new RegExp(`\\b(?:${Object.keys(functionDefinitions).join('|')})\\b`, 'i'),
          alias: 'function'
        },
        'parameter': {
          pattern: /\b(?:close|high|low|volume|open)\b/i,
          alias: 'variable'
        },
        'operator': {
          pattern: /\b(?:AND|OR|XOR|crossover)\b/i,
          alias: 'operator'
        },
        'comparison': {
          pattern: /[><=!]=?/,
          alias: 'operator'
        },
        'number': {
          pattern: /\b\d+(?:\.\d+)?\b/,
          alias: 'number'
        },
        'timeframe': {
          pattern: /\b(?:daily|weekly|monthly|yearly|d|w|m|y)\b/i,
          alias: 'string'
        },
        'keyword': {
          pattern: /\b(?:crossover|tf)\b/i,
          alias: 'keyword'
        },
        'parenthesis': {
          pattern: /[()]/,
          alias: 'punctuation'
        },
        'comma': {
          pattern: /,/,
          alias: 'punctuation'
        }
      }
    }

    // Highlight the content
    const highlightedContent = computed(() => {
      if (!props.modelValue) return ''
      
      try {
        defineTradingLanguage()
        const highlighted = Prism.highlight(props.modelValue, Prism.languages.trading, 'trading')
        return highlighted
      } catch (error) {
        console.warn('Syntax highlighting error:', error)
        return props.modelValue
      }
    })

    const handleInput = (event) => {
      emit('update:modelValue', event.target.value)
    }

    const handleKeydown = (event) => {
      emit('keydown', event)
    }

    const handleScroll = (event) => {
      // Sync scroll between textarea and overlay
      const overlay = textareaRef.value.parentElement.querySelector('.syntax-overlay')
      if (overlay) {
        overlay.scrollTop = event.target.scrollTop
        overlay.scrollLeft = event.target.scrollLeft
      }
    }

    const handleFocus = () => {
      // Initialize autocomplete on focus
      nextTick(() => {
        initTribute()
      })
    }

    const handleBlur = () => {
      // Keep tribute attached for better UX
    }

    onMounted(() => {
      defineTradingLanguage()
      nextTick(() => {
        initTribute()
      })
    })

    onBeforeUnmount(() => {
      if (tribute) {
        tribute.detach(textareaRef.value)
      }
    })

    return {
      textareaRef,
      highlightedContent,
      handleInput,
      handleKeydown,
      handleScroll,
      handleFocus,
      handleBlur
    }
  }
}
</script>

<style scoped>
.syntax-highlighted-input {
  position: relative;
}

.syntax-overlay {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
  font-size: 14px;
  line-height: 1.5;
  padding: 12px;
  color: #e5e7eb;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 8px;
  pointer-events: none;
  z-index: 1;
}

/* Enhanced autocomplete styling */
:deep(.tribute-container) {
  background: #0b1220;
  border: 1px solid #233046;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

:deep(.tribute-container ul) {
  list-style: none;
  margin: 0;
  padding: 0;
}

:deep(.tribute-container li) {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #1f2937;
}

:deep(.tribute-container li:last-child) {
  border-bottom: none;
}

:deep(.tribute-container li.highlight) {
  background: #1f2937;
}

.as-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.as-icon {
  font-weight: bold;
  color: #61dafb;
  min-width: 16px;
}

.as-key {
  font-weight: 600;
  color: #e5e7eb;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
}

.as-type {
  font-size: 11px;
  color: #9ca3af;
  background: #374151;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.as-description {
  font-size: 12px;
  color: #9ca3af;
  font-style: italic;
  width: 100%;
  margin-top: 2px;
}

.as-params {
  font-size: 11px;
  color: #fbbf24;
  background: #451a03;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
  width: 100%;
  margin-top: 2px;
}

/* Syntax highlighting colors */
:deep(.token.function) {
  color: #61dafb;
}

:deep(.token.parameter) {
  color: #98c379;
}

:deep(.token.operator) {
  color: #f97583;
}

:deep(.token.number) {
  color: #faa356;
}

:deep(.token.timeframe) {
  color: #c678dd;
}

:deep(.token.keyword) {
  color: #ff6b6b;
}

:deep(.token.punctuation) {
  color: #e5e7eb;
}
</style>

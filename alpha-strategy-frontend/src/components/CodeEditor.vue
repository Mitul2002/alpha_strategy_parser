<template>
  <div ref="editorRoot" class="cm-wrapper"></div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, drawSelection, Decoration, ViewPlugin } from '@codemirror/view'
import { autocompletion, closeBrackets, closeBracketsKeymap, completionKeymap } from '@codemirror/autocomplete'

export default {
  name: 'CodeEditor',
  props: {
    modelValue: { type: String, default: '' }
  },
  emits: ['update:modelValue', 'ctrlEnter'],
  setup(props, { emit }) {
    const editorRoot = ref(null)
    let view = null

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

    const functions = Object.keys(functionDefinitions)
    const params = ['close','open','high','low','volume']
    const operators = ['AND','OR','crossover','>','<','>=','<=','==','!=','+','-','*','/']
    const timeframes = ['daily','weekly','monthly','yearly','d','w','m','y']

    const highlightPlugin = ViewPlugin.fromClass(class {
      constructor(view) { this.decorations = this.buildDecorations(view) }
      update(update) { if (update.docChanged || update.viewportChanged) this.decorations = this.buildDecorations(update.view) }
      buildDecorations(view) {
        const builder = []
        const text = view.state.doc.toString()
        const add = (re, cls) => { let m; while ((m = re.exec(text))) builder.push(Decoration.mark({ class: cls }).range(m.index, m.index + m[0].length)) }
        add(new RegExp(`\\b(${functions.join('|')})\\b`, 'gi'), 'tok-function')
        add(/\b(close|open|high|low|volume)\b/gi, 'tok-param')
        add(/\b(AND|OR|crossover|tf)\b/gi, 'tok-operator')
        add(/(>=|<=|==|!=|>|<)/g, 'tok-operator')
        add(/\b\d+(?:\.\d+)?\b/g, 'tok-number')
        add(/\b(daily|weekly|monthly|yearly|d|w|m|y)\b/gi, 'tok-timeframe')
        return Decoration.set(builder, true)
      }
    }, { decorations: v => v.decorations })

    function contextSource(context) {
      const before = context.state.sliceDoc(0, context.pos)
      const lower = before.toLowerCase()
      const lastOpen = lower.lastIndexOf('(')
      const lastClose = lower.lastIndexOf(')')
      const inParens = lastOpen > lastClose
      const afterTfOpen = lower.lastIndexOf('tf(') === lastOpen
      let commaSinceOpen = -1
      if (inParens) { const seg = lower.slice(lastOpen + 1); commaSinceOpen = (seg.match(/,/g) || []).length }
      const lastWord = ((before.match(/[a-z_]+$/i) || [''])[0]).toLowerCase()
      const prevToken = ((before.replace(/\s+/g,' ').trim().match(/([a-z_]+|\)|,|>=|<=|==|!=|>|<|and|or|crossover)$/i) || [''])[1] || '').toLowerCase()

      const options = []
      const pushAll = (arr, type) => {
        // Map to CM6 known icon categories
        const iconType = type === 'function' ? 'function' : type === 'param' ? 'variable' : type === 'operator' ? 'keyword' : /* timeframe */ 'constant'
        arr.forEach(k => {
          const def = functionDefinitions[k]
          const label = def ? `${k}(${def.params.join(', ')})` : k
          const detail = def ? def.description : ''
          const info = def ? `Parameters: ${def.params.join(', ')}` : ''
          
          options.push({ 
            label: k, 
            type: iconType, 
            apply: type==='function' ? k + '(' : (type==='timeframe' ? `'${k}'` : k),
            detail: detail,
            info: info
          })
        })
      }
      
      if (afterTfOpen && inParens && commaSinceOpen >= 1) pushAll(timeframes, 'timeframe')
      else if (inParens) pushAll(params, 'param')
      else {
        if (prevToken === ')' || functions.includes(prevToken)) pushAll(['AND','OR','crossover','>','<','>=','<=','==','!='], 'operator')
        else if (prevToken === 'and' || prevToken === 'or' || before.trim().length === 0) { pushAll(functions, 'function'); pushAll(params, 'param') }
        else { pushAll(functions, 'function'); pushAll(params, 'param'); pushAll(operators, 'operator'); pushAll(timeframes, 'timeframe') }
      }
      
      const filtered = options.filter(o => lastWord ? o.label.toLowerCase().includes(lastWord) : true)
        .sort((a,b) => { 
          const ap = a.label.toLowerCase().startsWith(lastWord)?0:1; 
          const bp = b.label.toLowerCase().startsWith(lastWord)?0:1; 
          const tp=t=>({function:0,param:1,operator:2,timeframe:3}[t]??9); 
          return ap-bp||tp(a.type)-tp(b.type)||a.label.localeCompare(b.label) 
        }).slice(0,50)
      
      return { from: context.pos - (lastWord ? lastWord.length : 0), options: filtered }
    }

    onMounted(() => {
      const ctrlEnterKeymap = keymap.of([{ key: 'Ctrl-Enter', run: () => { emit('ctrlEnter'); return true } }])

      view = new EditorView({
        state: EditorState.create({
          doc: props.modelValue,
          extensions: [
            ctrlEnterKeymap,
            keymap.of([...closeBracketsKeymap, ...completionKeymap]),
            drawSelection(),
            closeBrackets(),
            autocompletion({ 
              override: [contextSource], 
              icons: true,
              activateOnTyping: true,
              closeOnBlur: false
            }),
            highlightPlugin,
            EditorView.theme({
              '&': { backgroundColor: '#111827', color: '#e5e7eb', border: '1px solid #374151', borderRadius: '8px' },
              '.cm-content': { fontFamily: 'ui-monospace, SFMono-Regular, Consolas, Menlo, monospace', fontSize: '14px', minHeight: '96px', padding: '12px' },
              '.cm-tooltip': { backgroundColor: '#0b1220', border: '1px solid #233046', borderRadius: '8px' },
              '.cm-tooltip-autocomplete > ul > li[aria-selected]': { backgroundColor: '#1f2937' },
              '.cm-tooltip-autocomplete > ul > li': { padding: '8px 12px', borderBottom: '1px solid #1f2937' },
              '.cm-tooltip-autocomplete > ul > li:last-child': { borderBottom: 'none' },
              '.tok-function': { color: '#61dafb' }, 
              '.tok-param': { color: '#98c379' }, 
              '.tok-operator': { color: '#f97583' }, 
              '.tok-number': { color: '#faa356' }, 
              '.tok-timeframe': { color: '#c678dd' }
            }),
            EditorView.updateListener.of(u => { if (u.docChanged) emit('update:modelValue', u.state.doc.toString()) })
          ]
        }),
        parent: editorRoot.value
      })
    })

    onBeforeUnmount(() => { if (view) view.destroy() })

    watch(() => props.modelValue, (nv) => {
      if (!view) return
      const cur = view.state.doc.toString()
      if (nv !== cur) view.dispatch({ changes: { from: 0, to: cur.length, insert: nv } })
    })

    return { editorRoot }
  }
}
</script>

<style scoped>
.cm-wrapper { width: 100%; }

/* Enhanced autocomplete styling */
:deep(.cm-tooltip-autocomplete) {
  background: #0b1220;
  border: 1px solid #233046;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  max-height: 300px;
  overflow-y: auto;
}

:deep(.cm-tooltip-autocomplete ul) {
  list-style: none;
  margin: 0;
  padding: 0;
}

:deep(.cm-tooltip-autocomplete li) {
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.cm-tooltip-autocomplete li:last-child) {
  border-bottom: none;
}

:deep(.cm-tooltip-autocomplete li[aria-selected]) {
  background: #1f2937;
}

:deep(.cm-completionIcon) {
  font-weight: bold;
  color: #61dafb;
  min-width: 16px;
}

:deep(.cm-completionLabel) {
  font-weight: 600;
  color: #e5e7eb;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
}

:deep(.cm-completionDetail) {
  font-size: 12px;
  color: #9ca3af;
  font-style: italic;
  margin-left: auto;
}

:deep(.cm-completionInfo) {
  font-size: 11px;
  color: #fbbf24;
  background: #451a03;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Consolas, Liberation Mono, Menlo, monospace;
}
</style>

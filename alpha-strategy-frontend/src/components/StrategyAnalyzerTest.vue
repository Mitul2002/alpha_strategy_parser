<template>
  <div class="p-6 bg-white rounded-lg shadow-lg">
    <h2 class="text-2xl font-bold mb-4">Strategy Analyzer Test</h2>
    
    <!-- Test Input -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Test Strategy:
      </label>
      <textarea
        v-model="testStrategy"
        class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        rows="3"
        placeholder="Enter a strategy to test..."
      ></textarea>
    </div>

    <!-- Test Buttons -->
    <div class="mb-6 space-x-2">
      <button
        @click="testExample1"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Test Example 1
      </button>
      <button
        @click="testExample2"
        class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
      >
        Test Example 2
      </button>
      <button
        @click="testRandomStrategy"
        class="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
      >
        Test Random Strategy
      </button>
    </div>

    <!-- Results -->
    <div v-if="analysisResult" class="space-y-4">
      <!-- Detected Indicators -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">Detected Indicators:</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="indicator in detectedIndicators"
            :key="indicator"
            class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
          >
            {{ indicator.toUpperCase() }}
          </span>
          <span v-if="detectedIndicators.length === 0" class="text-gray-500">
            No indicators detected
          </span>
        </div>
      </div>

      <!-- Priority Indicators -->
      <div class="bg-yellow-50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">Priority Indicators:</h3>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(value, indicator) in priorityIndicators"
            :key="indicator"
            v-if="value"
            class="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm"
          >
            {{ indicator.toUpperCase() }}
          </span>
          <span v-if="Object.values(priorityIndicators).every(v => !v)" class="text-gray-500">
            No priority indicators detected
          </span>
        </div>
      </div>

      <!-- Full Analysis -->
      <div class="bg-gray-50 p-4 rounded-lg">
        <h3 class="text-lg font-semibold mb-2">Full Analysis:</h3>
        <pre class="text-sm bg-white p-3 rounded border overflow-auto">{{ JSON.stringify(analysisResult, null, 2) }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import StrategyAnalyzer from '../strategyAnalyzer.js'

export default {
  name: 'StrategyAnalyzerTest',
  data() {
    return {
      testStrategy: '',
      analyzer: new StrategyAnalyzer(),
      analysisResult: null,
      detectedIndicators: [],
      priorityIndicators: {}
    }
  },
  methods: {
    analyzeStrategy() {
      if (!this.testStrategy.trim()) {
        this.analysisResult = null
        this.detectedIndicators = []
        this.priorityIndicators = {}
        return
      }

      this.analysisResult = this.analyzer.analyzeStrategy(this.testStrategy)
      this.detectedIndicators = this.analyzer.getDetectedIndicators(this.testStrategy)
      this.priorityIndicators = this.analyzer.getPriorityIndicators(this.testStrategy)
    },
    testExample1() {
      this.testStrategy = "roc(close, 6) < -2 AND stddev(close, 10) > sma(stddev(close, 10), 5) AND obv(close, volume) < sma(obv(close, volume), 20)"
      this.analyzeStrategy()
    },
    testExample2() {
      this.testStrategy = "ema(close, 34) > ema(close, 55) AND countstreak(macd(close, 12, 26, 9) > 0, 5) >= 3 AND rsi(close, 14) > 58"
      this.analyzeStrategy()
    },
    testRandomStrategy() {
      const strategies = [
        "rsi(close, 14) < 30 AND bb_lower(close, 20, 2) > close",
        "ema(close, 21) crossover ema(close, 55) AND adx(high, low, close, 14) > 25",
        "macd(close, 12, 26, 9) > 0 AND stoch(high, low, close, 14) > 80",
        "atr(high, low, close, 14) > sma(atr(high, low, close, 14), 20) AND mfi(high, low, close, volume, 14) > 70",
        "sma(close, 50) > sma(close, 200) AND willr(high, low, close, 14) < -50"
      ]
      const randomStrategy = strategies[Math.floor(Math.random() * strategies.length)]
      this.testStrategy = randomStrategy
      this.analyzeStrategy()
    }
  },
  watch: {
    testStrategy() {
      this.analyzeStrategy()
    }
  }
}
</script>

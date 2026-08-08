<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
    <!-- Professional Header -->
    <header class="bg-slate-800 border-b border-slate-700 shadow-lg">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-white">Alpha Strategy Parser</h1>
              <p class="text-slate-400 text-sm">Full-Scale Trading Strategy Analysis Platform</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="text-right">
              <div class="text-sm text-slate-400">Status</div>
              <div class="text-green-400 text-sm font-medium">● Live</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 px-6 py-6">
      <div class="max-w-7xl mx-auto">
        
        <!-- No Results State -->
        <div v-if="!results" class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl p-12 text-center">
          <div class="w-24 h-24 mx-auto mb-6 bg-slate-700 rounded-full flex items-center justify-center">
            <svg class="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-semibold text-white mb-2">Ready to Analyze</h3>
          <p class="text-slate-400">Enter a trading strategy below to see comprehensive analysis across all 2,050+ stocks</p>
        </div>
        
        <!-- Results Display -->
        <div v-else class="space-y-6">
          
          <!-- Strategy Query Display -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <h3 class="text-lg font-semibold text-white">Executed Strategy</h3>
            </div>
            <div class="p-6">
              <div class="bg-slate-900 rounded-lg p-4 border border-slate-600">
                <code class="text-green-400 font-mono text-sm">{{ results.strategy }}</code>
              </div>
            </div>
          </div>
            
          <!-- Aggregated Summary Statistics -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-white">Aggregated Summary Statistics</h3>
              </div>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <!-- Avg Return -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.avg_return * 100).toFixed(2) }}%</div>
                  <div class="text-slate-300 text-xs">Avg Return (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Avg Sharpe -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ aggregatedMetrics.sharpe_ratio.toFixed(2) }}</div>
                  <div class="text-slate-300 text-xs">Avg Sharpe (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Max Runup -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.max_runup * 100).toFixed(2) }}%</div>
                  <div class="text-slate-300 text-xs">Max Runup (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Total Signals -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ aggregatedMetrics.total_signals.toLocaleString() }}</div>
                  <div class="text-slate-300 text-xs">Total Signals</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Avg Win Rate -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.win_rate * 100).toFixed(1) }}%</div>
                  <div class="text-slate-300 text-xs">Avg Win Rate (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Avg Information Ratio -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ aggregatedMetrics.information_ratio.toFixed(2) }}</div>
                  <div class="text-slate-300 text-xs">Avg Information Ratio (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Avg Signals/Day -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ avgSignalsPerDay.toFixed(1) }}</div>
                  <div class="text-slate-300 text-xs">Avg Signals/Day (All Periods)</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                
                <!-- Stocks Analyzed -->
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ results.performance_stats?.total_symbols?.toLocaleString() || '0' }}</div>
                  <div class="text-slate-300 text-xs">Stocks Analyzed</div>
                  <svg class="w-4 h-4 text-slate-400 mx-auto mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Performance Summary by Forward Lookahead Period -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                <h3 class="text-lg font-semibold text-white">Performance Summary (All Forward Lookaheads)</h3>
              </div>
            </div>
            <div class="p-6">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-slate-600">
                      <th class="text-left py-3 px-4 font-semibold text-slate-300">Period</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Return (%)</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Win Rate (%)</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Total Signals</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Sharpe</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Sortino</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Std Dev</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(metrics, period) in forwardPeriodMetrics" :key="period" class="border-b border-slate-700/50">
                      <td class="py-3 px-4 font-medium text-white">{{ period }}d</td>
                      <td class="py-3 px-4 text-right text-white">{{ (metrics.avg_return * 100).toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ (metrics.win_rate * 100).toFixed(2) }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ metrics.total_signals.toLocaleString() }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ metrics.sharpe_ratio.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ metrics.sortino_ratio.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ (metrics.avg_std_dev * 100).toFixed(4) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <!-- Detailed Results Table -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  <h3 class="text-lg font-semibold text-white">Detailed Results</h3>
                </div>
                <div class="text-sm text-slate-400">
                  Showing {{ stockwiseData.length }} stocks
                </div>
              </div>
            </div>
            <div class="p-6">
              <div class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-slate-600">
                      <th class="text-left py-3 px-4 font-semibold text-slate-300">Symbol</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Total Signals</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Total Return</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Return</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Win Rate</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Sharpe Ratio</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Sortino Ratio</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Information Ratio</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Max Runup</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Max Drawdown</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Best Return</th>
                      <th class="text-right py-3 px-4 font-semibold text-slate-300">Worst Return</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(stock, index) in stockwiseData" :key="stock.Symbol" class="border-b border-slate-700/50 hover:bg-slate-700/30">
                      <td class="py-3 px-4 font-medium text-white">{{ stock.Symbol }}</td>
                      <td class="py-3 px-4 text-right text-white">{{ stock.Total_Signals.toLocaleString() }}</td>
                      <td class="py-3 px-4 text-right" :class="stock.Total_Return >= 0 ? 'text-green-400' : 'text-red-400'">{{ stock.Total_Return.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right" :class="stock.Avg_Return >= 0 ? 'text-green-400' : 'text-red-400'">{{ (stock.Avg_Return * 100).toFixed(4) }}%</td>
                      <td class="py-3 px-4 text-right text-white">{{ (stock.Win_Rate * 100).toFixed(2) }}%</td>
                      <td class="py-3 px-4 text-right" :class="stock.Sharpe_Ratio >= 0 ? 'text-green-400' : 'text-red-400'">{{ stock.Sharpe_Ratio.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right" :class="stock.Sortino_Ratio >= 0 ? 'text-green-400' : 'text-red-400'">{{ stock.Sortino_Ratio.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right" :class="stock.Information_Ratio >= 0 ? 'text-green-400' : 'text-red-400'">{{ stock.Information_Ratio.toFixed(4) }}</td>
                      <td class="py-3 px-4 text-right text-green-400">{{ (stock.Max_Runup * 100).toFixed(2) }}%</td>
                      <td class="py-3 px-4 text-right text-red-400">{{ (stock.Max_Drawdown * 100).toFixed(2) }}%</td>
                      <td class="py-3 px-4 text-right text-green-400">{{ (stock.Best_Return * 100).toFixed(2) }}%</td>
                      <td class="py-3 px-4 text-right text-red-400">{{ (stock.Worst_Return * 100).toFixed(2) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Bottom Input Bar -->
    <div class="bg-slate-800 border-t border-slate-700 shadow-lg">
      <div class="max-w-7xl mx-auto px-6 py-4">
        <div class="flex items-center space-x-4">
          <div class="flex-1">
            <CodeEditor
              v-model="strategyInput"
              placeholder="Enter your trading strategy (e.g., ema(close, 50) > ema(close, 200))"
              @ctrlEnter="executeStrategy"
              :disabled="isExecuting"
            />
          </div>
          <button
            @click="executeStrategy"
            :disabled="isExecuting || !strategyInput.trim()"
            class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-lg"
          >
            <svg v-if="isExecuting" class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            <span>{{ isExecuting ? 'Analyzing...' : 'Analyze Strategy' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import CodeEditor from './components/CodeEditor.vue'

export default {
  name: 'AppFullScale',
  components: {
    CodeEditor
  },
  setup() {
    const strategyInput = ref('')
    const results = ref(null)
    const isExecuting = ref(false)

    // Computed properties for aggregated metrics
    const aggregatedMetrics = computed(() => {
      if (!results.value?.aggregated_metrics?.overall) {
        return {
          avg_return: 0,
          sharpe_ratio: 0,
          max_runup: 0,
          total_signals: 0,
          win_rate: 0,
          information_ratio: 0,
          avg_std_dev: 0,
          max_drawdown: 0,
          best_return: 0,
          worst_return: 0,
          total_return: 0
        }
      }
      return results.value.aggregated_metrics.overall
    })

    // Computed property for forward period metrics
    const forwardPeriodMetrics = computed(() => {
      if (!results.value?.aggregated_metrics) return {}
      const metrics = { ...results.value.aggregated_metrics }
      delete metrics.overall
      return metrics
    })

    // Computed property for stockwise data
    const stockwiseData = computed(() => {
      if (!results.value?.stockwise_metrics) return []
      return results.value.stockwise_metrics.map(metric => ({
        Symbol: metric.symbol,
        Total_Signals: metric.total_signals,
        Total_Return: metric.total_return,
        Avg_Return: metric.avg_return,
        Win_Rate: metric.win_rate,
        Sharpe_Ratio: metric.sharpe_ratio,
        Sortino_Ratio: metric.sortino_ratio,
        Information_Ratio: metric.information_ratio,
        Max_Runup: metric.max_runup,
        Max_Drawdown: metric.max_drawdown,
        Best_Return: metric.best_return,
        Worst_Return: metric.worst_return
      }))
    })

    // Computed property for average signals per day
    const avgSignalsPerDay = computed(() => {
      if (!aggregatedMetrics.value.total_signals) return 0
      // Assuming 252 trading days per year and 10 years of data
      const totalDays = 252 * 10
      return aggregatedMetrics.value.total_signals / totalDays
    })

    const executeStrategy = async () => {
      if (!strategyInput.value.trim()) return
      
      isExecuting.value = true
      
      try {
        const response = await fetch('http://127.0.0.1:8000/execute-full-scale', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            strategy: strategyInput.value.trim()
          })
        })
        
        const data = await response.json()
        
        if (data.ok) {
          results.value = {
            ...data.results,
            strategy: strategyInput.value.trim()
          }
          // Scroll to top to show results
          window.scrollTo({ top: 0, behavior: 'smooth' })
        } else {
          console.error('Execution failed:', data.error)
          alert('Strategy execution failed: ' + (data.error || 'Unknown error'))
        }
      } catch (error) {
        console.error('API Error:', error)
        alert('API Error: ' + error.message)
      } finally {
        isExecuting.value = false
      }
    }

    return {
      strategyInput,
      results,
      isExecuting,
      aggregatedMetrics,
      forwardPeriodMetrics,
      stockwiseData,
      avgSignalsPerDay,
      executeStrategy
    }
  }
}
</script>

<style scoped>
/* Custom scrollbar for better UX */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #334155;
}

::-webkit-scrollbar-thumb {
  background: #64748B;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94A3B8;
}

/* Smooth transitions */
* {
  transition: all 0.2s ease-in-out;
}
</style>

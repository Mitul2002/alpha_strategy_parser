<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-4xl mx-auto px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-4">Create New Strategy</h1>
        <p class="text-slate-400">Analyze a trading strategy across all stocks with custom lookahead periods</p>
      </div>

      <!-- Results Display (now shown first) -->
      <div v-if="results" class="space-y-6 mb-10">
        <!-- Strategy Query Display -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
            <h3 class="text-lg font-semibold text-white">Executed Strategy</h3>
          </div>
          <div class="p-6">
            <div class="bg-slate-900 rounded-lg p-4 border border-slate-600">
              <code class="text-green-400 font-mono text-sm break-words">{{ results.aggregated_metrics.strategy }}</code>
            </div>
          </div>
        </div>
            
        <!-- Aggregated Summary Statistics -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
            <div class="flex items-center space-x-2">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
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
              </div>
              
              <!-- Avg Sharpe -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ aggregatedMetrics.avg_sharpe.toFixed(2) }}</div>
                <div class="text-slate-300 text-xs">Avg Sharpe (All Periods)</div>
              </div>
              
              <!-- Max Runup -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.max_runup * 100).toFixed(2) }}%</div>
                <div class="text-slate-300 text-xs">Max Runup (All Periods)</div>
              </div>
              
              <!-- Total Signals -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ formattedMetrics.total_signals }}</div>
                <div class="text-slate-300 text-xs">Total Signals</div>
              </div>
              
              <!-- Avg Win Rate -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.avg_win_rate * 100).toFixed(1) }}%</div>
                <div class="text-slate-300 text-xs">Avg Win Rate (All Periods)</div>
              </div>
              
              <!-- Avg Information Ratio -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ aggregatedMetrics.avg_information_ratio.toFixed(2) }}</div>
                <div class="text-slate-300 text-xs">Avg Information Ratio (All Periods)</div>
              </div>
              
              <!-- Avg Signals/Day -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.avg_signals_per_day || 0).toFixed(1) }}</div>
                <div class="text-slate-300 text-xs">Avg Signals/Day (All Periods)</div>
              </div>
              
              <!-- Stocks Analyzed -->
              <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                <div class="text-2xl font-bold text-white mb-1">{{ (aggregatedMetrics.total_symbols || 0).toLocaleString() }}</div>
                <div class="text-slate-300 text-xs">Stocks Analyzed</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Summary by Forward Lookahead Period -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
            <div class="flex items-center space-x-2">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
              <h3 class="text-lg font-semibold text-white">Performance Summary (All Forward Lookaheads)</h3>
            </div>
          </div>
          <div class="p-6">
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-slate-600">
                    <th class="text-left py-3 px-4 font-semibold text-slate-300">Period (Days)</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Return (%)</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Win Rate (%)</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Total Signals</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Sharpe</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Sortino</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Std Dev</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(periodData, period) in lookaheadResults" :key="period" class="border-b border-slate-700/50">
                    <td class="py-3 px-4 font-medium text-white">{{ period }} days</td>
                    <td class="py-3 px-4 text-right text-white">{{ ((periodData.avg_return || 0) * 100).toFixed(4) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ ((periodData.win_rate || 0) * 100).toFixed(2) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (periodData.total_signals || 0).toLocaleString() }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (periodData.avg_sharpe || 0).toFixed(4) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (periodData.avg_sortino || 0).toFixed(4) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ ((periodData.avg_std_dev || 0) * 100).toFixed(4) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Stockwise Results Table (first lookahead period) -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h11M9 21V3m12 7h-4m0 0V7m0 3v4"></path>
                </svg>
                <h3 class="text-lg font-semibold text-white">Stock Results ({{ selectedLookaheadPeriod }} days)</h3>
              </div>
              <div class="flex items-center space-x-4">
                <!-- Lookahead Period Selector -->
                <div class="flex items-center space-x-2 text-sm">
                  <label class="text-slate-300">Period:</label>
                  <select 
                    v-model="selectedLookaheadPeriod" 
                    class="bg-slate-700 border border-slate-600 text-white rounded px-2 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option 
                      v-for="period in availableLookaheadPeriods" 
                      :key="period" 
                      :value="period"
                    >
                      {{ period }} days
                    </option>
                  </select>
                </div>
                
                <input
                  v-model="stockSearch"
                  type="text"
                  placeholder="Search symbol..."
                  class="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
                <div class="flex items-center space-x-2 text-sm">
                  <label class="text-slate-300">Sort by</label>
                  <select v-model="sortBy" class="bg-slate-700 border border-slate-600 text-white rounded px-2 py-2">
                    <option value="total_signals">Signals</option>
                    <option value="avg_return">Avg Return</option>
                    <option value="win_rate">Win Rate</option>
                    <option value="sharpe_ratio">Sharpe</option>
                    <option value="sortino_ratio">Sortino</option>
                    <option value="information_ratio">Info Ratio</option>
                  </select>
                  <button @click="toggleSortDir" class="px-2 py-2 bg-slate-700 border border-slate-600 rounded text-white hover:bg-slate-600">
                    {{ sortDir === 'desc' ? '▼' : '▲' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <!-- Clustering Controls -->
          <div class="px-6 pt-6">
            <div v-if="results && selectedLookaheadPeriod" class="bg-slate-900/60 border border-slate-700 rounded-lg p-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m7-7v14" />
                  </svg>
                  <h4 class="text-sm font-semibold text-white">K-Means Clustering</h4>
                </div>
                <div class="flex items-center space-x-3 text-sm">
                  <label class="text-slate-300">Feature X</label>
                  <select v-model="clusterFeatureX" class="bg-slate-700 border border-slate-600 text-white rounded px-2 py-1">
                    <option v-for="f in clusterableFeatures" :key="f.key" :value="f.key">{{ f.label }}</option>
                  </select>
                  <label class="text-slate-300">Feature Y</label>
                  <select v-model="clusterFeatureY" class="bg-slate-700 border border-slate-600 text-white rounded px-2 py-1">
                    <option v-for="f in clusterableFeatures" :key="f.key" :value="f.key">{{ f.label }}</option>
                  </select>
                  <label class="text-slate-300">Clusters</label>
                  <input v-model.number="clusterK" type="number" min="2" max="12" class="w-20 bg-slate-700 border border-slate-600 text-white rounded px-2 py-1" />
                  <button @click="runClustering" :disabled="!canCluster" class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white rounded">Cluster</button>
                  <button v-if="clusterAssignments.size>0" @click="clearClustering" class="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded">Clear</button>
                </div>
              </div>
              <div v-if="clusterAssignments.size>0" class="mt-3 text-xs text-slate-300">Assigned {{ clusterAssignments.size }} symbols into {{ clusterSummary.k }} clusters using {{ clusterSummary.featureXLabel }} vs {{ clusterSummary.featureYLabel }}.</div>
            </div>
          </div>

          <div class="p-6">
            <!-- Scatter plot below clustering controls, above table -->
            <div v-if="clusterAssignments.size>0" class="mb-6">
              <PlotlyScatter
                :points="clusterPoints"
                :x-label="clusterSummary.featureXLabel || clusterFeatureX"
                :y-label="clusterSummary.featureYLabel || clusterFeatureY"
                :clusters="clusterSummary.k"
              />
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-slate-600">
                    <th class="text-left py-3 px-4 font-semibold text-slate-300">Symbol</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Signals</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Return (%)</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Win Rate (%)</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Sharpe</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Sortino</th>
                    <th v-if="clusterAssignments.size>0" class="text-right py-3 px-4 font-semibold text-slate-300">Cluster</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="row in paginatedStocks"
                    :key="row.symbol"
                    class="border-b border-slate-700/50 hover:bg-slate-700/40 cursor-pointer"
                    @click="selectStock(row)"
                  >
                    <td class="py-3 px-4 font-medium text-white">{{ row.symbol }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ row.total_signals.toLocaleString() }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (row.avg_return * 100).toFixed(2) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (row.win_rate * 100).toFixed(1) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (row.sharpe_ratio || 0).toFixed(2) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ (row.sortino_ratio || 0).toFixed(2) }}</td>
                    <td v-if="clusterAssignments.size>0" class="py-3 px-4 text-right text-white">{{ clusterAssignments.get(row.symbol) ?? '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="stockTable.length === 0" class="text-center text-slate-400 py-6">No stock results</div>

            <!-- Pagination Controls -->
            <div v-if="totalPages > 1" class="flex items-center justify-between mt-4 text-sm">
              <div class="text-slate-300">Page {{ currentPage }} of {{ totalPages }}</div>
              <div class="flex items-center space-x-2">
                <button
                  @click="goToPage(currentPage - 1)"
                  :disabled="currentPage === 1"
                  class="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white disabled:opacity-50"
                >Prev</button>
                <button
                  @click="goToPage(currentPage + 1)"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white disabled:opacity-50"
                >Next</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Chart for Selected Stock -->
        <div v-if="selectedStock" class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">Chart - {{ selectedStock.symbol }}</h3>
            <div class="text-sm text-slate-400">Indicators from strategy are auto-enabled</div>
          </div>
          <div class="p-0">
            <TradingChart :symbol="selectedStock.symbol" :indicators="indicatorFlags || indicatorFlagsRef" :lookahead-periods="parsedLookaheadPeriods" />
          </div>
        </div>

        <!-- Trades List for Selected Stock -->
        <div v-if="selectedStock" class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
          <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-white">Trades - {{ selectedStock.symbol }}</h3>
            <div class="text-sm text-slate-400">Showing entry date and price</div>
          </div>
          <div class="p-6">
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-slate-600">
                    <th class="text-left py-3 px-4 font-semibold text-slate-300">Entry Date</th>
                    <th class="text-right py-3 px-4 font-semibold text-slate-300">Entry Price</th>
                    <th v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).rsi" class="text-right py-3 px-4 font-semibold text-slate-300">RSI</th>
                    <th v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).adx" class="text-right py-3 px-4 font-semibold text-slate-300">ADX</th>
                    <th v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).atr" class="text-right py-3 px-4 font-semibold text-slate-300">ATR</th>
                    <th v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).mfi" class="text-right py-3 px-4 font-semibold text-slate-300">MFI</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(t, i) in paginatedTrades" :key="i" class="border-b border-slate-700/50">
                    <td class="py-3 px-4 text-white">{{ formatEntryDate(t) }}</td>
                    <td class="py-3 px-4 text-right text-white">{{ t.entry_price?.toFixed(2) }}</td>
                    <td v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).rsi" class="py-3 px-4 text-right text-white">{{ t.rsi?.toFixed(2) || '-' }}</td>
                    <td v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).adx" class="py-3 px-4 text-right text-white">{{ t.adx?.toFixed(2) || '-' }}</td>
                    <td v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).atr" class="py-3 px-4 text-right text-white">{{ t.atr?.toFixed(2) || '-' }}</td>
                    <td v-if="(indicatorFlags || indicatorFlagsRef) && (indicatorFlags || indicatorFlagsRef).mfi" class="py-3 px-4 text-right text-white">{{ t.mfi?.toFixed(2) || '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="selectedTrades.length === 0" class="text-center text-slate-400 py-6">No entries available</div>

            <div v-else-if="tradesTotalPages > 1" class="flex items-center justify-between mt-4 text-sm">
              <div class="text-slate-300">Page {{ tradesCurrentPage }} of {{ tradesTotalPages }}</div>
              <div class="flex items-center space-x-2">
                <button @click="goToTradesPage(tradesCurrentPage - 1)" :disabled="tradesCurrentPage === 1" class="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white disabled:opacity-50">Prev</button>
                <button @click="goToTradesPage(tradesCurrentPage + 1)" :disabled="tradesCurrentPage === tradesTotalPages" class="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white disabled:opacity-50">Next</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Save Strategy (with Custom Name and Notes now here) -->
        <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 space-y-4">
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Custom Name (Optional)</label>
              <input
                v-model="customName"
                type="text"
                placeholder="My EMA Strategy"
                class="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-2">Notes (Optional)</label>
              <input
                v-model="notes"
                type="text"
                placeholder="Strategy description or notes"
                class="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div class="flex flex-col items-center">
          <button
              @click.prevent="saveStrategy"
              :disabled="isSaving || !results"
              class="px-8 py-3 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-lg"
          >
              <svg v-if="saveSuccess" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
            </svg>
              <span>{{ saveSuccess ? 'Saved' : (isSaving ? 'Saving...' : 'Save to Favorites') }}</span>
            </button>
            <div v-if="!results" class="mt-2 text-xs text-slate-400">Run analysis first to enable saving.</div>
            <div v-if="saveError" class="mt-2 text-xs text-red-400">{{ saveError }}</div>
          </div>
        </div>
      </div>

      <!-- Strategy Input Form (moved to bottom, larger) -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-8 mt-6">
        <div class="space-y-6">
          <!-- Lookahead Periods Input -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-3">Lookahead Periods (comma-separated)</label>
            <div class="flex items-center space-x-4">
              <input
                v-model="lookaheadInput"
                type="text"
                placeholder="7,22,45,60"
                class="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                :disabled="isExecuting"
              />
              <div class="text-sm text-slate-400">
                Days ahead to calculate returns
              </div>
            </div>
            <div class="mt-2 text-sm text-slate-400">
              Enter comma-separated numbers (e.g., 7,22,45,60) for different lookahead periods
            </div>
          </div>

          <!-- Strategy Text Input (Larger and at the bottom) -->
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-3">Trading Strategy</label>
            <CodeEditor
              v-model="strategyInput"
              placeholder="Enter your trading strategy (e.g., ema(close, 50) > ema(close, 200))"
              :disabled="isExecuting"
              class="min-h-[220px]"
            />
          </div>

          <!-- Execute Button -->
          <div class="flex items-center justify-between pt-2">
            <div class="text-sm text-slate-400">
              <span v-if="parsedLookaheadPeriods.length > 0">
                Will analyze {{ parsedLookaheadPeriods.length }} lookahead period(s): {{ parsedLookaheadPeriods.join(', ') }} days
              </span>
              <span v-else class="text-yellow-400">
                Please enter valid lookahead periods
              </span>
            </div>
            <button
              @click="executeStrategy"
              :disabled="isExecuting || !strategyInput.trim() || parsedLookaheadPeriods.length === 0"
              class="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-lg"
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
  </div>
</template>

<script>
import { ref, computed, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import CodeEditor from '../components/CodeEditor.vue'
import ClusterScatter from '../components/ClusterScatter.vue'
import PlotlyScatter from '../components/PlotlyScatter.vue'
import TradingChart from '../components/TradingChart.vue'
import { BackendService } from '../backendService.js'

export default {
  name: 'NewStrategy',
  components: {
    CodeEditor,
    ClusterScatter,
    PlotlyScatter,
    TradingChart
  },
  setup() {
    const router = useRouter()
    const strategyInput = ref('')
    const lookaheadInput = ref('7,22,45,60')
    const customName = ref('')
    const notes = ref('')
    const results = ref(null)
    const isExecuting = ref(false)
    const isSaving = ref(false)
    const saveSuccess = ref(false)
    const saveError = ref('')
    const selectedStock = ref(null)
    const indicatorFlagsRef = ref({ rsi: false, adx: false, atr: false, mfi: false })
    // indicator detection from strategy
    const indicatorFlags = computed(() => {
      if (!strategyInput.value) return { rsi: false, adx: false, atr: false, mfi: false }
      const s = (strategyInput.value || '').toLowerCase()
      return {
        rsi: /\brsi\s*\(/.test(s) || /stochrsi/.test(s),
        adx: /\badx\s*\(/.test(s),
        atr: /\batr\s*\(/.test(s),
        mfi: /\bmfi\s*\(/.test(s),
      }
    })

    const parsedLookaheadPeriods = computed(() => {
      if (!lookaheadInput.value.trim()) return []
      return lookaheadInput.value
        .split(',')
        .map(s => parseInt(s.trim()))
        .filter(n => !isNaN(n) && n > 0)
    })

    const aggregatedMetrics = computed(() => {
      if (!results.value?.aggregated_metrics) {
        return {
          avg_return: 0,
          avg_sharpe: 0,
          avg_sortino: 0,
          avg_information_ratio: 0,
          avg_std_dev: 0,
          max_runup: 0,
          total_signals: 0,
          total_symbols: 0,
          avg_win_rate: 0,
          avg_signals_per_day: 0,
          strategy: ''
        }
      }
      const m = results.value.aggregated_metrics
      return {
        avg_return: m.average_return || 0,
        avg_sharpe: m.avg_sharpe || 0,
        avg_sortino: m.avg_sortino || 0,
        avg_information_ratio: m.avg_information_ratio || 0,
        avg_std_dev: m.avg_std_dev || 0,
        max_runup: m.max_runup || 0,
        total_signals: Number(m.total_signals) || 0,
        total_symbols: Number(m.total_symbols_processed) || 0,
        avg_win_rate: m.avg_win_rate || 0,
        avg_signals_per_day: m.avg_signals_per_day || 0,
        strategy: m.strategy || ''
      }
    })

    const formattedMetrics = computed(() => {
      return {
        total_signals: (aggregatedMetrics.value.total_signals || 0).toLocaleString(),
        avg_return: ((aggregatedMetrics.value.avg_return || 0) * 100).toFixed(2) + '%',
        win_rate: ((aggregatedMetrics.value.avg_win_rate || 0) * 100).toFixed(1) + '%'
      }
    })

    const lookaheadResults = computed(() => {
      if (!results.value?.lookahead_results) return {}
      const lookaheadData = {}
      for (const [period, stockData] of Object.entries(results.value.lookahead_results)) {
        if (stockData && stockData.length > 0) {
          lookaheadData[period] = {
            avg_return: stockData.reduce((sum, stock) => sum + stock.avg_return, 0) / stockData.length,
            win_rate: stockData.reduce((sum, stock) => sum + stock.win_rate, 0) / stockData.length,
            total_signals: stockData.reduce((sum, stock) => sum + stock.total_signals, 0),
            avg_sharpe: stockData.reduce((sum, stock) => sum + stock.sharpe_ratio, 0) / stockData.length,
            avg_sortino: stockData.reduce((sum, stock) => sum + stock.sortino_ratio, 0) / stockData.length,
            avg_std_dev: stockData.reduce((sum, stock) => sum + stock.std_dev, 0) / stockData.length,
          }
        }
      }
      return lookaheadData
    })

    const firstLookahead = computed(() => parsedLookaheadPeriods.value[0] || (results.value?.aggregated_metrics?.lookahead_periods?.[0] ?? null))

    const stockTable = computed(() => {
      if (!results.value?.lookahead_results || !selectedLookaheadPeriod.value) return []
      const rows = results.value.lookahead_results[String(selectedLookaheadPeriod.value)] || []
      return rows
    })

    // Search, sort, pagination state
    const stockSearch = ref('')
    const sortBy = ref('total_signals')
    const sortDir = ref('desc')
    const pageSize = ref(15)
    const currentPage = ref(1)
    
    // Lookahead period selection
    const selectedLookaheadPeriod = ref(null)
    const availableLookaheadPeriods = computed(() => {
      if (!results.value?.aggregated_metrics?.lookahead_periods) return []
      return results.value.aggregated_metrics.lookahead_periods
    })
    
    // Watch for results changes to set initial selected period
    watch(() => results.value, (newResults) => {
      if (newResults?.aggregated_metrics?.lookahead_periods?.length > 0) {
        selectedLookaheadPeriod.value = newResults.aggregated_metrics.lookahead_periods[0]
      }
    }, { immediate: true })

    // Clustering state
    const clusterFeatureX = ref('sharpe_ratio')
    const clusterFeatureY = ref('avg_return')
    const clusterK = ref(3)
    const clusterAssignments = reactive(new Map())
    const clusterSummary = reactive({ k: 0, featureXLabel: '', featureYLabel: '' })

    const clusterableFeatures = computed(() => [
      { key: 'avg_return', label: 'Avg Return' },
      { key: 'win_rate', label: 'Win Rate' },
      { key: 'sharpe_ratio', label: 'Sharpe' },
      { key: 'sortino_ratio', label: 'Sortino' },
      { key: 'information_ratio', label: 'Info Ratio' },
      { key: 'total_signals', label: 'Signals' },
    ])

    const canCluster = computed(() => {
      const valid = results.value && stockTable.value?.length > clusterK.value && clusterK.value >= 2
      return valid && clusterFeatureX.value && clusterFeatureY.value && clusterFeatureX.value !== clusterFeatureY.value
    })

    const zscore = (arr) => {
      const n = arr.length
      if (n === 0) return arr
      const mean = arr.reduce((s, v) => s + v, 0) / n
      const std = Math.sqrt(arr.reduce((s, v) => s + (v - mean) * (v - mean), 0) / Math.max(1, n - 1)) || 1
      return arr.map(v => (v - mean) / std)
    }

    const runClustering = () => {
      if (!canCluster.value) return
      clusterAssignments.clear()
      // Use ALL symbols for the selected lookahead period directly from raw results
      const periodKey = String(selectedLookaheadPeriod.value)
      const rowsRaw = (results.value?.lookahead_results?.[periodKey] || [])
      const fxKey = clusterFeatureX.value
      const fyKey = clusterFeatureY.value
      // Extract arrays and median-impute missing values to avoid dropping symbols
      const xRaw = rowsRaw.map(r => Number(r[fxKey]))
      const yRaw = rowsRaw.map(r => Number(r[fyKey]))
      const median = (arr) => {
        const vals = arr.filter(v => Number.isFinite(v)).sort((a,b)=>a-b)
        if (vals.length === 0) return 0
        const mid = Math.floor(vals.length/2)
        return vals.length % 2 ? vals[mid] : (vals[mid-1] + vals[mid]) / 2
      }
      const mx = median(xRaw)
      const my = median(yRaw)
      const x = xRaw.map(v => Number.isFinite(v) ? v : mx)
      const y = yRaw.map(v => Number.isFinite(v) ? v : my)
      const rows = rowsRaw
      const xs = zscore(x)
      const ys = zscore(y)
      const points = xs.map((vx, i) => [vx, ys[i]])
      // initialize centroids with first k unique points
      const k = Math.min(clusterK.value, points.length)
      let centroids = points.slice(0, k).map(p => [...p])
      let assignments = new Array(points.length).fill(0)
      const dist2 = (a, b) => (a[0]-b[0])**2 + (a[1]-b[1])**2
      for (let iter = 0; iter < 50; iter++) {
        // assign
        let changed = false
        for (let i = 0; i < points.length; i++) {
          let best = 0, bestd = Infinity
          for (let c = 0; c < centroids.length; c++) {
            const d = dist2(points[i], centroids[c])
            if (d < bestd) { bestd = d; best = c }
          }
          if (assignments[i] !== best) { assignments[i] = best; changed = true }
        }
        // update centroids
        const sums = Array.from({ length: k }, () => [0, 0])
        const counts = Array.from({ length: k }, () => 0)
        for (let i = 0; i < points.length; i++) {
          const c = assignments[i]
          sums[c][0] += points[i][0]
          sums[c][1] += points[i][1]
          counts[c] += 1
        }
        for (let c = 0; c < k; c++) {
          if (counts[c] > 0) {
            centroids[c][0] = sums[c][0] / counts[c]
            centroids[c][1] = sums[c][1] / counts[c]
          }
        }
        if (!changed) break
      }
      // save assignments mapped by symbol
      for (let i = 0; i < rows.length; i++) {
        clusterAssignments.set(rows[i].symbol, (assignments[i] + 1))
      }
      const fx = clusterableFeatures.value.find(f => f.key === clusterFeatureX.value)
      const fy = clusterableFeatures.value.find(f => f.key === clusterFeatureY.value)
      clusterSummary.k = k
      clusterSummary.featureXLabel = fx?.label || clusterFeatureX.value
      clusterSummary.featureYLabel = fy?.label || clusterFeatureY.value
    }

    const clearClustering = () => {
      clusterAssignments.clear()
      clusterSummary.k = 0
      clusterSummary.featureXLabel = ''
      clusterSummary.featureYLabel = ''
    }

    // Points for scatter
    const clusterPoints = computed(() => {
      if (clusterAssignments.size === 0) return []
      const fx = clusterFeatureX.value
      const fy = clusterFeatureY.value
      const periodKey = String(selectedLookaheadPeriod.value)
      const rowsRaw = (results.value?.lookahead_results?.[periodKey] || [])
      return rowsRaw.map(r => ({ symbol: r.symbol, x: Number(r[fx]), y: Number(r[fy]), cluster: clusterAssignments.get(r.symbol) || 0 }))
    })

    const filteredStocks = computed(() => {
      const q = stockSearch.value.trim().toLowerCase()
      let rows = stockTable.value
      if (q) rows = rows.filter(r => r.symbol?.toLowerCase().includes(q))
      return rows
    })

    const sortedStocks = computed(() => {
      const key = sortBy.value
      const dir = sortDir.value === 'desc' ? -1 : 1
      return [...filteredStocks.value].sort((a, b) => {
        const av = a[key] ?? 0
        const bv = b[key] ?? 0
        if (av < bv) return -1 * dir
        if (av > bv) return 1 * dir
        return 0
      })
    })

    const totalPages = computed(() => Math.max(1, Math.ceil(sortedStocks.value.length / pageSize.value)))

    const paginatedStocks = computed(() => {
      const start = (currentPage.value - 1) * pageSize.value
      return sortedStocks.value.slice(start, start + pageSize.value)
    })

    const goToPage = (p) => {
      const tp = totalPages.value
      if (p < 1) p = 1
      if (p > tp) p = tp
      currentPage.value = p
    }

    const toggleSortDir = () => {
      sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
    }

    watch([stockSearch, sortBy, sortDir, stockTable], () => {
      currentPage.value = 1
    })

    const selectedTrades = computed(() => {
      if (!selectedStock.value) return []
      return selectedStock.value.trades || []
    })

    const selectStock = (row) => {
      selectedStock.value = row
      try {
        const indicators = JSON.stringify(indicatorFlags.value || {})
        const periods = JSON.stringify(parsedLookaheadPeriods.value || [7,22,45,60])
        window.location.href = `/trade-analysis/${encodeURIComponent(row.symbol)}?indicators=${encodeURIComponent(indicators)}&periods=${encodeURIComponent(periods)}`
      } catch (_) {
        // fallback: just set selection
      }
    }

    const executeStrategy = async () => {
      if (!strategyInput.value.trim() || parsedLookaheadPeriods.value.length === 0) return
      isExecuting.value = true
      results.value = null
      try {
        const response = await BackendService.executeStrategyMultiLookahead(strategyInput.value.trim(), parsedLookaheadPeriods.value)
        if (response && response.ok) {
          results.value = response.results
        } else {
          console.error('Strategy execution failed:', response)
          alert(response?.error || 'Execution failed')
        }
      } catch (error) {
        console.error('Error executing strategy:', error)
        alert('Error executing strategy. Check backend logs.')
      } finally {
        isExecuting.value = false
      }
    }

    const saveStrategy = () => {
      if (!results.value || isSaving.value) return
      console.log('[NewStrategy] saveStrategy clicked')
      isSaving.value = true
      saveSuccess.value = false
      saveError.value = ''

      // store only essential, lightweight fields
      const strategyData = {
        id: Date.now().toString(),
        strategyText: strategyInput.value.trim(),
        customName: customName.value.trim() || null,
        notes: notes.value.trim() || null,
        dateAdded: new Date().toISOString().split('T')[0],
        lookaheadPeriods: parsedLookaheadPeriods.value,
        avgReturn: aggregatedMetrics.value.avg_return,
        sharpe: aggregatedMetrics.value.avg_sharpe,
        winRate: aggregatedMetrics.value.avg_win_rate,
        totalSignals: aggregatedMetrics.value.total_signals
      }

      let favorites = []
      try {
        const stored = localStorage.getItem('alpha_strategy_favorites')
        if (stored) {
          favorites = JSON.parse(stored)
        }
      } catch (error) {
        console.error('Error loading favorites:', error)
      }

      // migrate existing entries to lightweight format to reduce size
      const toLight = (s) => ({
        id: s.id || Date.now().toString(),
        strategyText: s.strategyText,
        customName: s.customName || null,
        notes: s.notes || null,
        dateAdded: s.dateAdded || new Date().toISOString().split('T')[0],
        lookaheadPeriods: s.lookaheadPeriods || [],
        avgReturn: s.avgReturn ?? 0,
        sharpe: s.sharpe ?? 0,
        winRate: s.winRate ?? 0,
        totalSignals: s.totalSignals ?? 0
      })
      favorites = (favorites || []).map(toLight)

      // de-duplicate by strategyText + lookaheadPeriods
      const key = strategyData.strategyText + '|' + strategyData.lookaheadPeriods.join(',')
      const idx = favorites.findIndex(s => (s.strategyText + '|' + (s.lookaheadPeriods || []).join(',')) === key)
      if (idx >= 0) {
        favorites[idx] = { ...favorites[idx], ...strategyData, id: favorites[idx].id }
      } else {
      favorites.unshift(strategyData)
      }

      // cap history length
      const MAX_FAVORITES = 200
      if (favorites.length > MAX_FAVORITES) {
        favorites = favorites.slice(0, MAX_FAVORITES)
      }

      // attempt to save; if quota, trim until it fits
      const trySave = () => {
      try {
        localStorage.setItem('alpha_strategy_favorites', JSON.stringify(favorites))
          return true
        } catch (e) {
          return false
        }
      }

      if (!trySave()) {
        // progressively trim older items
        let trimmed = false
        while (favorites.length > 0 && !trySave()) {
          favorites.pop()
          trimmed = true
        }
        if (!trySave()) {
          saveError.value = 'Storage is full. Delete some saved strategies from History.'
          console.error('Error saving strategy: storage full')
          isSaving.value = false
          return
        }
        if (trimmed) {
          saveError.value = 'Oldest saved strategies were trimmed due to storage limits.'
        }
      }

      window.dispatchEvent(new CustomEvent('favorites-updated'))
      saveSuccess.value = true
      isSaving.value = false
    }

    // reset "Saved" state when inputs change
    watch([strategyInput, lookaheadInput, customName, notes], () => {
      saveSuccess.value = false
    })

    // trades pagination
    const tradesPageSize = ref(15)
    const tradesCurrentPage = ref(1)
    const tradesTotalPages = computed(() => Math.max(1, Math.ceil(selectedTrades.value.length / tradesPageSize.value)))
    const paginatedTrades = computed(() => {
      const start = (tradesCurrentPage.value - 1) * tradesPageSize.value
      return selectedTrades.value.slice(start, start + tradesPageSize.value)
    })
    const goToTradesPage = (p) => {
      const tp = tradesTotalPages.value
      if (p < 1) p = 1
      if (p > tp) p = tp
      tradesCurrentPage.value = p
    }
    watch([selectedStock], () => { tradesCurrentPage.value = 1 })

    const formatEntryDate = (t) => {
      if (t.entry_date && typeof t.entry_date === 'string') {
        const s = t.entry_date
        if (s.length >= 10) return s.slice(0, 10)
        // fallback parse
        try { return new Date(s).toISOString().slice(0,10) } catch (_) { /* noop */ }
      }
      if (t.entry_date && t.entry_date.toISOString) return t.entry_date.toISOString().slice(0,10)
      if (typeof t.entry_date === 'number') {
        try { return new Date(t.entry_date).toISOString().slice(0,10) } catch (_) {}
      }
      return '#' + (t.entry_index ?? '?')
    }

    return {
      strategyInput,
      lookaheadInput,
      customName,
      notes,
      results,
      isExecuting,
      isSaving,
      saveSuccess,
      saveError,
      parsedLookaheadPeriods,
      aggregatedMetrics,
      formattedMetrics,
      lookaheadResults,
      executeStrategy,
      saveStrategy,
      firstLookahead,
      selectedLookaheadPeriod,
      availableLookaheadPeriods,
      // clustering
      clusterFeatureX,
      clusterFeatureY,
      clusterK,
      clusterAssignments,
      clusterSummary,
      clusterPoints,
      clusterableFeatures,
      canCluster,
      runClustering,
      clearClustering,
      stockTable,
      selectedStock,
      // search/sort/pagination
      stockSearch,
      sortBy,
      sortDir,
      pageSize,
      currentPage,
      filteredStocks,
      sortedStocks,
      paginatedStocks,
      totalPages,
      goToPage,
      toggleSortDir,
      // trades
      selectedTrades,
      selectStock,
      tradesPageSize,
      tradesCurrentPage,
      tradesTotalPages,
      paginatedTrades,
      goToTradesPage,
      formatEntryDate,
      indicatorFlags,
      indicatorFlagsRef
      
    }
  }
}
</script>

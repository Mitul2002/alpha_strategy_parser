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
              <p class="text-slate-400 text-sm">Professional Trading Strategy Analysis Platform</p>
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

    <!-- Main Content Area - Full Width -->
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
          <p class="text-slate-400">Enter a trading strategy below to see detailed analysis and performance metrics</p>
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
            
          <!-- Performance Metrics -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <h3 class="text-lg font-semibold text-white">Performance Overview</h3>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="text-center p-6 bg-gradient-to-br from-purple-900/20 to-purple-800/20 rounded-xl border border-purple-700/30">
                  <div class="text-4xl font-bold text-purple-400 mb-2">{{ results.summary?.total_trades || 0 }}</div>
                  <div class="text-purple-300 text-sm font-medium">Total Trades</div>
                  <div class="text-purple-400/60 text-xs mt-1">Market opportunities detected</div>
                </div>
                
                <div class="text-center p-6 bg-gradient-to-br from-green-900/20 to-green-800/20 rounded-xl border border-green-700/30">
                  <div class="text-4xl font-bold text-green-400 mb-2">{{ results.summary?.win_rate?.toFixed(1) || 0 }}%</div>
                  <div class="text-green-300 text-sm font-medium">Win Rate</div>
                  <div class="text-green-400/60 text-xs mt-1">Profitable trades</div>
                </div>
              </div>
              
              <!-- Additional Metrics -->
              <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ results.summary?.winning_trades || 0 }}</div>
                  <div class="text-slate-300 text-xs">Winning Trades</div>
                </div>
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ results.summary?.losing_trades || 0 }}</div>
                  <div class="text-slate-300 text-xs">Losing Trades</div>
                </div>
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">₹{{ results.summary?.total_pnl?.toFixed(2) || '0.00' }}</div>
                  <div class="text-slate-300 text-xs">Total PnL</div>
                </div>
                <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div class="text-2xl font-bold text-white mb-1">{{ results.summary?.total_pnl_pct?.toFixed(2) || '0.00' }}%</div>
                  <div class="text-slate-300 text-xs">Return %</div>
                </div>
              </div>
            </div>
          </div>
              
          <!-- Trades Table with Pagination and Date Filtering -->
          <div class="bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
            <div class="bg-gradient-to-r from-slate-700 to-slate-800 px-6 py-4 border-b border-slate-700">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-semibold text-white">Trade Analysis</h3>
                  <p class="text-slate-400 text-sm mt-1">Detailed breakdown of all trade entries with indicator values</p>
                </div>
                <div class="flex items-center space-x-4">
                  <!-- Date Range Filter -->
                  <div class="flex items-center space-x-2">
                    <label class="text-sm text-slate-300">From:</label>
                    <input 
                      type="date" 
                      v-model="dateFilter.startDate"
                      @change="applyDateFilter"
                      class="bg-slate-700 border border-slate-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div class="flex items-center space-x-2">
                    <label class="text-sm text-slate-300">To:</label>
                    <input 
                      type="date" 
                      v-model="dateFilter.endDate"
                      @change="applyDateFilter"
                      class="bg-slate-700 border border-slate-600 rounded px-3 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button 
                    @click="clearDateFilter"
                    class="px-3 py-1 bg-slate-600 hover:bg-slate-500 text-white text-sm rounded transition-colors"
                  >
                    Clear Filter
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Trades Count and Pagination Info -->
            <div class="px-6 py-3 bg-slate-700/50 border-b border-slate-600 flex items-center justify-between">
              <div class="text-sm text-slate-300">
                Showing {{ paginationDisplayInfo.startIndex + 1 }}-{{ paginationDisplayInfo.endIndex }} of {{ filteredTrades.length }} trades
                <span v-if="dateFilter.startDate || dateFilter.endDate" class="text-blue-400 ml-2">
                  (Date filtered)
                </span>
              </div>
              <div class="flex items-center space-x-2">
                <label class="text-sm text-slate-300">Trades per page:</label>
                <select 
                  v-model="paginationInfo.itemsPerPage" 
                  @change="changePageSize"
                  class="bg-slate-700 border border-slate-600 rounded px-2 py-1 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>
            
            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-slate-700">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">#</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Entry Date</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Entry Price</th>
                    <th v-for="column in getIndicatorColumns" :key="column.key" class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">{{ column.label }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">PnL</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Return %</th>
                  </tr>
                </thead>
                <tbody class="bg-slate-800 divide-y divide-slate-700">
                  <tr v-for="trade in paginatedTrades" :key="trade.trade_number" class="hover:bg-slate-700/50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-300">{{ trade.trade_number }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">{{ trade.entry_date }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-slate-300 font-medium">₹{{ trade.entry_price?.toFixed(2) }}</td>
                    <td v-for="column in getIndicatorColumns" :key="column.key" class="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      <span class="font-mono">{{ getIndicatorValue(trade, column.key) !== null ? getIndicatorValue(trade, column.key)?.toFixed(2) : 'N/A' }}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <span :class="trade.pnl >= 0 ? 'text-green-400 font-medium' : 'text-red-400 font-medium'">
                        ₹{{ trade.pnl?.toFixed(2) || 'N/A' }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <span :class="trade.pnl_pct >= 0 ? 'text-green-400 font-medium' : 'text-red-400 font-medium'">
                        {{ trade.pnl_pct?.toFixed(2) || 'N/A' }}%
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Pagination Controls -->
            <div class="px-6 py-4 bg-slate-700/50 border-t border-slate-600">
              <div class="flex items-center justify-between">
                <div class="text-sm text-slate-300">
                  Page {{ paginationInfo.currentPage }} of {{ totalPages }}
                </div>
                <div class="flex items-center space-x-2">
                  <!-- First Page -->
                  <button 
                    @click="goToPage(1)"
                    :disabled="paginationInfo.currentPage === 1"
                    class="px-3 py-1 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
                  >
                    First
                  </button>
                  
                  <!-- Previous Page -->
                  <button 
                    @click="goToPage(paginationInfo.currentPage - 1)"
                    :disabled="paginationInfo.currentPage === 1"
                    class="px-3 py-1 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
                  >
                    Previous
                  </button>
                  
                  <!-- Page Numbers -->
                  <div class="flex items-center space-x-1">
                    <button 
                      v-for="page in visiblePageNumbers" 
                      :key="page"
                      @click="goToPage(page)"
                      :class="[
                        'px-3 py-1 text-sm rounded transition-colors',
                        page === paginationInfo.currentPage 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-slate-600 hover:bg-slate-500 text-white'
                      ]"
                    >
                      {{ page }}
                    </button>
                  </div>
                  
                  <!-- Next Page -->
                  <button 
                    @click="goToPage(paginationInfo.currentPage + 1)"
                    :disabled="paginationInfo.currentPage === totalPages"
                    class="px-3 py-1 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
                  >
                    Next
                  </button>
                  
                  <!-- Last Page -->
                  <button 
                    @click="goToPage(totalPages)"
                    :disabled="paginationInfo.currentPage === totalPages"
                    class="px-3 py-1 bg-slate-600 hover:bg-slate-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm rounded transition-colors"
                  >
                    Last
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
              
    <!-- Bottom Input Bar - Fixed at Bottom -->
    <div class="bg-slate-800 border-t border-slate-700 px-6 py-4">
      <div class="max-w-7xl mx-auto">
        <div class="flex gap-4 items-end">
          <!-- Strategy Input -->
          <div class="flex-1">
            <CodeEditor
              v-model="strategyInput"
              @ctrlEnter="executeStrategy"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import SyntaxHighlightedInput from './components/SyntaxHighlightedInput.vue'
import CodeEditor from './components/CodeEditor.vue' // Added import for CodeEditor

export default {
  name: 'App',
  components: {
    SyntaxHighlightedInput,
    CodeEditor // Added CodeEditor to components
  },
  setup() {
    const strategyInput = ref('')
    const selectedStock = ref('RELIANCE')
    const results = ref(null)
    const isExecuting = ref(false)
    
    // Pagination state
    const paginationInfo = ref({
      currentPage: 1,
      itemsPerPage: 25
    })
    
    // Date filtering state
    const dateFilter = ref({
      startDate: '',
      endDate: ''
    })

    // Handle strategy input keydown events
    const handleStrategyKeydown = (event) => {
      if (event.ctrlKey && event.key === 'Enter') {
        executeStrategy()
      }
    }

    // Function to get indicator values from trade data
    const getIndicatorValue = (trade, indicator) => {
      if (!trade.indicators) return null
      
      // Map indicator names to the keys in the indicators object
      const indicatorMap = {
        'rsi': 'rsi',
        'ema_21': 'ema_21',
        'ema_50': 'ema_50', 
        'ema_200': 'ema_200',
        'sma_50': 'sma_50',
        'sma_200': 'sma_200'
      }
      
      const key = indicatorMap[indicator]
      return key ? trade.indicators[key] : null
    }

    // Get available indicator columns based on the first trade
    const getIndicatorColumns = computed(() => {
      if (!results.value?.trades?.length) return []
      
      const firstTrade = results.value.trades[0]
      if (!firstTrade.indicators) return []
      
      const columns = []
      if (firstTrade.indicators.rsi !== undefined) columns.push({ key: 'rsi', label: 'RSI(14)' })
      if (firstTrade.indicators.ema_21 !== undefined) columns.push({ key: 'ema_21', label: 'EMA(21)' })
      if (firstTrade.indicators.ema_50 !== undefined) columns.push({ key: 'ema_50', label: 'EMA(50)' })
      if (firstTrade.indicators.ema_200 !== undefined) columns.push({ key: 'ema_200', label: 'EMA(200)' })
      if (firstTrade.indicators.sma_50 !== undefined) columns.push({ key: 'sma_50', label: 'SMA(50)' })
      if (firstTrade.indicators.sma_200 !== undefined) columns.push({ key: 'sma_200', label: 'SMA(200)' })
      
      return columns
    })

    // Filtered trades based on date range
    const filteredTrades = computed(() => {
      if (!results.value?.trades) return []
      
      let trades = results.value.trades
      
      // Apply date filtering
      if (dateFilter.value.startDate || dateFilter.value.endDate) {
        trades = trades.filter(trade => {
          const tradeDate = new Date(trade.entry_date)
          const startDate = dateFilter.value.startDate ? new Date(dateFilter.value.startDate) : null
          const endDate = dateFilter.value.endDate ? new Date(dateFilter.value.endDate) : null
          
          if (startDate && tradeDate < startDate) return false
          if (endDate && tradeDate > endDate) return false
          
          return true
        })
      }
      
      return trades
    })

    // Pagination computed properties
    const totalPages = computed(() => {
      return Math.ceil(filteredTrades.value.length / paginationInfo.value.itemsPerPage)
    })

    const paginationDisplayInfo = computed(() => {
      const startIndex = (paginationInfo.value.currentPage - 1) * paginationInfo.value.itemsPerPage
      const endIndex = Math.min(startIndex + paginationInfo.value.itemsPerPage, filteredTrades.value.length)
      
      return {
        startIndex,
        endIndex,
        currentPage: paginationInfo.value.currentPage,
        itemsPerPage: paginationInfo.value.itemsPerPage
      }
    })

    const paginatedTrades = computed(() => {
      const startIndex = paginationDisplayInfo.value.startIndex
      const endIndex = paginationDisplayInfo.value.endIndex
      
      return filteredTrades.value.slice(startIndex, endIndex)
    })

    // Visible page numbers for pagination
    const visiblePageNumbers = computed(() => {
      const current = paginationInfo.value.currentPage
      const total = totalPages.value
      const delta = 2
      
      const range = []
      const rangeWithDots = []
      
      for (let i = Math.max(2, current - delta); i <= Math.min(total - 1, current + delta); i++) {
        range.push(i)
      }
      
      if (current - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }
      
      rangeWithDots.push(...range)
      
      if (current + delta < total - 1) {
        rangeWithDots.push('...', total)
      } else if (total > 1) {
        rangeWithDots.push(total)
      }
      
      return rangeWithDots.filter(page => page !== '...')
    })

    // Pagination methods
    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        paginationInfo.value.currentPage = page
      }
    }

    const changePageSize = () => {
      paginationInfo.value.currentPage = 1 // Reset to first page when changing page size
    }

    // Date filtering methods
    const applyDateFilter = () => {
      paginationInfo.value.currentPage = 1 // Reset to first page when applying date filter
    }

    const clearDateFilter = () => {
      dateFilter.value.startDate = ''
      dateFilter.value.endDate = ''
      paginationInfo.value.currentPage = 1 // Reset to first page when clearing filter
    }

    // Reset pagination when results change
    watch(() => results.value, () => {
      paginationInfo.value.currentPage = 1
      dateFilter.value.startDate = ''
      dateFilter.value.endDate = ''
    })

    const executeStrategy = async () => {
      if (!strategyInput.value.trim()) return
      
      isExecuting.value = true
      
      try {
        const response = await fetch('http://127.0.0.1:8000/execute', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            strategy: strategyInput.value.trim(),
            timeframe: 'daily',
            mode: 'single',
            stock: selectedStock.value
          })
        })
        
        const data = await response.json()
        
        if (data.ok) {
          results.value = {
            ...data.results[0],
            strategy: strategyInput.value.trim() // Store the strategy for display
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
      selectedStock,
      results,
      isExecuting,
      paginationInfo,
      dateFilter,
      filteredTrades,
      totalPages,
      paginationDisplayInfo,
      paginatedTrades,
      visiblePageNumbers,
      getIndicatorValue,
      getIndicatorColumns,
      executeStrategy,
      goToPage,
      changePageSize,
      applyDateFilter,
      clearDateFilter,
      handleStrategyKeydown
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
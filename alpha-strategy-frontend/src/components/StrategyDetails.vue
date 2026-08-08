<template>
  <div class="p-6 bg-slate-700/30">
    <!-- Aggregated Metrics -->
    <div class="mb-8">
      <h4 class="text-lg font-semibold text-white mb-4">Performance Summary</h4>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
          <div class="text-xl font-bold text-white mb-1">{{ (strategy.avgReturn * 100).toFixed(2) }}%</div>
          <div class="text-slate-300 text-xs">Avg Return</div>
        </div>
        <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
          <div class="text-xl font-bold text-white mb-1">{{ strategy.sharpe.toFixed(2) }}</div>
          <div class="text-slate-300 text-xs">Sharpe Ratio</div>
        </div>
        <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
          <div class="text-xl font-bold text-white mb-1">{{ (strategy.winRate * 100).toFixed(1) }}%</div>
          <div class="text-slate-300 text-xs">Win Rate</div>
        </div>
        <div class="text-center p-4 bg-slate-700/50 rounded-lg border border-slate-600">
          <div class="text-xl font-bold text-white mb-1">{{ strategy.totalSignals.toLocaleString() }}</div>
          <div class="text-slate-300 text-xs">Total Signals</div>
        </div>
      </div>
    </div>

    <!-- Stock-wise Performance Table -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-4">
        <h4 class="text-lg font-semibold text-white">Stock-wise Performance</h4>
        <div class="flex items-center space-x-4">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              v-model="stockSearchQuery"
              type="text"
              placeholder="Search stocks..."
              class="pl-10 pr-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
          <select
            v-model="stockSortBy"
            class="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          >
            <option value="symbol">Symbol</option>
            <option value="avg_return">Avg Return</option>
            <option value="sharpe">Sharpe</option>
            <option value="win_rate">Win Rate</option>
            <option value="total_signals">Signals</option>
          </select>
        </div>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-600">
              <th class="text-left py-3 px-4 font-semibold text-slate-300">Symbol</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Signals</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Avg Return</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Win Rate</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Sharpe</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Max Runup</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Max Drawdown</th>
              <th class="text-right py-3 px-4 font-semibold text-slate-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="stock in filteredStockData" 
              :key="stock.symbol" 
              class="border-b border-slate-700/50 hover:bg-slate-700/30"
            >
              <td class="py-3 px-4 font-medium text-white">{{ stock.symbol }}</td>
              <td class="py-3 px-4 text-right text-white">{{ stock.totalSignals.toLocaleString() }}</td>
              <td class="py-3 px-4 text-right" :class="stock.avgReturn >= 0 ? 'text-green-400' : 'text-red-400'">
                {{ (stock.avgReturn * 100).toFixed(2) }}%
              </td>
              <td class="py-3 px-4 text-right text-white">{{ (stock.winRate * 100).toFixed(1) }}%</td>
              <td class="py-3 px-4 text-right" :class="stock.sharpe >= 0 ? 'text-green-400' : 'text-red-400'">
                {{ stock.sharpe.toFixed(2) }}
              </td>
              <td class="py-3 px-4 text-right text-green-400">{{ (stock.maxRunup * 100).toFixed(2) }}%</td>
              <td class="py-3 px-4 text-right text-red-400">{{ (stock.maxDrawdown * 100).toFixed(2) }}%</td>
              <td class="py-3 px-4 text-right">
                <button
                  @click="viewStockTrades(stock)"
                  class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors duration-200"
                >
                  View Trades
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Individual Trades Modal -->
    <div v-if="selectedStock" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 w-full max-w-4xl mx-4 max-h-[80vh] overflow-hidden">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-semibold text-white">Individual Trades - {{ selectedStock.symbol }}</h3>
          <button
            @click="selectedStock = null"
            class="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded-lg transition-colors duration-200"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="overflow-y-auto max-h-[60vh]">
          <div v-if="selectedStockTrades.length === 0" class="text-center py-8">
            <p class="text-slate-400">No individual trade data available for this stock.</p>
          </div>
          <div v-else class="space-y-2">
            <div 
              v-for="(trade, index) in selectedStockTrades" 
              :key="index"
              class="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
            >
              <div class="flex items-center space-x-4">
                <span class="text-slate-400 text-sm">Trade #{{ index + 1 }}</span>
                <span class="text-white">{{ trade.date }}</span>
              </div>
              <div class="flex items-center space-x-6 text-sm">
                <span class="text-slate-400">Entry: {{ trade.entryPrice }}</span>
                <span class="text-slate-400">Exit: {{ trade.exitPrice }}</span>
                <span :class="trade.return >= 0 ? 'text-green-400' : 'text-red-400'">
                  {{ (trade.return * 100).toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'StrategyDetails',
  props: {
    strategy: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const stockSearchQuery = ref('')
    const stockSortBy = ref('symbol')
    const selectedStock = ref(null)
    const selectedStockTrades = ref([])

    const filteredStockData = computed(() => {
      let filtered = [...(props.strategy.stockwiseData || [])]

      // Search filter
      if (stockSearchQuery.value) {
        const query = stockSearchQuery.value.toLowerCase()
        filtered = filtered.filter(stock => 
          stock.symbol.toLowerCase().includes(query)
        )
      }

      // Sort
      filtered.sort((a, b) => {
        switch (stockSortBy.value) {
          case 'avg_return':
            return b.avgReturn - a.avgReturn
          case 'sharpe':
            return b.sharpe - a.sharpe
          case 'win_rate':
            return b.winRate - a.winRate
          case 'total_signals':
            return b.totalSignals - a.totalSignals
          case 'symbol':
          default:
            return a.symbol.localeCompare(b.symbol)
        }
      })

      return filtered
    })

    const viewStockTrades = (stock) => {
      selectedStock.value = stock
      // For now, generate mock trade data
      // In the future, this would come from the backend
      selectedStockTrades.value = generateMockTrades(stock)
    }

    const generateMockTrades = (stock) => {
      // Mock trade data - in real implementation, this would come from backend
      const trades = []
      const numTrades = Math.min(stock.totalSignals, 20) // Limit to 20 trades for demo
      
      for (let i = 0; i < numTrades; i++) {
        trades.push({
          date: `2024-01-${String(i + 1).padStart(2, '0')}`,
          entryPrice: (100 + Math.random() * 50).toFixed(2),
          exitPrice: (100 + Math.random() * 50).toFixed(2),
          return: (Math.random() - 0.5) * 0.1 // Random return between -5% and +5%
        })
      }
      
      return trades
    }

    return {
      stockSearchQuery,
      stockSortBy,
      selectedStock,
      selectedStockTrades,
      filteredStockData,
      viewStockTrades
    }
  }
}
</script>

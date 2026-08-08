import re

# Read the current NewStrategy.vue file
with open('NewStrategy.vue', 'r') as f:
    content = f.read()

# Update the Stock Results header section
old_header = '''            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h11M9 21V3m12 7h-4m0 0V7m0 3v4"></path>
                </svg>
                <h3 class="text-lg font-semibold text-white">Stock Results ({{ firstLookahead }} days)</h3>
              </div>
              <div class="flex items-center space-x-4">
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
                    <option value="sharpe_ratio">Sharpe</option>'''

new_header = '''            <div class="flex items-center justify-between">
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
                    <option value="sharpe_ratio">Sharpe</option>'''

content = content.replace(old_header, new_header)

# Update the stockTable computed property to use selectedLookaheadPeriod
old_stockTable = '''    const stockTable = computed(() => {
      if (!results.value?.lookahead_results || !firstLookahead.value) return []
      const rows = results.value.lookahead_results[String(firstLookahead.value)] || []
      return rows
    })'''

new_stockTable = '''    const stockTable = computed(() => {
      if (!results.value?.lookahead_results || !selectedLookaheadPeriod.value) return []
      const rows = results.value.lookahead_results[String(selectedLookaheadPeriod.value)] || []
      return rows
    })'''

content = content.replace(old_stockTable, new_stockTable)

# Add the new reactive variables after the existing ones
old_variables = '''    // Search, sort, pagination state
    const stockSearch = ref('')
    const sortBy = ref('total_signals')
    const sortDir = ref('desc')
    const pageSize = ref(15)
    const currentPage = ref(1)'''

new_variables = '''    // Search, sort, pagination state
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
    }, { immediate: true })'''

content = content.replace(old_variables, new_variables)

# Add the new variables to the return statement
old_return = '''    return {
      strategyInput,
      lookaheadInput,
      isExecuting,
      results,
      error,
      indicatorFlags,
      indicatorFlagsRef,
      parsedLookaheadPeriods,
      aggregatedMetrics,
      performanceTable,
      stockTable,
      stockSearch,
      sortBy,
      sortDir,
      pageSize,
      currentPage,
      selectedStock,
      showChart,
      firstLookahead,
      executeStrategy,
      clearResults,
      formatNumber,
      formatPercentage,
      sortedAndFilteredStocks,
      paginatedStocks,
      totalPages,
      goToPage,
      nextPage,
      prevPage,
      selectStock,
      closeChart
    }'''

new_return = '''    return {
      strategyInput,
      lookaheadInput,
      isExecuting,
      results,
      error,
      indicatorFlags,
      indicatorFlagsRef,
      parsedLookaheadPeriods,
      aggregatedMetrics,
      performanceTable,
      stockTable,
      stockSearch,
      sortBy,
      sortDir,
      pageSize,
      currentPage,
      selectedStock,
      showChart,
      firstLookahead,
      selectedLookaheadPeriod,
      availableLookaheadPeriods,
      executeStrategy,
      clearResults,
      formatNumber,
      formatPercentage,
      sortedAndFilteredStocks,
      paginatedStocks,
      totalPages,
      goToPage,
      nextPage,
      prevPage,
      selectStock,
      closeChart
    }'''

content = content.replace(old_return, new_return)

# Write the updated content
with open('NewStrategy.vue', 'w') as f:
    f.write(content)

print("Updated NewStrategy.vue with dynamic lookahead period selector")

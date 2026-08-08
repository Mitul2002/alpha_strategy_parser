<!-- Updated Stock Results section with dynamic lookahead period selection -->
<div class="bg-slate-800 rounded-lg p-6">
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-2">
      <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h11M9 21V3m12 7h-4m0 0V7m0 3v4"></path>
      </svg>
      <h3 class="text-lg font-semibold text-white">Stock Results</h3>
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
        </select>
        <button 
          @click="sortDir = sortDir === 'asc' ? 'desc' : 'asc'"
          class="bg-slate-700 border border-slate-600 text-white rounded px-2 py-2 hover:bg-slate-600 transition-colors"
        >
          {{ sortDir === 'asc' ? '↑' : '↓' }}
        </button>
      </div>
    </div>
  </div>
  
  <!-- Rest of the stock results table remains the same -->
  <!-- ... existing table code ... -->
</div>

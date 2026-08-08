<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-7xl mx-auto px-6 py-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white mb-4">Strategy History</h1>
        <p class="text-slate-400">Your saved and favorited trading strategies</p>
      </div>

      <!-- Search and Filter Bar -->
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4">
          <!-- Search Input -->
          <div class="flex-1">
            <div class="relative">
              <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search strategies (e.g., ema, rsi, close > sma...)"
                class="w-full pl-10 pr-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <!-- Sort Dropdown -->
          <div class="md:w-64">
            <select
              v-model="sortBy"
              class="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="date">Date Added</option>
              <option value="name">Strategy Name</option>
              <option value="avg_return">Avg Return</option>
              <option value="sharpe">Sharpe Ratio</option>
              <option value="win_rate">Win Rate</option>
              <option value="total_signals">Total Signals</option>
            </select>
          </div>

          <!-- Date Range Filter -->
          <div class="md:w-64">
            <input
              v-model="dateRange"
              type="text"
              placeholder="Date range (e.g., 24/11/2013 - 30/05/2024)"
              class="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      <!-- Strategy Cards -->
      <div v-if="filteredFavorites.length === 0" class="text-center py-12">
        <div class="w-24 h-24 mx-auto mb-6 bg-slate-700 rounded-full flex items-center justify-center">
          <svg class="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-white mb-2">No Saved Strategies</h3>
        <p class="text-slate-400 mb-6">Start by creating and saving your first strategy</p>
        <router-link 
          to="/new-strategy" 
          class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Create New Strategy
        </router-link>
      </div>

      <div v-else class="space-y-6">
        <div v-for="strategy in filteredFavorites" :key="strategy.id" class="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <!-- Strategy Card Header -->
          <div 
            class="p-6 cursor-pointer hover:bg-slate-700/50 transition-colors duration-200"
            @click="toggleStrategy(strategy.id)"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-semibold text-white">{{ strategy.customName || 'Unnamed Strategy' }}</h3>
                  <span class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">{{ strategy.dateAdded }}</span>
                </div>
                <p class="text-slate-400 text-sm font-mono mb-3">{{ strategy.strategyText }}</p>
                <div class="flex flex-wrap gap-4 text-sm">
                  <div class="flex items-center space-x-2">
                    <span class="text-slate-400">Return:</span>
                    <span :class="strategy.avgReturn >= 0 ? 'text-green-400' : 'text-red-400'">
                      {{ (strategy.avgReturn * 100).toFixed(2) }}%
                    </span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-slate-400">Sharpe:</span>
                    <span :class="strategy.sharpe >= 0 ? 'text-green-400' : 'text-red-400'">
                      {{ strategy.sharpe.toFixed(2) }}
                    </span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-slate-400">Win Rate:</span>
                    <span class="text-white">{{ (strategy.winRate * 100).toFixed(1) }}%</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="text-slate-400">Signals:</span>
                    <span class="text-white">{{ strategy.totalSignals.toLocaleString() }}</span>
                  </div>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click.stop="editStrategy(strategy)"
                  class="p-2 text-slate-400 hover:text-white hover:bg-slate-600 rounded-lg transition-colors duration-200"
                  title="Edit Strategy"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
                <button
                  @click.stop="removeStrategy(strategy.id)"
                  class="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-600 rounded-lg transition-colors duration-200"
                  title="Remove Strategy"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                  </svg>
                </button>
                <svg 
                  class="w-6 h-6 text-slate-400 transition-transform duration-200"
                  :class="{ 'rotate-180': expandedStrategies.includes(strategy.id) }"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                </svg>
              </div>
            </div>
          </div>

          <!-- Expanded Strategy Details -->
          <div v-if="expandedStrategies.includes(strategy.id)" class="border-t border-slate-700">
            <StrategyDetails :strategy="strategy" />
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Strategy Modal -->
    <div v-if="editingStrategy" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-slate-800 rounded-xl border border-slate-700 p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold text-white mb-4">Edit Strategy</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Custom Name</label>
            <input
              v-model="editingStrategy.customName"
              type="text"
              class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-300 mb-2">Notes</label>
            <textarea
              v-model="editingStrategy.notes"
              rows="3"
              class="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="editingStrategy = null"
            class="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="saveStrategyEdit"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import StrategyDetails from '../components/StrategyDetails.vue'

export default {
  name: 'History',
  components: {
    StrategyDetails
  },
  setup() {
    const favorites = ref([])
    const expandedStrategies = ref([])
    const searchQuery = ref('')
    const sortBy = ref('date')
    const dateRange = ref('')
    const editingStrategy = ref(null)

    const filteredFavorites = computed(() => {
      let filtered = [...favorites.value]

      // Search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(strategy => 
          strategy.strategyText.toLowerCase().includes(query) ||
          (strategy.customName && strategy.customName.toLowerCase().includes(query)) ||
          (strategy.notes && strategy.notes.toLowerCase().includes(query))
        )
      }

      // Sort
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'name':
            return (a.customName || 'Unnamed Strategy').localeCompare(b.customName || 'Unnamed Strategy')
          case 'avg_return':
            return b.avgReturn - a.avgReturn
          case 'sharpe':
            return b.sharpe - a.sharpe
          case 'win_rate':
            return b.winRate - a.winRate
          case 'total_signals':
            return b.totalSignals - a.totalSignals
          case 'date':
          default:
            return new Date(b.dateAdded) - new Date(a.dateAdded)
        }
      })

      return filtered
    })

    const toggleStrategy = (strategyId) => {
      const index = expandedStrategies.value.indexOf(strategyId)
      if (index > -1) {
        expandedStrategies.value.splice(index, 1)
      } else {
        expandedStrategies.value.push(strategyId)
      }
    }

    const editStrategy = (strategy) => {
      editingStrategy.value = { ...strategy }
    }

    const saveStrategyEdit = () => {
      if (editingStrategy.value) {
        const index = favorites.value.findIndex(s => s.id === editingStrategy.value.id)
        if (index > -1) {
          favorites.value[index] = { ...editingStrategy.value }
          saveFavorites()
        }
        editingStrategy.value = null
      }
    }

    const removeStrategy = (strategyId) => {
      if (confirm('Are you sure you want to remove this strategy?')) {
        favorites.value = favorites.value.filter(s => s.id !== strategyId)
        expandedStrategies.value = expandedStrategies.value.filter(id => id !== strategyId)
        saveFavorites()
      }
    }

    const loadFavorites = () => {
      try {
        const stored = localStorage.getItem('alpha_strategy_favorites')
        if (stored) {
          favorites.value = JSON.parse(stored)
        }
      } catch (error) {
        console.error('Error loading favorites:', error)
        favorites.value = []
      }
    }

    const saveFavorites = () => {
      try {
        localStorage.setItem('alpha_strategy_favorites', JSON.stringify(favorites.value))
      } catch (error) {
        console.error('Error saving favorites:', error)
      }
    }

    onMounted(() => {
      loadFavorites()
    })

    return {
      favorites,
      expandedStrategies,
      searchQuery,
      sortBy,
      dateRange,
      editingStrategy,
      filteredFavorites,
      toggleStrategy,
      editStrategy,
      saveStrategyEdit,
      removeStrategy
    }
  }
}
</script>

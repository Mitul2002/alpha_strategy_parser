<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <!-- Hero Section -->
    <div class="max-w-7xl mx-auto px-6 py-12">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-white mb-6">
          Alpha Strategy Parser
        </h1>
        <p class="text-xl text-slate-300 mb-8 max-w-3xl mx-auto">
          Analyze trading strategies across 2,050+ stocks with comprehensive metrics, 
          performance analytics, and detailed trade-by-trade insights.
        </p>
        <div class="flex justify-center space-x-4">
          <router-link 
            to="/new-strategy" 
            class="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2 shadow-lg"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            <span>Create New Strategy</span>
          </router-link>
          
          <router-link 
            to="/history" 
            class="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-all duration-200 flex items-center space-x-2"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>View History</span>
            <span v-if="favoritesCount > 0" class="bg-blue-600 text-white text-sm px-2 py-1 rounded-full">{{ favoritesCount }}</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'Dashboard',
  setup() {
    const favorites = ref([])

    const favoritesCount = computed(() => favorites.value.length)

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

    const onFavoritesUpdated = () => {
      loadFavorites()
    }

    onMounted(() => {
      loadFavorites()
      window.addEventListener('favorites-updated', onFavoritesUpdated)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('favorites-updated', onFavoritesUpdated)
    })

    return {
      favoritesCount
    }
  }
}
</script>

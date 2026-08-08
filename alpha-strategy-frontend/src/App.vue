<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <!-- Navigation Header -->
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
          
          <!-- Navigation Menu -->
          <nav class="flex items-center space-x-6">
            <router-link 
              to="/" 
              class="px-4 py-2 rounded-lg transition-colors duration-200"
              :class="$route.path === '/' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700 hover:text-white'"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
            </svg>
                <span>Dashboard</span>
              </div>
            </router-link>
            
            <router-link 
              to="/history" 
              class="px-4 py-2 rounded-lg transition-colors duration-200"
              :class="$route.path === '/history' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700 hover:text-white'"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>History</span>
                <span v-if="favoritesCount > 0" class="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">{{ favoritesCount }}</span>
              </div>
            </router-link>
            
            <router-link 
              to="/new-strategy" 
              class="px-4 py-2 rounded-lg transition-colors duration-200"
              :class="$route.path === '/new-strategy' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700 hover:text-white'"
            >
              <div class="flex items-center space-x-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                <span>New Strategy</span>
              </div>
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
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
      favoritesCount,
      favorites
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

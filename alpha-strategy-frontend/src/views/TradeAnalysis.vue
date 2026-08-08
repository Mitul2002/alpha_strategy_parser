<template>
  <div class="min-h-screen bg-slate-900 text-slate-100">
    <div class="max-w-7xl mx-auto px-6 py-6">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-2xl font-bold">Chart - {{ symbol }}</h1>
        <router-link to="/new-strategy" class="text-blue-400 hover:underline">Back</router-link>
      </div>
      <TradingChart
        :symbol="symbol"
        :indicators="indicatorFlags"
        :lookahead-periods="lookaheadPeriods"
      />
    </div>
  </div>
</template>

<script>
import TradingChart from '../components/TradingChart.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

export default {
  name: 'TradeAnalysis',
  components: { TradingChart },
  setup() {
    const route = useRoute()
    const symbol = computed(() => route.params.symbol)
    const lookaheadPeriods = computed(() => {
      const q = route.query.periods
      if (!q) return [7, 22, 45, 60]
      try {
        return JSON.parse(q)
      } catch {
        return [7, 22, 45, 60]
      }
    })
    const indicatorFlags = computed(() => {
      const flags = route.query.indicators
      if (!flags) return {}
      try { return JSON.parse(flags) } catch { return {} }
    })
    return { symbol, lookaheadPeriods, indicatorFlags }
  }
}
</script> 
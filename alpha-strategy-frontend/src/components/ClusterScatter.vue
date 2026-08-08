<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <div class="text-sm text-slate-300">{{ xLabel }} vs {{ yLabel }}</div>
      <div class="flex items-center space-x-2 text-xs">
        <div v-for="c in legend" :key="c.id" class="flex items-center space-x-1">
          <span :style="{ background: c.color }" class="inline-block w-3 h-3 rounded"></span>
          <span class="text-slate-400">C{{ c.id }}</span>
        </div>
      </div>
    </div>
    <div ref="container" class="bg-slate-900/60 border border-slate-700 rounded-lg p-3 overflow-hidden">
      <svg :width="width" :height="height">
        <!-- axes -->
        <line :x1="m" :y1="height-m" :x2="width-m" :y2="height-m" stroke="#334155" stroke-width="1" />
        <line :x1="m" :y1="m" :x2="m" :y2="height-m" stroke="#334155" stroke-width="1" />
        <!-- ticks -->
        <g v-for="(t, i) in xTicks" :key="'xt'+i">
          <line :x1="xScale(t)" :y1="height-m" :x2="xScale(t)" :y2="height-m+4" stroke="#475569" />
          <text :x="xScale(t)" :y="height-m+16" text-anchor="middle" fill="#94a3b8" font-size="10">{{ formatNumber(t) }}</text>
        </g>
        <g v-for="(t, i) in yTicks" :key="'yt'+i">
          <line :x1="m-4" :y1="yScale(t)" :x2="m" :y2="yScale(t)" stroke="#475569" />
          <text :x="m-8" :y="yScale(t)+3" text-anchor="end" fill="#94a3b8" font-size="10">{{ formatNumber(t) }}</text>
        </g>
        <!-- points -->
        <g v-for="(p, i) in points" :key="i">
          <circle :cx="xScale(p.x)" :cy="yScale(p.y)" r="3" :fill="clusterColor(p.cluster)" fill-opacity="0.9">
            <title>{{ p.symbol }}\n{{ xLabel }}: {{ p.x.toFixed(3) }}\n{{ yLabel }}: {{ p.y.toFixed(3) }}\nCluster: C{{ p.cluster }}</title>
          </circle>
        </g>
      </svg>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ClusterScatter',
  props: {
    points: { type: Array, default: () => [] },
    xLabel: { type: String, default: 'X' },
    yLabel: { type: String, default: 'Y' },
    width: { type: Number, default: 800 },
    height: { type: Number, default: 360 },
    clusters: { type: Number, default: 0 }
  },
  data() {
    return {
      m: 36,
      palette: ['#22c55e', '#60a5fa', '#f472b6', '#f59e0b', '#ef4444', '#a78bfa', '#34d399', '#f87171', '#93c5fd', '#fb923c']
    }
  },
  computed: {
    xDomain() {
      const xs = this.points.map(p => p.x)
      const min = Math.min(...xs)
      const max = Math.max(...xs)
      const pad = (max - min) * 0.05 || 1
      return [min - pad, max + pad]
    },
    yDomain() {
      const ys = this.points.map(p => p.y)
      const min = Math.min(...ys)
      const max = Math.max(...ys)
      const pad = (max - min) * 0.05 || 1
      return [min - pad, max + pad]
    },
    xTicks() {
      return this.linspace(this.xDomain[0], this.xDomain[1], 5)
    },
    yTicks() {
      return this.linspace(this.yDomain[0], this.yDomain[1], 5)
    },
    legend() {
      const n = Math.min(this.clusters || 0, this.palette.length)
      return Array.from({ length: n }, (_, i) => ({ id: i + 1, color: this.palette[i % this.palette.length] }))
    }
  },
  methods: {
    xScale(v) {
      const [min, max] = this.xDomain
      return this.m + (v - min) * (this.width - 2 * this.m) / (max - min || 1)
    },
    yScale(v) {
      const [min, max] = this.yDomain
      // SVG y increases downward, invert
      return this.height - this.m - (v - min) * (this.height - 2 * this.m) / (max - min || 1)
    },
    clusterColor(id) { return this.palette[(id - 1) % this.palette.length] },
    linspace(a, b, n) {
      const step = (b - a) / (n - 1 || 1)
      return Array.from({ length: n }, (_, i) => a + i * step)
    },
    formatNumber(v) {
      const av = Math.abs(v)
      if (av >= 1) return v.toFixed(2)
      if (av >= 0.01) return v.toFixed(3)
      return v.toExponential(2)
    }
  }
}
</script>

<style scoped>
</style> 
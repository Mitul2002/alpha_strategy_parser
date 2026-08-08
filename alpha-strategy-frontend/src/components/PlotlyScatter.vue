<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <div class="text-sm text-slate-300">{{ xLabel }} vs {{ yLabel }}</div>
      <div class="text-xs text-slate-400">Interactive scatter (zoom, pan, hover)</div>
    </div>
    <div ref="container" class="bg-slate-900/60 border border-slate-700 rounded-lg p-2">
      <div ref="plot" :style="{ width: '100%', height: height + 'px' }"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlotlyScatter',
  props: {
    points: { type: Array, default: () => [] },
    xLabel: { type: String, default: 'X' },
    yLabel: { type: String, default: 'Y' },
    height: { type: Number, default: 380 },
    clusters: { type: Number, default: 0 }
  },
  data() {
    return {
      plotlyLoaded: false,
      palette: ['#22c55e', '#60a5fa', '#f472b6', '#f59e0b', '#ef4444', '#a78bfa', '#34d399', '#f87171', '#93c5fd', '#fb923c']
    }
  },
  watch: {
    points: {
      handler() { this.renderPlot() },
      deep: true
    },
    height() { this.renderPlot() },
    clusters() { this.renderPlot() }
  },
  mounted() {
    this.ensurePlotly().then(() => this.renderPlot())
    window.addEventListener('resize', this.resize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.resize)
  },
  methods: {
    async ensurePlotly() {
      if (window.Plotly) { this.plotlyLoaded = true; return }
      await new Promise((resolve, reject) => {
        const s = document.createElement('script')
        s.src = 'https://cdn.plot.ly/plotly-2.30.0.min.js'
        s.async = true
        s.onload = () => { this.plotlyLoaded = true; resolve() }
        s.onerror = reject
        document.head.appendChild(s)
      })
    },
    resize() { if (this.$refs.plot && window.Plotly) window.Plotly.Plots.resize(this.$refs.plot) },
    renderPlot() {
      if (!this.plotlyLoaded || !this.$refs.plot) return
      const groups = new Map()
      for (const p of this.points) {
        const cid = p.cluster || 1
        if (!groups.has(cid)) groups.set(cid, { x: [], y: [], text: [], name: 'C' + cid, marker: { color: this.palette[(cid-1)%this.palette.length], size: 6, opacity: 0.9 }, mode: 'markers', type: 'scattergl' })
        const g = groups.get(cid)
        g.x.push(p.x)
        g.y.push(p.y)
        g.text.push(`${p.symbol}<br>${this.xLabel}: ${p.x.toFixed(3)}<br>${this.yLabel}: ${p.y.toFixed(3)}<br>Cluster: C${cid}`)
      }
      const data = Array.from(groups.values())
      const layout = {
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#ffffff',
        margin: { l: 60, r: 20, t: 20, b: 50 },
        xaxis: { title: this.xLabel, color: '#0f172a', gridcolor: '#e5e7eb', zerolinecolor: '#94a3b8' },
        yaxis: { title: this.yLabel, color: '#0f172a', gridcolor: '#e5e7eb', zerolinecolor: '#94a3b8' },
        legend: { font: { color: '#0f172a' } },
        hovermode: 'closest',
        autosize: true,
        height: this.height
      }
      const config = { responsive: true, displaylogo: false, modeBarButtonsToRemove: ['select2d','lasso2d'] }
      window.Plotly.newPlot(this.$refs.plot, data, layout, config)
    }
  }
}
</script>

<style scoped>
</style> 
<template>
  <div class="trading-chart-container">
    
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="text-gray-500">Loading chart...</div>
    </div>
    
    <div v-else-if="error" class="flex items-center justify-center h-64">
      <div class="text-red-500">{{ error }}</div>
    </div>
    
    <div v-else class="space-y-4">
      

      <!-- Main Chart -->
      <div ref="chartContainer" class="w-full border rounded-lg" :style="{ height: chartHeight + 'px' }"></div>
      
      <!-- Legend -->
      <div class="p-4 bg-gray-50 rounded-lg">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div class="space-y-1">
            <div class="font-medium text-gray-700">OHLC</div>
            <div>Open: <span class="font-mono">{{ legendData.open || '-' }}</span></div>
            <div>High: <span class="font-mono">{{ legendData.high || '-' }}</span></div>
            <div>Low: <span class="font-mono">{{ legendData.low || '-' }}</span></div>
            <div>Close: <span class="font-mono">{{ legendData.close || '-' }}</span></div>
          </div>
          <div class="space-y-1">
            <div class="font-medium text-gray-700">EMA(20)</div>
            <div>Value: <span class="font-mono">{{ legendData.ema || '-' }}</span></div>
          </div>
          <div v-if="showRSI" class="space-y-1">
            <div class="font-medium text-gray-700">RSI(14)</div>
            <div>Value: <span class="font-mono">{{ legendData.rsi || '-' }}</span></div>
          </div>
          <div v-if="showADX" class="space-y-1">
            <div class="font-medium text-gray-700">ADX(14)</div>
            <div>Value: <span class="font-mono">{{ legendData.adx || '-' }}</span></div>
          </div>
          <div v-if="showATR" class="space-y-1">
            <div class="font-medium text-gray-700">ATR(14)</div>
            <div>Value: <span class="font-mono">{{ legendData.atr || '-' }}</span></div>
          </div>
          <div v-if="showMFI" class="space-y-1">
            <div class="font-medium text-gray-700">MFI(14)</div>
            <div>Value: <span class="font-mono">{{ legendData.mfi || '-' }}</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { createChart, CandlestickSeries, LineSeries, HistogramSeries } from 'lightweight-charts'

export default {
  name: 'TradingChart',
  props: {
    symbol: {
      type: String,
      default: null
    },
    indicators: {
      type: Object,
      default: () => ({})
    },
    lookaheadPeriods: {
      type: Array,
      default: () => [7, 22, 45, 60]
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      symbols: [],
      selectedSymbol: null,
      selectedLookahead: 7,
      showRSI: false,
      showADX: false,
      showATR: false,
      showMFI: false,
      chart: null,
      candlestickSeries: null,
      emaSeries: null,
      rsiSeries: null,
      adxSeries: null,
      atrSeries: null,
      mfiSeries: null,
      volumeSeries: null,
      legendData: {}
    }
  },
  computed: {
    chartHeight() {
      let height = 400
      if (this.showRSI) height += 150
      if (this.showADX) height += 150
      if (this.showATR) height += 150
      if (this.showMFI) height += 150
      return height
    }
  },
  watch: {
    symbol: {
      handler(newSymbol) {
        if (newSymbol && newSymbol !== this.selectedSymbol) {
          this.selectedSymbol = newSymbol
          this.loadChart()
        }
      },
      immediate: true
    }
  },
  async mounted() {
    this.initializeIndicators()
    if (this.lookaheadPeriods.length > 0) {
      this.selectedLookahead = this.lookaheadPeriods[0]
    }
    if (this.symbol) {
      this.selectedSymbol = this.symbol
      await this.loadChart()
    }
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.remove()
    }
  },
  methods: {
    async loadSymbols() {
      try {
        const response = await fetch('http://localhost:8000/symbols')
        const data = await response.json()
        if (data.ok && Array.isArray(data.results)) {
          this.symbols = data.results.slice(0, 50)
          if (this.symbols.length > 0 && !this.selectedSymbol) {
            this.selectedSymbol = this.symbols[0]
          }
        }
      } catch (error) {
        console.error('Failed to load symbols:', error)
        this.symbols = ['HDFCBANK', 'ICICIBANK', 'BHARTIARTL', 'RELIANCE', 'HDFC']
        if (!this.selectedSymbol) {
          this.selectedSymbol = this.symbols[0]
        }
      }
    },
    
    initializeIndicators() {
      if (this.indicators.rsi) this.showRSI = true
      if (this.indicators.adx) this.showADX = true
      if (this.indicators.atr) this.showATR = true
      if (this.indicators.mfi) this.showMFI = true
    },
    
    async loadChart() {
    // Prevent multiple simultaneous loads
    if (this.loading) return
    this.loading = true
      this.error = null
      
      try {
        const response = await fetch(`http://localhost:8000/ohlcv/${encodeURIComponent(this.selectedSymbol)}`)
        const data = await response.json()
        
        if (!data.ok) {
          throw new Error(data.error || 'Failed to load chart data')
        }
        
        const ohlcvData = data.results
        if (!ohlcvData || !ohlcvData.time || ohlcvData.time.length === 0) {
          throw new Error("No data available for this symbol")
        }
        
        // Convert API response to chart format
        const chartData = ohlcvData.time.map((time, index) => ({
          time: time,
          open: ohlcvData.open[index] || 0,
          high: ohlcvData.high[index] || 0,
          low: ohlcvData.low[index] || 0,
          close: ohlcvData.close[index] || 0,
          volume: ohlcvData.volume[index] || 0
        }))
        
        this.createChart(chartData)
        
      } catch (error) {
        console.error('Chart loading error:', error)
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    
    createChart(ohlcvData) {
    // Clean up existing chart
      if (this.chart) {
        this.chart.remove()
      }
      
      const container = this.$refs.chartContainer
      if (!container) return
      
      const width = container.clientWidth || container.getBoundingClientRect().width || 800
      console.log('[TradingChart] container width:', width, 'data len:', ohlcvData.length)

      // Normalize time to YYYY-MM-DD strings (already the case) to avoid blanks
      // Convert to UTCTimestamp (seconds) which the chart API accepts reliably
      const normalized = ohlcvData.map(d => ({
        time: typeof d.time === 'number' ? d.time : Math.floor(new Date(d.time).getTime() / 1000),
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
        volume: d.volume,
      }))
      
      // Create main chart
      this.chart = createChart(container, {
        autoSize: true,
        height: this.chartHeight,
        layout: {
          background: { type: 'solid', color: '#0f172a' },
          textColor: '#cbd5e1',
        },
        grid: {
          vertLines: { color: '#334155' },
          horzLines: { color: '#334155' },
        },
        crosshair: {
          mode: 1,
        },
        rightPriceScale: {
          borderColor: '#334155',
        },
        timeScale: {
          borderColor: '#334155',
        },
      })
      
      // Add candlestick series (v5: addSeries then setData)
      this.candlestickSeries = this.chart.addSeries(CandlestickSeries, {
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      })
      this.candlestickSeries.setData(normalized.map(d => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
      })))
      console.log('[TradingChart] set candlestick data. first=', normalized[0], 'last=', normalized[normalized.length-1])
      
      // Calculate and add EMA
      const emaData = this.calculateEMA(normalized, 20)
      this.emaSeries = this.chart.addSeries(LineSeries, {
        color: '#ff6b6b',
        lineWidth: 2,
        priceFormat: {
          type: 'price',
          precision: 2,
          minMove: 0.01,
        },
      })
      this.emaSeries.setData(emaData)
      
      // Add volume
      this.volumeSeries = this.chart.addSeries(HistogramSeries, {
        priceFormat: { type: 'volume' },
        priceScaleId: 'volume',
      })
      this.volumeSeries.setData(normalized.map(d => ({
        time: d.time,
        value: d.volume,
        color: d.close >= d.open ? '#26a69a' : '#ef5350'
      })))
      
      // Add indicators in separate panes
      this.addIndicators(normalized)
      
      // Setup crosshair tracking
      this.setupCrosshairTracking(normalized)
      
      // Fit content so data is visible
      this.chart.timeScale().fitContent()
      
      // Handle resize
      window.addEventListener('resize', this.handleResize)
    },
    
    addIndicators(ohlcvData) {
      if (this.showRSI) {
        const rsiData = this.calculateRSI(ohlcvData, 14)
        this.rsiSeries = this.chart.addSeries(LineSeries, {
          color: '#9c27b0',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        })
        this.rsiSeries.setData(rsiData)
      }
      
      if (this.showADX) {
        const adxData = this.calculateADX(ohlcvData, 14)
        this.adxSeries = this.chart.addSeries(LineSeries, {
          color: '#ff9800',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        })
        this.adxSeries.setData(adxData)
      }
      
      if (this.showATR) {
        const atrData = this.calculateATR(ohlcvData, 14)
        this.atrSeries = this.chart.addSeries(LineSeries, {
          color: '#4caf50',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        })
        this.atrSeries.setData(atrData)
      }
      
      if (this.showMFI) {
        const mfiData = this.calculateMFI(ohlcvData, 14)
        this.mfiSeries = this.chart.addSeries(LineSeries, {
          color: '#2196f3',
          lineWidth: 2,
          priceFormat: {
            type: 'price',
            precision: 2,
            minMove: 0.01,
          },
        })
        this.mfiSeries.setData(mfiData)
      }
    },
    
    updateIndicators() {
      if (this.selectedSymbol) {
        this.loadChart()
      }
    },
    
    setupCrosshairTracking(ohlcvData) {
      // Create maps for O(1) lookup
      const dataMap = new Map()
      ohlcvData.forEach(d => {
        dataMap.set(d.time, d)
      })
      
      const emaMap = new Map()
      this.calculateEMA(ohlcvData, 20).forEach(d => {
        emaMap.set(d.time, d.value)
      })
      
      const rsiMap = new Map()
      if (this.showRSI) {
        this.calculateRSI(ohlcvData, 14).forEach(d => {
          rsiMap.set(d.time, d.value)
        })
      }
      
      const adxMap = new Map()
      if (this.showADX) {
        this.calculateADX(ohlcvData, 14).forEach(d => {
          adxMap.set(d.time, d.value)
        })
      }
      
      const atrMap = new Map()
      if (this.showATR) {
        this.calculateATR(ohlcvData, 14).forEach(d => {
          atrMap.set(d.time, d.value)
        })
      }
      
      const mfiMap = new Map()
      if (this.showMFI) {
        this.calculateMFI(ohlcvData, 14).forEach(d => {
          mfiMap.set(d.time, d.value)
        })
      }
      
      this.chart.subscribeCrosshairMove(param => {
        if (param.point === undefined || !param.time || param.point.x < 0 || param.point.y < 0) {
          this.legendData = {}
          return
        }
        
        const data = dataMap.get(param.time)
        if (!data) return
        
        this.legendData = {
          open: data.open?.toFixed(2),
          high: data.high?.toFixed(2),
          low: data.low?.toFixed(2),
          close: data.close?.toFixed(2),
          ema: emaMap.get(param.time)?.toFixed(2),
          rsi: rsiMap.get(param.time)?.toFixed(2),
          adx: adxMap.get(param.time)?.toFixed(2),
          atr: atrMap.get(param.time)?.toFixed(2),
          mfi: mfiMap.get(param.time)?.toFixed(2)
        }
      })
    },
    
    handleResize() {
      if (this.chart && this.$refs.chartContainer) {
        this.chart.applyOptions({
          width: this.$refs.chartContainer.clientWidth,
          height: this.chartHeight
        })
      }
    },
    
    // Technical indicator calculations
    calculateEMA(data, period) {
      const result = []
      let ema = data[0].close
      
      for (let i = 0; i < data.length; i++) {
        if (i === 0) {
          ema = data[i].close
        } else {
          ema = (data[i].close * (2 / (period + 1))) + (ema * (1 - (2 / (period + 1))))
        }
        result.push({ time: data[i].time, value: ema })
      }
      return result
    },
    
    calculateRSI(data, period) {
      const result = []
      let gains = 0
      let losses = 0
      
      for (let i = 1; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close
        if (change > 0) gains += change
        else losses -= change
        
        if (i >= period) {
          const avgGain = gains / period
          const avgLoss = losses / period
          const rs = avgGain / (avgLoss || 0.0001)
          const rsi = 100 - (100 / (1 + rs))
          result.push({ time: data[i].time, value: rsi })
          
          // Remove oldest change
          const oldChange = data[i - period + 1].close - data[i - period].close
          if (oldChange > 0) gains -= oldChange
          else losses += oldChange
        }
      }
      return result
    },
    
    calculateATR(data, period) {
      const result = []
      const trs = []
      
      for (let i = 1; i < data.length; i++) {
        const tr = Math.max(
          data[i].high - data[i].low,
          Math.abs(data[i].high - data[i - 1].close),
          Math.abs(data[i].low - data[i - 1].close)
        )
        trs.push(tr)
        
        if (trs.length >= period) {
          const atr = trs.slice(-period).reduce((a, b) => a + b, 0) / period
          result.push({ time: data[i].time, value: atr })
        }
      }
      return result
    },
    
    calculateADX(data, period) {
      const result = []
      const trs = []
      const plusDMs = []
      const minusDMs = []
      
      for (let i = 1; i < data.length; i++) {
        const tr = Math.max(
          data[i].high - data[i].low,
          Math.abs(data[i].high - data[i - 1].close),
          Math.abs(data[i].low - data[i - 1].close)
        )
        trs.push(tr)
        
        const plusDM = data[i].high - data[i - 1].high > data[i - 1].low - data[i].low 
          ? Math.max(data[i].high - data[i - 1].high, 0) : 0
        const minusDM = data[i - 1].low - data[i].low > data[i].high - data[i - 1].high 
          ? Math.max(data[i - 1].low - data[i].low, 0) : 0
        
        plusDMs.push(plusDM)
        minusDMs.push(minusDM)
        
        if (trs.length >= period) {
          const atr = trs.slice(-period).reduce((a, b) => a + b, 0) / period
          const plusDI = (plusDMs.slice(-period).reduce((a, b) => a + b, 0) / period) / atr * 100
          const minusDI = (minusDMs.slice(-period).reduce((a, b) => a + b, 0) / period) / atr * 100
          const dx = Math.abs(plusDI - minusDI) / (plusDI + minusDI) * 100
          result.push({ time: data[i].time, value: dx })
        }
      }
      return result
    },
    
    calculateMFI(data, period) {
      const result = []
      const typicalPrices = []
      const moneyFlows = []
      
      for (let i = 0; i < data.length; i++) {
        const tp = (data[i].high + data[i].low + data[i].close) / 3
        typicalPrices.push(tp)
        
        if (i > 0) {
          const moneyFlow = tp * data[i].volume
          moneyFlows.push({ moneyFlow, isPositive: tp > typicalPrices[i - 1] })
        }
        
        if (moneyFlows.length >= period) {
          const periodFlows = moneyFlows.slice(-period)
          const positiveFlow = periodFlows.filter(f => f.isPositive).reduce((a, f) => a + f.moneyFlow, 0)
          const negativeFlow = periodFlows.filter(f => !f.isPositive).reduce((a, f) => a + f.moneyFlow, 0)
          const mfi = 100 - (100 / (1 + (positiveFlow / (negativeFlow || 0.0001))))
          result.push({ time: data[i].time, value: mfi })
        }
      }
      return result
    }
  }
}
</script>

<style scoped>
.trading-chart-container {
  @apply w-full;
}
</style>

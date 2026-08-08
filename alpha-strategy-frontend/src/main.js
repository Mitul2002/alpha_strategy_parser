import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import History from './views/History.vue'
import NewStrategy from './views/NewStrategy.vue'
import StrategyAnalyzerTest from './components/StrategyAnalyzerTest.vue'
import './assets/main.css'
import TradeAnalysis from './views/TradeAnalysis.vue'

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard },
    { path: '/history', component: History },
    { path: '/new-strategy', component: NewStrategy },
    { path: '/test-analyzer', component: StrategyAnalyzerTest },
    { path: '/trade-analysis/:symbol', component: TradeAnalysis }
  ]
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')

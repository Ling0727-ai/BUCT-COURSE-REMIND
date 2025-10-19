import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/global.css'
import { initMobileOptimizations } from './utils/mobile-utils'

createApp(App).use(router).mount('#app')
initMobileOptimizations()
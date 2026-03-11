import {createApp} from 'vue'
import App from '@/App.vue'
import router from '@/router/index'
import '@/assets/global.css'
import '@/assets/toast.css'
import '@/assets/task-progress.css'
import {initMobileOptimizations} from '@/utils/mobile-utils'
import {initDesktopEffects} from '@/app/desktop-effects.service'
import {initSessionExpiration} from '@/app/session-expiration.service'
import {taskProgressCanvasService} from './task-progress-canvas.service'

export function bootstrapApp(): void {
    createApp(App).use(router).mount('#app')

    initMobileOptimizations()
    initSessionExpiration()
    initDesktopEffects()
    taskProgressCanvasService.start()

    console.info('[main] 应用入口加载时间:', new Date().toISOString())
    window.__APP_MAIN_LOADED = true
}


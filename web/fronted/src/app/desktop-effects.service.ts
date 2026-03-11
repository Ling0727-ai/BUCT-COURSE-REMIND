import {isDesktop} from '@/utils/mobile-utils'
import {initMouseTrail} from '@/utils/mouse-trail'

export function initDesktopEffects(): void {
    if (!isDesktop()) {
        return
    }

    try {
        const manager = initMouseTrail()
        window.__MOUSE_TRAIL_MANAGER = manager
    } catch (error) {
        console.warn('[mouse-trail] init failed', error)
    }
}


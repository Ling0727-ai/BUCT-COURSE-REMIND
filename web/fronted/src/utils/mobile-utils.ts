// 移动端工具函数

const IOS_ZOOM_MAX_TOUCHES = 1
const DOUBLE_TAP_THRESHOLD_MS = 300
const VIEWPORT_RESIZE_DELAY_MS = 100
const KEYBOARD_SCROLL_DELAY_MS = 300
const TOUCH_FEEDBACK_RESET_MS = 150

const viewportResizeHandler = (): void => {
    setViewportHeight()
}

const orientationChangeHandler = (): void => {
    setTimeout(setViewportHeight, VIEWPORT_RESIZE_DELAY_MS)
}

export const isMobile = (): boolean => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

export const isIOS = (): boolean => {
    return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

export const isAndroid = (): boolean => {
    return /Android/.test(navigator.userAgent)
}

export const getDevicePixelRatio = (): number => {
    return window.devicePixelRatio || 1
}

export const setViewportHeight = (): void => {
    const vh = window.innerHeight * 0.01
    document.documentElement.style.setProperty('--vh', `${vh}px`)
}

export const preventIOSZoom = (): void => {
    if (!isIOS()) {
        return
    }

    document.addEventListener(
        'touchstart',
        (event: TouchEvent) => {
            if (event.touches.length > IOS_ZOOM_MAX_TOUCHES) {
                event.preventDefault()
            }
        },
        {passive: false}
    )

    let lastTouchEnd = 0
    document.addEventListener('touchend', (event: TouchEvent) => {
        const now = Date.now()
        if (now - lastTouchEnd <= DOUBLE_TAP_THRESHOLD_MS) {
            event.preventDefault()
        }
        lastTouchEnd = now
    })
}

export const optimizeMobileScroll = (): void => {
    const scrollElements = document.querySelectorAll<HTMLElement>('.form-section, .illustration-section')
    scrollElements.forEach((element) => {
        element.style.setProperty('-webkit-overflow-scrolling', 'touch')
        element.style.overscrollBehavior = 'contain'
    })
}

export const handleMobileKeyboard = (): void => {
    if (!isMobile()) {
        return
    }

    const inputs = document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement>('input, textarea')

    inputs.forEach((input) => {
        input.addEventListener('focus', () => {
            setTimeout(() => {
                input.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center',
                    inline: 'nearest'
                })
            }, KEYBOARD_SCROLL_DELAY_MS)
        })

        input.addEventListener('blur', () => {
            setTimeout(setViewportHeight, KEYBOARD_SCROLL_DELAY_MS)
        })
    })
}

export const addTouchFeedback = (): void => {
    const touchElements = document.querySelectorAll<HTMLElement>('button, .custom-checkbox, .terms-link')

    touchElements.forEach((element) => {
        element.addEventListener(
            'touchstart',
            () => {
                element.style.opacity = '0.7'
            },
            {passive: true}
        )

        element.addEventListener(
            'touchend',
            () => {
                setTimeout(() => {
                    element.style.opacity = ''
                }, TOUCH_FEEDBACK_RESET_MS)
            },
            {passive: true}
        )

        element.addEventListener(
            'touchcancel',
            () => {
                element.style.opacity = ''
            },
            {passive: true}
        )
    })
}

export const initMobileOptimizations = (): void => {
    if (!isMobile()) {
        return
    }

    setViewportHeight()
    preventIOSZoom()

    window.addEventListener('resize', viewportResizeHandler)
    window.addEventListener('orientationchange', orientationChangeHandler)

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            optimizeMobileScroll()
            handleMobileKeyboard()
            addTouchFeedback()
        })
        return
    }

    optimizeMobileScroll()
    handleMobileKeyboard()
    addTouchFeedback()
}

export const cleanupMobileOptimizations = (): void => {
    window.removeEventListener('resize', viewportResizeHandler)
    window.removeEventListener('orientationchange', orientationChangeHandler)
}

export const isDesktop = (): boolean => {
    return !isMobile()
}


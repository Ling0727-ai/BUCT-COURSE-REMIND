// 移动端工具函数

/**
 * 检测是否为移动设备
 */
export const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

/**
 * 检测是否为iOS设备
 */
export const isIOS = () => {
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
}

/**
 * 检测是否为Android设备
 */
export const isAndroid = () => {
  return /Android/.test(navigator.userAgent)
}

/**
 * 获取设备像素比
 */
export const getDevicePixelRatio = () => {
  return window.devicePixelRatio || 1
}

/**
 * 设置viewport高度变量（解决移动端100vh问题）
 */
export const setViewportHeight = () => {
  const vh = window.innerHeight * 0.01
  document.documentElement.style.setProperty('--vh', `${vh}px`)
}

/**
 * 防止iOS Safari缩放
 */
export const preventIOSZoom = () => {
  if (isIOS()) {
    document.addEventListener('touchstart', (event) => {
      if (event.touches.length > 1) {
        event.preventDefault()
      }
    }, { passive: false })

    let lastTouchEnd = 0
    document.addEventListener('touchend', (event) => {
      const now = (new Date()).getTime()
      if (now - lastTouchEnd <= 300) {
        event.preventDefault()
      }
      lastTouchEnd = now
    }, false)
  }
}

/**
 * 优化移动端滚动
 */
export const optimizeMobileScroll = () => {
  // 为支持的元素添加平滑滚动
  const scrollElements = document.querySelectorAll('.form-section, .illustration-section')
  scrollElements.forEach(element => {
    element.style.webkitOverflowScrolling = 'touch'
    element.style.overscrollBehavior = 'contain'
  })
}

/**
 * 处理移动端键盘弹出
 */
export const handleMobileKeyboard = () => {
  if (isMobile()) {
    const inputs = document.querySelectorAll('input, textarea')
    
    inputs.forEach(input => {
      input.addEventListener('focus', () => {
        // 延迟执行，等待键盘弹出
        setTimeout(() => {
          input.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center',
            inline: 'nearest'
          })
        }, 300)
      })
      
      input.addEventListener('blur', () => {
        // 键盘收起后重新设置viewport高度
        setTimeout(setViewportHeight, 300)
      })
    })
  }
}

/**
 * 添加触摸反馈
 */
export const addTouchFeedback = () => {
  const touchElements = document.querySelectorAll('button, .custom-checkbox, .terms-link')
  
  touchElements.forEach(element => {
    element.addEventListener('touchstart', () => {
      element.style.opacity = '0.7'
    }, { passive: true })
    
    element.addEventListener('touchend', () => {
      setTimeout(() => {
        element.style.opacity = ''
      }, 150)
    }, { passive: true })
    
    element.addEventListener('touchcancel', () => {
      element.style.opacity = ''
    }, { passive: true })
  })
}

/**
 * 初始化移动端优化
 */
export const initMobileOptimizations = () => {
  if (isMobile()) {
    setViewportHeight()
    preventIOSZoom()
    
    // 监听窗口变化
    window.addEventListener('resize', setViewportHeight)
    window.addEventListener('orientationchange', () => {
      setTimeout(setViewportHeight, 100)
    })
    
    // DOM加载完成后执行
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        optimizeMobileScroll()
        handleMobileKeyboard()
        addTouchFeedback()
      })
    } else {
      optimizeMobileScroll()
      handleMobileKeyboard()
      addTouchFeedback()
    }
  }
}

/**
 * 清理移动端优化
 */
export const cleanupMobileOptimizations = () => {
  window.removeEventListener('resize', setViewportHeight)
  window.removeEventListener('orientationchange', setViewportHeight)
}

/**
 * 检测是否为桌面设备
 */
export const isDesktop = () => {
  return !isMobile()
}

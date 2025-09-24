export function useToast() {
  const showToast = (type, title, message) => {
    console.log('显示 Toast:', type, title, message)
    
    const toast = document.createElement('div')
    toast.className = `toast toast-${type}`
    
    // 强制设置样式确保位置正确
    toast.style.cssText = `
      position: fixed !important;
      top: 20px !important;
      left: 50% !important;
      transform: translateX(-50%) translateY(-100%) !important;
      z-index: 999999 !important;
      opacity: 0 !important;
      pointer-events: auto !important;
    `
    
    toast.innerHTML = `
      <div class="toast-icon">
        <i class="fas ${getToastIcon(type)}"></i>
      </div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <div class="toast-progress">
        <div class="toast-progress-bar toast-progress-${type}"></div>
      </div>
    `
    
    // 点击整个 Toast 关闭
    toast.addEventListener('click', () => {
      console.log('Toast 被点击，准备关闭')
      toast.style.transform = 'translateX(-50%) translateY(-100%)'
      toast.style.opacity = '0'
      setTimeout(() => {
        if (document.body.contains(toast)) {
          document.body.removeChild(toast)
          console.log('Toast 已移除')
        }
      }, 300)
    })
    
    document.body.appendChild(toast)
    console.log('Toast 已添加到 body')
    
    // 显示动画
    setTimeout(() => {
      toast.style.transform = 'translateX(-50%) translateY(0)'
      toast.style.opacity = '1'
      toast.classList.add('show')
      console.log('Toast 显示动画已启动')
      
      // 启动进度条动画
      const progressBar = toast.querySelector('.toast-progress-bar')
      if (progressBar) {
        progressBar.style.animation = 'toast-progress 3s linear forwards'
      }
    }, 100)
    
    // 自动移除
    setTimeout(() => {
      if (document.body.contains(toast)) {
        console.log('Toast 自动关闭')
        toast.style.transform = 'translateX(-50%) translateY(-100%)'
        toast.style.opacity = '0'
        setTimeout(() => {
          if (document.body.contains(toast)) {
            document.body.removeChild(toast)
            console.log('Toast 自动移除完成')
          }
        }, 300)
      }
    }, 3000)
  }

  const getToastIcon = (type) => {
    const icons = {
      success: 'fa-check-circle',
      error: 'fa-exclamation-circle',
      warning: 'fa-exclamation-triangle',
      info: 'fa-info-circle'
    }
    return icons[type] || 'fa-info-circle'
  }

  return {
    showToast
  }
}
<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
@import './assets/global.css';
@import './assets/mobile-fixes.css';

/* 应用级别的样式 */
#app {
  min-height: 100vh;
  font-family: 'Inter', 'SF Pro Display', 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
}

/* 路由过渡动画 */
.router-enter-active,
.router-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.router-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.router-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 全局按钮样式重置 */
button {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  margin: 0;
}

/* 全局输入框样式重置 */
input,
textarea,
select {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
}

/* 全局链接样式 */
a {
  color: var(--primary-color);
  text-decoration: none;
  transition: var(--transition-normal);
}

a:hover {
  color: var(--primary-dark);
}

/* 全局表单元素样式 */
input:disabled,
textarea:disabled,
select:disabled,
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 全局图片样式 */
img {
  max-width: 100%;
  height: auto;
}

/* 全局列表样式重置 */
ul,
ol {
  list-style: none;
}

/* 全局表格样式 */
table {
  border-collapse: collapse;
  border-spacing: 0;
}

/* 全局代码样式 */
code,
pre {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Consolas', 'Courier New', monospace;
}
</style>
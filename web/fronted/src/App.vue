<template>
  <div class="app-bg">
    <!-- 自定义背景层 -->
    <div
      v-if="settings.enabled && mediaUrl"
      class="custom-bg"
      :style="{ opacity: settings.bgOpacity }"
    >
      <img
        v-if="mediaType !== 'video'"
        :src="mediaUrl"
        alt="custom background"
      />
      <video
        v-else
        :src="mediaUrl"
        autoplay
        loop
        muted
        playsinline
      />
    </div>

    <!-- 动态光晕 -->
    <div class="bg-blob bg-blob-1"></div>
    <div class="bg-blob bg-blob-2"></div>
    <div class="bg-blob bg-blob-3"></div>

    <router-view />
  </div>
</template>

<script>
import { useBackground } from '@/composables/useBackground'

export default {
  name: 'App',
  setup() {
    const { settings, mediaUrl, mediaType } = useBackground()
    return { settings, mediaUrl, mediaType }
  }
}
</script>

<style>
@import './assets/global.css';
@import './assets/mobile-fixes.css';

#app {
  min-height: 100vh;
}

.app-bg {
  min-height: 100vh;
}

/* 自定义背景层 */
.custom-bg {
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  overflow: hidden;
}

.custom-bg img,
.custom-bg video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 动态渐变光晕 */
.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  will-change: transform;
  z-index: -1;
}

.bg-blob-1 {
  width: 500px;
  height: 500px;
  background: rgba(59, 130, 246, 0.1);
  top: -120px;
  right: -80px;
  animation: blobFloat1 25s ease-in-out infinite;
}

.bg-blob-2 {
  width: 400px;
  height: 400px;
  background: rgba(139, 92, 246, 0.08);
  bottom: -100px;
  left: -60px;
  animation: blobFloat2 30s ease-in-out infinite;
}

.bg-blob-3 {
  width: 350px;
  height: 350px;
  background: rgba(34, 197, 94, 0.06);
  top: 50%;
  right: 15%;
  animation: blobFloat3 20s ease-in-out infinite;
}

@keyframes blobFloat1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -30px) scale(1.05); }
  66% { transform: translate(-20px, 40px) scale(0.95); }
}

@keyframes blobFloat2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-30px, -20px) scale(1.05); }
  66% { transform: translate(20px, 30px) scale(0.95); }
}

@keyframes blobFloat3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, 20px) scale(1.08); }
}

/* 路由过渡 */
.router-enter-active,
.router-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.router-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.router-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .bg-blob {
    animation: none !important;
  }
}
</style>

<template>
  <div class="app-bg" :class="`preset-${settings.preset}`">
    <!-- 自定义背景层 -->
    <div
      v-if="settings.preset === 'custom' && mediaUrl"
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

    <!-- 动态光晕 - 浅色模式更柔和，深色模式更鲜艳 -->
    <div
      v-if="settings.preset !== 'none' && settings.preset !== 'custom'"
      class="bg-blobs"
    >
      <div class="bg-blob bg-blob-1"></div>
      <div class="bg-blob bg-blob-2"></div>
      <div class="bg-blob bg-blob-3"></div>
    </div>

    <router-view />

    <ToastHost />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useBackground } from '@/composables/useBackground'
import ToastHost from '@/components/ToastHost.vue'

export default defineComponent({
  name: 'App',
  components: { ToastHost },
  setup() {
    const { settings, mediaUrl, mediaType } = useBackground()
    return { settings, mediaUrl, mediaType }
  }
})
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

/* ─── 自定义背景层 ─── */
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

/* ─── 动态渐变光晕 ─── */
.bg-blobs {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  overflow: hidden;
}

.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  will-change: transform;
  z-index: -1;
}

/* ─── 浅色模式光晕（柔和淡雅） ─── */
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

/* ─── 深色模式光晕（深邃鲜艳） ─── */
.preset-dark .bg-blob-1 {
  width: 600px;
  height: 600px;
  background: rgba(59, 130, 246, 0.18);
  top: -150px;
  right: -100px;
}

.preset-dark .bg-blob-2 {
  width: 500px;
  height: 500px;
  background: rgba(139, 92, 246, 0.15);
  bottom: -120px;
  left: -80px;
}

.preset-dark .bg-blob-3 {
  width: 450px;
  height: 450px;
  background: rgba(14, 165, 233, 0.12);
  top: 40%;
  right: 10%;
}

/* ─── 动画 ─── */
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

/* ─── 路由过渡 ─── */
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

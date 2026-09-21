<template>
  <Teleport to="body">
    <div class="toast-region" aria-live="polite" aria-atomic="false">
      <TransitionGroup name="toast" tag="div" class="toast-stack">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="`toast-${toast.type}`"
          :role="toast.type === 'error' ? 'alert' : 'status'"
          @mouseenter="pause(toast.id)"
          @mouseleave="resume(toast.id)"
          @focusin="pause(toast.id)"
          @focusout="resume(toast.id)"
        >
          <i class="toast-icon fas" :class="iconFor(toast.type)" aria-hidden="true"></i>

          <div class="toast-content">
            <p class="toast-title">{{ toast.title }}</p>
            <p v-if="toast.message" class="toast-message">{{ toast.message }}</p>
            <button
              v-if="toast.action"
              type="button"
              class="toast-action"
              @click="runAction(toast)"
            >
              {{ toast.action.label }}
            </button>
          </div>

          <button type="button" class="toast-close" aria-label="关闭提示" @click="dismiss(toast.id)">
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>

          <span
            v-if="toast.duration > 0"
            class="toast-progress"
            :class="`toast-progress-${toast.type}`"
            :style="{ animationDuration: `${toast.duration}ms` }"
            aria-hidden="true"
          ></span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useToast, type ToastItem, type ToastType } from '@/composables/useToast'

const ICONS: Record<ToastType, string> = {
  success: 'fa-check-circle',
  error: 'fa-times-circle',
  info: 'fa-info-circle',
  warning: 'fa-exclamation-triangle'
}

export default defineComponent({
  name: 'ToastHost',
  setup() {
    const { toasts, dismiss, pause, resume } = useToast()

    const iconFor = (type: ToastType): string => ICONS[type] ?? ICONS.info

    const runAction = (toast: ToastItem) => {
      toast.action?.handler()
      dismiss(toast.id)
    }

    return { toasts, dismiss, pause, resume, iconFor, runAction }
  }
})
</script>

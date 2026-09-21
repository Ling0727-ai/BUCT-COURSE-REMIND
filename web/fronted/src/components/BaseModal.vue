<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        ref="overlayEl"
        class="modal-overlay"
        :style="{ '--modal-z': zIndex, '--modal-width': width }"
        @click="handleOverlayClick"
      >
        <div
          ref="contentEl"
          class="modal-content"
          :class="[panelClass, `modal-tone-${tone}`]"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="title ? titleId : undefined"
          :aria-label="title ? undefined : ariaLabel"
          tabindex="-1"
        >
          <div class="modal-header">
            <h3 v-if="title" :id="titleId" class="modal-title">
              <i v-if="icon" :class="icon" aria-hidden="true"></i>
              {{ title }}
            </h3>
            <slot name="header" />
            <button
              v-if="closable"
              type="button"
              class="modal-close"
              :aria-label="closeLabel"
              @click="requestClose"
            >
              <i class="fas fa-times" aria-hidden="true"></i>
            </button>
          </div>

          <div class="modal-body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script lang="ts">
import { computed, defineComponent, ref, toRef } from 'vue'
import { useModal } from '@/composables/useModal'

export default defineComponent({
  name: 'BaseModal',
  props: {
    modelValue: { type: Boolean, default: false },
    /** 标题文本；留空则使用 header 插槽并依赖 ariaLabel 提供可访问名称。 */
    title: { type: String, default: '' },
    icon: { type: String, default: '' },
    /** 无标题时的可访问名称。 */
    ariaLabel: { type: String, default: '' },
    /** CSS 宽度值，例如 '480px'。 */
    width: { type: String, default: '600px' },
    closable: { type: Boolean, default: true },
    /** 点击遮罩是否关闭。 */
    closeOnOverlay: { type: Boolean, default: true },
    panelClass: { type: String, default: '' },
    /** 标题图标配色，对应 modal.css 中的 .modal-tone-* */
    tone: {
      type: String as () => 'primary' | 'danger' | 'warning' | 'success',
      default: 'primary'
    },
    closeLabel: { type: String, default: '关闭弹窗' }
  },
  emits: ['update:modelValue', 'close'],
  setup(props, { emit }) {
    const overlayEl = ref<HTMLElement | null>(null)
    const contentEl = ref<HTMLElement | null>(null)

    const requestClose = () => {
      emit('update:modelValue', false)
      emit('close')
    }

    const handleOverlayClick = (event: MouseEvent) => {
      if (event.target !== overlayEl.value) {
        return
      }
      if (props.closeOnOverlay && props.closable) {
        requestClose()
      }
    }

    const { titleId, zIndex } = useModal({
      open: toRef(props, 'modelValue'),
      overlay: overlayEl,
      content: contentEl,
      onClose: requestClose,
      closable: computed(() => props.closable)
    })

    return { overlayEl, contentEl, titleId, zIndex, requestClose, handleOverlayClick }
  }
})
</script>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: Boolean,
  busy: Boolean,
  error: { type: String, default: '' },
})
const emit = defineEmits(['close', 'confirm'])
const password = ref('')

watch(
  () => props.open,
  (open) => {
    if (open) password.value = ''
  },
)

function submit() {
  if (password.value.length >= 4) emit('confirm', password.value)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click.self="emit('close')">
      <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="password-title">
        <button class="icon-button modal-close" type="button" aria-label="닫기" @click="emit('close')">×</button>
        <p class="eyebrow">작성자 확인</p>
        <h2 id="password-title">수정용 비밀번호를 입력해 주세요</h2>
        <p class="muted">글을 작성할 때 설정한 4~20자의 비밀번호입니다.</p>
        <form @submit.prevent="submit">
          <label for="post-password">비밀번호</label>
          <input
            id="post-password"
            v-model="password"
            type="password"
            minlength="4"
            maxlength="20"
            autocomplete="current-password"
            required
            autofocus
          />
          <p v-if="error" class="form-error">{{ error }}</p>
          <div class="modal-actions">
            <button class="button button-secondary" type="button" @click="emit('close')">취소</button>
            <button class="button button-danger" type="submit" :disabled="busy || password.length < 4">
              {{ busy ? '확인 중...' : '확인' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </Teleport>
</template>


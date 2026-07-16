<script setup>
import { nextTick, onMounted, ref } from 'vue'

import { chatApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import { REGIONS } from '../constants/categories'

const STORAGE_KEY = 'localhub-chat-history'
const open = ref(false)
const input = ref('')
const busy = ref(false)
const selectedRegion = ref('')
const messages = ref([])
const messageList = ref(null)

onMounted(() => {
  try {
    messages.value = JSON.parse(sessionStorage.getItem(STORAGE_KEY)) || []
  } catch {
    messages.value = []
  }
  if (!messages.value.length) {
    messages.value.push({
      role: 'assistant',
      content: '안녕하세요! 전국 곳곳의 여행 정보와 이웃 게시글을 찾아드릴게요.',
    })
  }
})

async function scrollToBottom() {
  await nextTick()
  if (messageList.value) messageList.value.scrollTop = messageList.value.scrollHeight
}

function persist() {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.value.slice(-20)))
}

async function send() {
  const content = input.value.trim()
  if (!content || busy.value) return
  const history = messages.value.slice(-10).map(({ role, content: text }) => ({ role, content: text }))
  messages.value.push({ role: 'user', content })
  input.value = ''
  busy.value = true
  await scrollToBottom()
  try {
    const result = await chatApi.send(content, history, selectedRegion.value)
    messages.value.push({ role: 'assistant', content: result.answer, items: result.matchedItems })
  } catch (error) {
    messages.value.push({ role: 'assistant', content: errorMessage(error, '잠시 후 다시 질문해 주세요.') })
  } finally {
    busy.value = false
    persist()
    await scrollToBottom()
  }
}
</script>

<template>
  <aside :class="['chat-widget', { open }]" aria-label="In지도 챗봇">
    <section v-if="open" class="chat-panel">
      <header class="chat-header">
        <div>
          <span class="status-dot"></span>
          <strong>전국 동네 도우미</strong>
          <small>제공된 지역정보를 바탕으로 답해요</small>
        </div>
        <button class="icon-button" type="button" aria-label="챗봇 닫기" @click="open = false">×</button>
      </header>
      <div ref="messageList" class="chat-messages" aria-live="polite">
        <label class="chat-region">
          <span>답변 지역</span>
          <select v-model="selectedRegion">
            <option v-for="region in REGIONS" :key="region.value" :value="region.value">{{ region.label }}</option>
          </select>
        </label>
        <article v-for="(message, index) in messages" :key="index" :class="['chat-message', message.role]">
          <p>{{ message.content }}</p>
          <div v-if="message.items?.length" class="chat-sources">
            <span v-for="item in message.items" :key="`${item.type}-${item.id}`">{{ item.title }}</span>
          </div>
        </article>
        <article v-if="busy" class="chat-message assistant typing"><span></span><span></span><span></span></article>
      </div>
      <form class="chat-form" @submit.prevent="send">
        <label class="sr-only" for="chat-input">질문 입력</label>
        <input id="chat-input" v-model="input" maxlength="500" placeholder="가고 싶은 여행지를 물어보세요" />
        <button type="submit" :disabled="busy || !input.trim()" aria-label="질문 보내기">↑</button>
      </form>
    </section>
    <button v-else class="chat-toggle" type="button" aria-label="챗봇 열기" @click="open = true">
      <span>✦</span>
      <strong>전국 여행지가 궁금하면 물어보세요</strong>
    </button>
  </aside>
</template>

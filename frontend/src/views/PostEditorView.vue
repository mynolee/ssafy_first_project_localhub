<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import PostForm from '../components/PostForm.vue'

const route = useRoute()
const router = useRouter()
const editing = computed(() => Boolean(route.params.id))
const post = ref(null)
const loading = ref(editing.value)
const busy = ref(false)
const error = ref('')

onMounted(async () => {
  if (!editing.value) return
  try {
    post.value = await postsApi.get(route.params.id)
  } catch (requestError) {
    error.value = errorMessage(requestError, '수정할 게시글을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})

async function save(payload) {
  busy.value = true
  error.value = ''
  try {
    const saved = editing.value
      ? await postsApi.update(route.params.id, payload)
      : await postsApi.create(payload)
    router.push({ name: 'home', query: { region: saved.region, saved: saved.id } })
  } catch (requestError) {
    error.value = errorMessage(requestError, '게시글을 저장하지 못했습니다.')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="page-hero compact editor-hero">
    <div class="container narrow"><p class="eyebrow">SHARE YOUR SEOUL</p><h1>{{ editing ? '이야기 수정' : '새 이야기 쓰기' }}</h1><p>직접 경험한 장소와 팁은 누군가의 좋은 하루가 됩니다.</p></div>
  </section>
  <section class="section editor-section">
    <div class="container narrow">
      <div v-if="loading" class="loading-state">글을 준비하고 있어요...</div>
      <PostForm v-else-if="!editing || post" :initial-post="post" :editing="editing" :busy="busy" :error="error" @submit="save" />
      <p v-else class="notice error-notice">{{ error }}</p>
    </div>
  </section>
</template>

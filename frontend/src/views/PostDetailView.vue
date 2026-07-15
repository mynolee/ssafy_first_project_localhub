<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import PasswordDialog from '../components/PasswordDialog.vue'
import { REGION_LABELS } from '../constants/categories'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const error = ref('')
const dialogOpen = ref(false)
const deleting = ref(false)
const deleteError = ref('')

onMounted(async () => {
  try {
    post.value = await postsApi.get(route.params.id)
  } catch (requestError) {
    error.value = errorMessage(requestError, '게시글을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})

async function removePost(password) {
  deleting.value = true
  deleteError.value = ''
  try {
    await postsApi.remove(route.params.id, password)
    router.push('/posts')
  } catch (requestError) {
    deleteError.value = errorMessage(requestError)
  } finally {
    deleting.value = false
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(value))
}
</script>

<template>
  <section class="section detail-section">
    <div class="container narrow">
      <RouterLink class="back-link" to="/posts">← 이웃 게시판으로</RouterLink>
      <div v-if="loading" class="loading-state">글을 불러오고 있어요...</div>
      <div v-else-if="error" class="notice error-notice">{{ error }} <RouterLink to="/posts">목록으로 돌아가기</RouterLink></div>
      <article v-else class="post-detail">
        <header>
          <span class="region-badge">{{ REGION_LABELS[post.region] }}</span>
          <CategoryBadge :category="post.category" />
          <h1>{{ post.title }}</h1>
          <div class="detail-meta"><strong>{{ post.author }}</strong><span>·</span><time>{{ formatDate(post.createdAt) }}</time></div>
        </header>
        <div class="post-content">{{ post.content }}</div>
        <footer>
          <div class="post-actions">
            <RouterLink class="button button-secondary" :to="`/posts/${post.id}/edit`">수정</RouterLink>
            <button class="button button-danger-ghost" type="button" @click="dialogOpen = true">삭제</button>
          </div>
          <RouterLink class="text-link" to="/posts">다른 이야기 보기 <span>→</span></RouterLink>
        </footer>
      </article>
    </div>
  </section>
  <PasswordDialog :open="dialogOpen" :busy="deleting" :error="deleteError" @close="dialogOpen = false" @confirm="removePost" />
</template>

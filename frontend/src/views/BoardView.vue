<script setup>
import { onMounted, ref, watch } from 'vue'

import { postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import { POST_CATEGORIES } from '../constants/categories'

const posts = ref([])
const selectedCategory = ref('')
const loading = ref(false)
const error = ref('')

async function loadPosts() {
  loading.value = true
  error.value = ''
  try {
    posts.value = await postsApi.list(selectedCategory.value)
  } catch (requestError) {
    error.value = errorMessage(requestError, '게시글을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
}

onMounted(loadPosts)
watch(selectedCategory, loadPosts)
</script>

<template>
  <section class="page-hero compact">
    <div class="container page-hero-inner">
      <div><p class="eyebrow">NEIGHBOR BOARD</p><h1>이웃 게시판</h1><p>서울에서 발견한 좋은 장소와 유용한 경험을 익명으로 나눠보세요.</p></div>
      <RouterLink class="button" to="/posts/new">새 이야기 쓰기</RouterLink>
    </div>
  </section>
  <section class="section board-section">
    <div class="container">
      <div class="board-toolbar">
        <div class="filter-pills" role="group" aria-label="게시판 카테고리">
          <button v-for="category in POST_CATEGORIES" :key="category.value" :class="{ active: selectedCategory === category.value }" type="button" @click="selectedCategory = category.value">{{ category.label }}</button>
        </div>
        <span>총 {{ posts.length }}개의 이야기</span>
      </div>
      <p v-if="error" class="notice error-notice">{{ error }}</p>
      <div v-else-if="loading" class="loading-state">이웃 이야기를 불러오고 있어요...</div>
      <div v-else-if="posts.length" class="post-list card">
        <RouterLink v-for="post in posts" :key="post.id" class="post-row" :to="`/posts/${post.id}`">
          <span class="post-number">{{ String(post.id).padStart(2, '0') }}</span>
          <div class="post-row-main"><CategoryBadge :category="post.category" /><h2>{{ post.title }}</h2></div>
          <div class="post-meta"><span>{{ post.author }}</span><time>{{ formatDate(post.createdAt) }}</time></div>
          <span class="row-arrow">→</span>
        </RouterLink>
      </div>
      <div v-else class="empty-state card"><h2>아직 이야기가 없습니다</h2><p>서울에서의 첫 경험을 이웃에게 알려주세요.</p><RouterLink class="button" to="/posts/new">첫 글 쓰기</RouterLink></div>
    </div>
  </section>
</template>


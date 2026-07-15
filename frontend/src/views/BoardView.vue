<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import { POST_CATEGORIES, REGION_LABELS, REGIONS } from '../constants/categories'
import PostForm from '../components/PostForm.vue'

const route = useRoute()
const router = useRouter()
const posts = ref([])
const selectedCategory = ref('')
const showForm = ref(false)
const selectedRegion = ref(typeof route.query.region === 'string' ? route.query.region : '')
const loading = ref(false)
const error = ref('')
const formBusy = ref(false)
const formError = ref('')

async function loadPosts() {
  loading.value = true
  error.value = ''
  try {
    posts.value = await postsApi.list({
      region: selectedRegion.value,
      category: selectedCategory.value,
    })
  } catch (requestError) {
    error.value = errorMessage(requestError, '게시글을 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

async function createPost(payload) {
  formBusy.value = true
  formError.value = ''
  try {
    await postsApi.create(payload)
    showForm.value = false
    await loadPosts()
  } catch (requestError) {
    formError.value = errorMessage(requestError, '게시글을 저장하지 못했습니다.')
  } finally {
    formBusy.value = false
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
}

onMounted(() => {
  if (route.query.compose) showForm.value = true
  loadPosts()
})
watch([selectedRegion, selectedCategory], () => {
  router.replace({
    query: {
      ...(selectedRegion.value ? { region: selectedRegion.value } : {}),
      ...(route.query.saved ? { saved: route.query.saved } : {}),
    },
  })
  loadPosts()
})
</script>

<template>
  <section id="community" class="page-hero compact main-board-hero">
    <div class="container page-hero-inner">
      <div><p class="eyebrow">LOCAL COMMUNITY</p><h1>지역 게시판</h1><p>전국에서 발견한 좋은 장소와 유용한 경험을 익명으로 나눠보세요.</p></div>
      <button class="button" type="button" @click="showForm = true">새 이야기 쓰기</button>
    </div>
  </section>
  <section class="section board-section main-board-section">
    <div class="container">
      <p v-if="route.query.saved" class="notice success-notice">게시글이 저장되었습니다. 새 글이 목록 맨 위에 표시됩니다.</p>
      <div class="region-filter" role="group" aria-label="지역 선택">
        <button v-for="region in REGIONS" :key="region.value" :class="{ active: selectedRegion === region.value }" type="button" @click="selectedRegion = region.value">{{ region.label }}</button>
      </div>
      <div class="board-toolbar">
        <div class="filter-pills" role="group" aria-label="게시판 카테고리">
          <button v-for="category in POST_CATEGORIES" :key="category.value" :class="{ active: selectedCategory === category.value }" type="button" @click="selectedCategory = category.value">{{ category.label }}</button>
        </div>
        <span>총 {{ posts.length }}개의 이야기</span>
      </div>
      <PostForm
        v-if="showForm"
        :initial-post="null"
        :editing="false"
        :busy="formBusy"
        :error="formError"
        @submit="createPost"
        @cancel="showForm = false"
      />
      <p v-if="error" class="notice error-notice">{{ error }}</p>
      <div v-else-if="loading" class="loading-state">이웃 이야기를 불러오고 있어요...</div>
      <div v-else-if="posts.length" class="post-list card">
        <RouterLink v-for="post in posts" :key="post.id" class="post-row" :to="`/posts/${post.id}`">
          <span class="post-number">{{ String(post.id).padStart(2, '0') }}</span>
          <div class="post-row-main">
            <div class="post-badges"><span class="region-badge">{{ REGION_LABELS[post.region] }}</span><CategoryBadge :category="post.category" /></div>
            <h2>{{ post.title }}</h2>
          </div>
          <div class="post-meta"><span>{{ post.author }}</span><time>{{ formatDate(post.createdAt) }}</time></div>
          <span class="row-arrow">→</span>
        </RouterLink>
      </div>
      <div v-else class="empty-state card"><h2>아직 이야기가 없습니다</h2><p>우리 지역에서의 첫 경험을 이웃에게 알려주세요.</p><button class="button" type="button" @click="showForm = true">첫 글 쓰기</button></div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { postsApi } from '../api/localhub'
import { errorMessage, resolveImageUrl } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import PasswordDialog from '../components/PasswordDialog.vue'
import { POST_CATEGORIES, REGION_LABELS, REGIONS } from '../constants/categories'
import PostForm from '../components/PostForm.vue'

const LIKED_STORAGE_KEY = 'localhub-liked-posts'

function loadLikedIds() {
  try {
    return new Set(JSON.parse(localStorage.getItem(LIKED_STORAGE_KEY)) || [])
  } catch {
    return new Set()
  }
}

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

const expandedId = ref(null)
const activePost = ref(null)
const detailLoading = ref(false)
const detailError = ref('')

const editingId = ref(null)
const editBusy = ref(false)
const editError = ref('')

const dialogOpen = ref(false)
const deleting = ref(false)
const deleteError = ref('')

const likedIds = ref(loadLikedIds())
const likeBusy = ref(false)

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

async function createPost(payload, imageFile) {
  formBusy.value = true
  formError.value = ''
  try {
    const created = await postsApi.create(payload)
    if (imageFile) await postsApi.uploadImage(created.id, imageFile)
    showForm.value = false
    await loadPosts()
  } catch (requestError) {
    formError.value = errorMessage(requestError, '게시글을 저장하지 못했습니다.')
  } finally {
    formBusy.value = false
  }
}

function syncPostInList(id, patch) {
  const target = posts.value.find((post) => post.id === id)
  if (target) Object.assign(target, patch)
}

async function loadDetail(id) {
  detailLoading.value = true
  detailError.value = ''
  try {
    activePost.value = await postsApi.get(id)
    syncPostInList(id, { viewCount: activePost.value.viewCount, likeCount: activePost.value.likeCount })
  } catch (requestError) {
    detailError.value = errorMessage(requestError, '게시글을 불러오지 못했습니다.')
  } finally {
    detailLoading.value = false
  }
}

function closeExpand() {
  expandedId.value = null
  activePost.value = null
  editingId.value = null
  editError.value = ''
  if (route.params.id) router.replace('/posts')
}

function toggleExpand(post) {
  if (expandedId.value === post.id) {
    closeExpand()
    return
  }
  expandedId.value = post.id
  editingId.value = null
  router.replace(`/posts/${post.id}`)
  loadDetail(post.id)
}

function startEdit() {
  editingId.value = expandedId.value
  editError.value = ''
  router.replace(`/posts/${expandedId.value}/edit`)
}

function cancelEdit() {
  editingId.value = null
  router.replace(`/posts/${expandedId.value}`)
}

async function saveEdit(payload, imageFile) {
  editBusy.value = true
  editError.value = ''
  try {
    activePost.value = await postsApi.update(expandedId.value, payload)
    if (imageFile) {
      const imageResult = await postsApi.uploadImage(expandedId.value, imageFile)
      activePost.value = { ...activePost.value, imageUrl: imageResult.imageUrl }
    }
    editingId.value = null
    router.replace(`/posts/${expandedId.value}`)
    await loadPosts()
  } catch (requestError) {
    editError.value = errorMessage(requestError, '게시글을 저장하지 못했습니다.')
  } finally {
    editBusy.value = false
  }
}

async function toggleLike(post) {
  if (likeBusy.value) return
  likeBusy.value = true
  const liked = likedIds.value.has(post.id)
  try {
    const result = liked ? await postsApi.unlike(post.id) : await postsApi.like(post.id)
    syncPostInList(post.id, { likeCount: result.likeCount })
    if (activePost.value?.id === post.id) activePost.value.likeCount = result.likeCount
    const next = new Set(likedIds.value)
    if (liked) next.delete(post.id)
    else next.add(post.id)
    likedIds.value = next
    localStorage.setItem(LIKED_STORAGE_KEY, JSON.stringify([...next]))
  } catch (requestError) {
    detailError.value = errorMessage(requestError, '좋아요 처리에 실패했습니다.')
  } finally {
    likeBusy.value = false
  }
}

function openDeleteDialog() {
  deleteError.value = ''
  dialogOpen.value = true
}

async function removePost(password) {
  deleting.value = true
  deleteError.value = ''
  try {
    await postsApi.remove(expandedId.value, password)
    dialogOpen.value = false
    closeExpand()
    await loadPosts()
  } catch (requestError) {
    deleteError.value = errorMessage(requestError)
  } finally {
    deleting.value = false
  }
}

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium' }).format(new Date(value))
}

onMounted(() => {
  if (route.query.compose) showForm.value = true
  if (route.params.id) {
    const id = Number(route.params.id)
    expandedId.value = id
    if (route.name === 'post-edit') editingId.value = id
    loadDetail(id)
  }
  loadPosts()
})

watch([selectedRegion, selectedCategory], () => {
  expandedId.value = null
  activePost.value = null
  editingId.value = null
  router.replace({
    path: '/posts',
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
        <div v-for="post in posts" :key="post.id" class="post-item">
          <button type="button" class="post-row" :class="{ active: expandedId === post.id }" @click="toggleExpand(post)">
            <span class="post-number">{{ String(post.id).padStart(2, '0') }}</span>
            <div class="post-row-main">
              <div class="post-badges"><span class="region-badge">{{ REGION_LABELS[post.region] }}</span><CategoryBadge :category="post.category" /></div>
              <h2>{{ post.title }}</h2>
            </div>
            <div class="post-meta">
              <span>{{ post.author }}</span>
              <time>{{ formatDate(post.createdAt) }}</time>
              <span class="post-stats"><span>조회 {{ post.viewCount }}</span><span>좋아요 {{ post.likeCount }}</span></span>
            </div>
            <span class="row-arrow">{{ expandedId === post.id ? '↑' : '→' }}</span>
          </button>

          <div v-if="expandedId === post.id" class="post-expand">
            <div v-if="detailLoading" class="loading-state">글을 불러오고 있어요...</div>
            <p v-else-if="detailError" class="notice error-notice">{{ detailError }}</p>
            <template v-else-if="activePost">
              <PostForm
                v-if="editingId === post.id"
                :initial-post="activePost"
                editing
                :busy="editBusy"
                :error="editError"
                @submit="saveEdit"
                @cancel="cancelEdit"
              />
              <template v-else>
                <div class="detail-meta">
                  <strong>{{ activePost.author }}</strong><span>·</span><time>{{ formatDate(activePost.createdAt) }}</time>
                  <span>·</span><span>조회 {{ activePost.viewCount }}</span>
                </div>
                <img v-if="activePost.imageUrl" :src="resolveImageUrl(activePost.imageUrl)" alt="게시글 첨부 이미지" class="post-image" />
                <div class="post-content">{{ activePost.content }}</div>
                <div class="post-actions">
                  <button
                    class="button like-button"
                    :class="{ active: likedIds.has(post.id) }"
                    type="button"
                    :disabled="likeBusy"
                    @click="toggleLike(post)"
                  >
                    {{ likedIds.has(post.id) ? '♥' : '♡' }} 좋아요 {{ activePost.likeCount }}
                  </button>
                  <button class="button button-secondary" type="button" @click="startEdit">수정</button>
                  <button class="button button-danger-ghost" type="button" @click="openDeleteDialog">삭제</button>
                </div>
              </template>
            </template>
          </div>
        </div>
      </div>
      <div v-else class="empty-state card"><h2>아직 이야기가 없습니다</h2><p>우리 지역에서의 첫 경험을 이웃에게 알려주세요.</p><button class="button" type="button" @click="showForm = true">첫 글 쓰기</button></div>
    </div>
  </section>
  <PasswordDialog :open="dialogOpen" :busy="deleting" :error="deleteError" @close="dialogOpen = false" @confirm="removePost" />
</template>

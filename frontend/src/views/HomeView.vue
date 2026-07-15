<script setup>
import { computed, onMounted, ref } from 'vue'

import { placesApi, postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import PlaceMap from '../components/PlaceMap.vue'
import { PLACE_CATEGORIES } from '../constants/categories'

const places = ref([])
const recentPosts = ref([])
const selectedCategory = ref('')
const loading = ref(true)
const error = ref('')

const filteredPlaces = computed(() =>
  selectedCategory.value
    ? places.value.filter((place) => place.category === selectedCategory.value)
    : places.value,
)

onMounted(async () => {
  try {
    ;[places.value, recentPosts.value] = await Promise.all([placesApi.list(), postsApi.list()])
    recentPosts.value = recentPosts.value.slice(0, 4)
  } catch (requestError) {
    error.value = errorMessage(requestError, '서울 지역 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
})

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { month: 'short', day: 'numeric' }).format(new Date(value))
}
</script>

<template>
  <section class="hero">
    <div class="container hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">SEOUL, CLOSE TO YOU</p>
        <h1>서울을 더 가까이,<br /><em>이웃의 시선으로.</em></h1>
        <p class="hero-description">공공데이터로 찾은 서울의 장소와 직접 다녀온 이웃의 이야기를 한곳에서 만나보세요.</p>
        <div class="hero-actions">
          <a class="button" href="#discover">서울 둘러보기</a>
          <RouterLink class="text-link" to="/posts">이웃 이야기 보기 <span>→</span></RouterLink>
        </div>
        <dl class="hero-stats">
          <div><dt>{{ places.length }}</dt><dd>지역 정보</dd></div>
          <div><dt>{{ recentPosts.length }}</dt><dd>최근 이야기</dd></div>
          <div><dt>24h</dt><dd>AI 동네 도우미</dd></div>
        </dl>
      </div>
      <div class="hero-visual">
        <div class="seoul-orbit orbit-one"></div>
        <div class="seoul-orbit orbit-two"></div>
        <div class="seoul-pin pin-one"><span>북촌</span></div>
        <div class="seoul-pin pin-two"><span>남산</span></div>
        <div class="seoul-pin pin-three"><span>한강</span></div>
        <div class="hero-card">
          <span class="hero-card-icon">⌖</span>
          <div><small>오늘의 서울</small><strong>가까운 동네부터<br />천천히 발견해요</strong></div>
        </div>
      </div>
    </div>
  </section>

  <section id="discover" class="section discover-section">
    <div class="container">
      <div class="section-heading">
        <div><p class="eyebrow">DISCOVER SEOUL</p><h2>지금, 어디로 가볼까요?</h2></div>
        <p>카테고리를 고르면 지도와 장소가 함께 바뀝니다.</p>
      </div>
      <div class="filter-pills" role="group" aria-label="지역정보 카테고리">
        <button
          v-for="category in PLACE_CATEGORIES"
          :key="category.value"
          :class="{ active: selectedCategory === category.value }"
          type="button"
          @click="selectedCategory = category.value"
        >{{ category.label }}</button>
      </div>
      <p v-if="error" class="notice error-notice">{{ error }}</p>
      <div v-else-if="loading" class="loading-state">서울 지도를 준비하고 있어요...</div>
      <div v-else class="map-layout">
        <PlaceMap :places="filteredPlaces" />
        <div class="place-list">
          <article v-for="place in filteredPlaces.slice(0, 5)" :key="place.id" class="place-card">
            <div class="place-index">{{ String(place.id).padStart(2, '0') }}</div>
            <div>
              <CategoryBadge :category="place.category" />
              <h3>{{ place.name }}</h3>
              <p>{{ place.description }}</p>
              <small>⌖ {{ place.address || '주소 정보 없음' }}</small>
            </div>
          </article>
          <div v-if="!filteredPlaces.length" class="empty-state">이 카테고리의 장소는 준비 중입니다.</div>
        </div>
      </div>
    </div>
  </section>

  <section class="section story-section">
    <div class="container">
      <div class="section-heading">
        <div><p class="eyebrow">NEIGHBOR STORIES</p><h2>서울을 먼저 경험한<br />이웃의 이야기</h2></div>
        <RouterLink class="text-link" to="/posts">게시판 전체 보기 <span>→</span></RouterLink>
      </div>
      <div v-if="recentPosts.length" class="story-grid">
        <RouterLink v-for="post in recentPosts" :key="post.id" class="story-card" :to="`/posts/${post.id}`">
          <CategoryBadge :category="post.category" />
          <h3>{{ post.title }}</h3>
          <div><span>{{ post.author }}</span><time>{{ formatDate(post.createdAt) }}</time></div>
        </RouterLink>
      </div>
      <div v-else class="story-empty card">
        <p>아직 등록된 이웃 이야기가 없어요.</p>
        <RouterLink class="button" to="/posts/new">첫 이야기 남기기</RouterLink>
      </div>
    </div>
  </section>
</template>


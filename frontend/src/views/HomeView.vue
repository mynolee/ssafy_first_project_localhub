<script setup>
import { onMounted, ref, watch } from 'vue'

import { placesApi, postsApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import CategoryBadge from '../components/CategoryBadge.vue'
import PlaceMap from '../components/PlaceMap.vue'
import { PLACE_CATEGORIES, REGIONS } from '../constants/categories'

const places = ref([])
const recentPosts = ref([])
const selectedCategory = ref('')
const selectedRegion = ref('SEOUL')
const loading = ref(true)
const error = ref('')

async function loadContent() {
  loading.value = true
  error.value = ''
  try {
    ;[places.value, recentPosts.value] = await Promise.all([
      placesApi.list({ region: selectedRegion.value, category: selectedCategory.value }),
      postsApi.list({ region: selectedRegion.value }),
    ])
    recentPosts.value = recentPosts.value.slice(0, 4)
  } catch (requestError) {
    error.value = errorMessage(requestError, '지역 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(loadContent)
watch([selectedRegion, selectedCategory], loadContent)

function formatDate(value) {
  return new Intl.DateTimeFormat('ko-KR', { month: 'short', day: 'numeric' }).format(new Date(value))
}
</script>

<template>
  <section class="hero">
    <div class="container hero-grid">
      <div class="hero-copy">
        <p class="eyebrow">KOREA, CLOSE TO YOU</p>
        <h1>우리 지역을 더 가까이,<br /><em>이웃의 시선으로.</em></h1>
        <p class="hero-description">공공데이터로 찾은 전국의 장소와 직접 다녀온 이웃의 이야기를 한곳에서 만나보세요.</p>
        <div class="hero-actions">
          <a class="button" href="#discover">전국 둘러보기</a>
          <RouterLink class="text-link" to="/">이웃 이야기 보기 <span>→</span></RouterLink>
        </div>
        <dl class="hero-stats">
          <div><dt>{{ places.length }}+</dt><dd>선택 지역 정보</dd></div>
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
          <div><small>오늘의 우리 지역</small><strong>가까운 동네부터<br />천천히 발견해요</strong></div>
        </div>
      </div>
    </div>
  </section>

  <section id="discover" class="section discover-section">
    <div class="container">
      <div class="section-heading">
        <div><p class="eyebrow">DISCOVER KOREA</p><h2>지금, 어디로 가볼까요?</h2></div>
        <p>카테고리를 고르면 지도와 장소가 함께 바뀝니다.</p>
      </div>
      <div class="region-filter" role="group" aria-label="지역 선택">
        <button v-for="region in REGIONS.slice(1)" :key="region.value" :class="{ active: selectedRegion === region.value }" type="button" @click="selectedRegion = region.value">{{ region.label }}</button>
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
      <div v-else-if="loading" class="loading-state">지역 지도를 준비하고 있어요...</div>
      <div v-else class="map-layout">
        <PlaceMap :places="places" />
        <div class="place-list">
          <article v-for="place in places.slice(0, 20)" :key="place.id" class="place-card">
            <div class="place-index">{{ String(place.id).padStart(2, '0') }}</div>
            <div>
              <CategoryBadge :category="place.category" />
              <h3>{{ place.name }}</h3>
              <p>{{ place.description || '한국관광공사에서 제공한 지역 정보입니다.' }}</p>
              <small>⌖ {{ place.address || '주소 정보 없음' }}</small>
            </div>
          </article>
          <div v-if="!places.length" class="empty-state">이 카테고리의 장소는 준비 중입니다.</div>
        </div>
      </div>
    </div>
  </section>

  <section class="section story-section">
    <div class="container">
      <div class="section-heading">
        <div><p class="eyebrow">NEIGHBOR STORIES</p><h2>우리 지역을 먼저 경험한<br />이웃의 이야기</h2></div>
        <RouterLink class="text-link" to="/">게시판 전체 보기 <span>→</span></RouterLink>
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

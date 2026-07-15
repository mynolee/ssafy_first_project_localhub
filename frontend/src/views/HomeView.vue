<script setup>
import { onMounted, ref, watch } from 'vue'

import { placesApi } from '../api/localhub'
import { errorMessage } from '../api/client'
import BoardView from './BoardView.vue'
import CategoryBadge from '../components/CategoryBadge.vue'
import PlaceMap from '../components/PlaceMap.vue'
import { PLACE_CATEGORIES, REGIONS } from '../constants/categories'

const places = ref([])
const selectedCategory = ref('')
const selectedRegion = ref('SEOUL')
const loading = ref(true)
const error = ref('')

async function loadPlaces() {
  loading.value = true
  error.value = ''
  try {
    places.value = await placesApi.list({
      region: selectedRegion.value,
      category: selectedCategory.value,
      limit: 200,
    })
  } catch (requestError) {
    error.value = errorMessage(requestError, '지역 정보를 불러오지 못했습니다.')
  } finally {
    loading.value = false
  }
}

onMounted(loadPlaces)
watch([selectedRegion, selectedCategory], loadPlaces)
</script>

<template>
  <BoardView />

  <section id="discover" class="section discover-section">
    <div class="container">
      <div class="section-heading">
        <div>
          <p class="eyebrow">LOCAL MAP</p>
          <h2>게시판 아래에서<br />지역을 둘러보세요</h2>
        </div>
        <p>지역과 카테고리를 선택하면 공공데이터 장소가 지도와 목록에 함께 표시됩니다.</p>
      </div>

      <div class="region-filter" role="group" aria-label="지도 지역 선택">
        <button
          v-for="region in REGIONS.slice(1)"
          :key="region.value"
          :class="{ active: selectedRegion === region.value }"
          type="button"
          @click="selectedRegion = region.value"
        >
          {{ region.label }}
        </button>
      </div>

      <div class="filter-pills map-category-filter" role="group" aria-label="지역정보 카테고리">
        <button
          v-for="category in PLACE_CATEGORIES"
          :key="category.value"
          :class="{ active: selectedCategory === category.value }"
          type="button"
          @click="selectedCategory = category.value"
        >
          {{ category.label }}
        </button>
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
          <div v-if="!places.length" class="empty-state">선택한 조건의 장소가 없습니다.</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import L from 'leaflet'

import { CATEGORY_LABELS } from '../constants/categories'

// 카테고리별 색상 정의
const CATEGORY_COLORS = {
  TOURIST: '#e85d3f',     // 주황색 - 관광지
  RESTAURANT: '#d5a63c',  // 노란색 - 맛집
  FESTIVAL: '#ff6b9d',    // 핑크 - 축제
  CULTURE: '#5b5bff',     // 파란색 - 문화
  COURSE: '#00bfa5',      // 청록색 - 코스
  LEISURE: '#9c27b0',     // 보라색 - 여가
  ACCOMMODATION: '#ff7043',// 밝은 주황 - 숙박
  SHOPPING: '#29b6f6',    // 연한 파란색 - 쇼핑
}

function getCategoryColor(category) {
  return CATEGORY_COLORS[category] || '#e85d3f'
}

const props = defineProps({
  places: { type: Array, default: () => [] },
  selectedPlaceId: { type: Number, default: null },
})
const emit = defineEmits(['place-selected'])

let map
let markerLayer
let markerByPlaceId = new Map()
let previousView = null

function focusPlace(place) {
  if (!map || !place?.latitude || !place?.longitude) return
  map.setView([place.latitude, place.longitude], 15, { animate: true })
}

function storeCurrentView() {
  if (!map) return
  previousView = {
    center: map.getCenter(),
    zoom: map.getZoom(),
  }
}

function restoreMapView() {
  if (!map) return
  if (previousView) {
    map.setView(previousView.center, previousView.zoom, { animate: true })
  } else {
    map.setView([37.5665, 126.978], 11, { animate: true })
  }
}

function updateMarkerHighlight(placeId) {
  markerByPlaceId.forEach((marker, id) => {
    const place = props.places.find(p => p.id === id)
    const isSelected = id === placeId
    marker.setStyle({
      radius: isSelected ? 10 : 9,
      color: '#ffffff',
      weight: isSelected ? 4 : 3,
      fillColor: isSelected ? '#1d5b49' : getCategoryColor(place?.category),
      fillOpacity: 1,
    })
  })
}

function calculateOptimalBounds() {
  if (!map || !markerLayer) return
  const bounds = []
  props.places
    .filter((place) => place.latitude != null && place.longitude != null)
    .forEach((place) => {
      bounds.push([place.latitude, place.longitude])
    })
  
  if (bounds.length === 0) return
  
  // Seoul의 중심을 기준으로 적절한 범위 내의 마커만 선택
  const seoulCenter = [37.5665, 126.978]
  const maxDistance = 0.15 // 약 15km 범위
  
  const filteredBounds = bounds.filter(coord => {
    const latDiff = Math.abs(coord[0] - seoulCenter[0])
    const lngDiff = Math.abs(coord[1] - seoulCenter[1])
    return latDiff < maxDistance && lngDiff < maxDistance
  })
  
  if (filteredBounds.length > 0) {
    map.fitBounds(filteredBounds, { padding: [35, 35], maxZoom: 13 })
  } else if (bounds.length > 0) {
    map.fitBounds(bounds, { padding: [35, 35], maxZoom: 13 })
  }
}

function drawMarkers() {
  if (!map || !markerLayer) return
  markerLayer.clearLayers()
  markerByPlaceId = new Map()
  props.places
    .filter((place) => place.latitude != null && place.longitude != null)
    .forEach((place) => {
      const coordinates = [place.latitude, place.longitude]
      const marker = L.circleMarker(coordinates, {
        radius: 9,
        color: '#ffffff',
        weight: 3,
        fillColor: getCategoryColor(place.category),
        fillOpacity: 1,
      })
      marker.bindPopup(
        `<strong>${place.name}</strong><br>${CATEGORY_LABELS[place.category] || place.category}<br>${place.address || ''}`,
      )
      marker.on('click', () => {
        emit('place-selected', place)
        updateMarkerHighlight(place.id)
      })
      marker.addTo(markerLayer)
      markerByPlaceId.set(place.id, marker)
    })
  calculateOptimalBounds()
}

onMounted(async () => {
  await nextTick()
  map = L.map('place-map', { scrollWheelZoom: false }).setView([37.5665, 126.978], 11)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  markerLayer = L.layerGroup().addTo(map)
  drawMarkers()
})

watch(() => props.places, drawMarkers, { deep: true })
watch(
  () => props.selectedPlaceId,
  (newId, oldId) => {
    if (!newId) {
      restoreMapView()
      updateMarkerHighlight(null)
      return
    }

    if (!oldId) {
      storeCurrentView()
    }

    const place = props.places.find((item) => item.id === newId)
    if (place) {
      focusPlace(place)
      updateMarkerHighlight(newId)
    }
  },
)

onBeforeUnmount(() => {
  map?.remove()
})
</script>

<template>
  <div id="place-map" class="place-map" aria-label="서울 지역정보 지도"></div>
</template>


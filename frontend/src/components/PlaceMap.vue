<script setup>
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import L from 'leaflet'

import { CATEGORY_LABELS } from '../constants/categories'

const props = defineProps({ places: { type: Array, default: () => [] } })

let map
let markerLayer

function drawMarkers() {
  if (!map || !markerLayer) return
  markerLayer.clearLayers()
  const bounds = []
  props.places
    .filter((place) => place.latitude != null && place.longitude != null)
    .forEach((place) => {
      const coordinates = [place.latitude, place.longitude]
      const marker = L.circleMarker(coordinates, {
        radius: 9,
        color: '#ffffff',
        weight: 3,
        fillColor: '#e85d3f',
        fillOpacity: 1,
      })
      marker.bindPopup(
        `<strong>${place.name}</strong><br>${CATEGORY_LABELS[place.category] || place.category}<br>${place.address || ''}`,
      )
      marker.addTo(markerLayer)
      bounds.push(coordinates)
    })
  if (bounds.length) map.fitBounds(bounds, { padding: [35, 35], maxZoom: 13 })
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

onBeforeUnmount(() => {
  map?.remove()
})
</script>

<template>
  <div id="place-map" class="place-map" aria-label="서울 지역정보 지도"></div>
</template>


<script setup>
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import L from 'leaflet'

import { CATEGORY_LABELS } from '../constants/categories'

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
    marker.setStyle({
      radius: id === placeId ? 10 : 9,
      color: '#ffffff',
      weight: id === placeId ? 4 : 3,
      fillColor: id === placeId ? '#1d5b49' : '#e85d3f',
      fillOpacity: 1,
    })
  })
}

function drawMarkers() {
  if (!map || !markerLayer) return
  markerLayer.clearLayers()
  const bounds = []
  markerByPlaceId = new Map()
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
      marker.on('click', () => {
        emit('place-selected', place)
        updateMarkerHighlight(place.id)
      })
      marker.addTo(markerLayer)
      markerByPlaceId.set(place.id, marker)
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


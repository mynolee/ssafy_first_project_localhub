<script setup>
import { computed } from 'vue'

import { CATEGORY_LABELS } from '../constants/categories'

const props = defineProps({ category: { type: String, required: true } })
const label = computed(() => CATEGORY_LABELS[props.category] || props.category)
</script>

<template>
  <span :class="['category-badge', `category-${category.toLowerCase()}`]">{{ label }}</span>
</template>


<script setup>
import { nextTick, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuOpen = ref(false)

function closeMenu() {
  menuOpen.value = false
}

async function goToSection(sectionId) {
  closeMenu()
  await router.push({ name: 'home', hash: `#${sectionId}` })
  await nextTick()
  document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' })
}

async function goToCompose() {
  closeMenu()
  await router.push({ name: 'home', hash: '#community', query: { compose: '1' } })
  await nextTick()
  document.getElementById('community')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink class="brand" to="/" @click="closeMenu">
        <span class="brand-mark">여</span>
        <span>여행씰</span>
      </RouterLink>
      <button
        class="menu-button"
        type="button"
        aria-label="메뉴 열기"
        :aria-expanded="menuOpen"
        @click="menuOpen = !menuOpen"
      >
        <span></span><span></span><span></span>
      </button>
      <nav :class="['main-nav', { open: menuOpen }]" aria-label="주요 메뉴">
        <button class="nav-section-button" type="button" @click="goToSection('community')">지역 게시판</button>
        <button class="nav-section-button" type="button" @click="goToSection('discover')">지역 지도</button>
        <button class="button button-small" type="button" @click="goToCompose">글쓰기</button>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'

const menuOpen = ref(false)

function closeMenu() {
  menuOpen.value = false
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <RouterLink class="brand" to="/" @click="closeMenu">
        <span class="brand-mark">L</span>
        <span>LocalHub</span>
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
        <RouterLink to="/" @click="closeMenu">서울 둘러보기</RouterLink>
        <RouterLink to="/posts" @click="closeMenu">이웃 게시판</RouterLink>
        <RouterLink class="button button-small" to="/posts/new" @click="closeMenu">글쓰기</RouterLink>
      </nav>
    </div>
  </header>
</template>


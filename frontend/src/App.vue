<script setup>
import AppHeader from './components/AppHeader.vue'
import ChatWidget from './components/ChatWidget.vue'
</script>

<template>
  <div class="app-shell">
    <AppHeader />
    <main>
      <RouterView />
    </main>
    <ChatWidget />
    <footer class="site-footer">
      <div class="container footer-inner">
        <div>
          <strong>LocalHub</strong>
          <p>전국의 장소와 사람을 잇는 지역 정보 커뮤니티</p>
        </div>
        <p>SSAFY 광주 4반 5팀 · 2026</p>
      </div>
    </footer>
  </div>
</template>

import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import PostEditorView from '../views/PostEditorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', alias: ['/posts', '/explore'], name: 'home', component: HomeView },
    { path: '/posts/:id', name: 'post-detail', component: PostDetailView },
    { path: '/posts/:id/edit', name: 'post-edit', component: PostEditorView },
  ],
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, top: 80, behavior: 'smooth' }
    return { top: 0 }
  },
})

export default router

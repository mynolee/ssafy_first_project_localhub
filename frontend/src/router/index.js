import { createRouter, createWebHistory } from 'vue-router'

import BoardView from '../views/BoardView.vue'
import HomeView from '../views/HomeView.vue'
import PostDetailView from '../views/PostDetailView.vue'
import PostEditorView from '../views/PostEditorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/posts', name: 'posts', component: BoardView },
    { path: '/posts/new', name: 'post-new', component: PostEditorView },
    { path: '/posts/:id', name: 'post-detail', component: PostDetailView },
    { path: '/posts/:id/edit', name: 'post-edit', component: PostEditorView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router


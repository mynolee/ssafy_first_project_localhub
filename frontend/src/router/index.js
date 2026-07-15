import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'

const BOARD_ROUTE_NAMES = ['home', 'post-detail', 'post-edit']

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', alias: ['/posts', '/explore'], name: 'home', component: HomeView },
    { path: '/posts/:id', name: 'post-detail', component: HomeView },
    { path: '/posts/:id/edit', name: 'post-edit', component: HomeView },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) return { el: to.hash, top: 80, behavior: 'smooth' }
    if (savedPosition) return savedPosition
    if (BOARD_ROUTE_NAMES.includes(to.name) && BOARD_ROUTE_NAMES.includes(from.name)) return false
    return { top: 0 }
  },
})

export default router

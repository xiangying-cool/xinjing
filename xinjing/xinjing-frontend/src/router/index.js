import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // 登录页（独立布局，不套 MainLayout）
  { path: '/login', name: 'Login', component: () => import('../pages/LoginPage.vue') },

  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../pages/HomePage.vue'), meta: { requiresAuth: true } },
      { path: 'screening', name: 'Screening', component: () => import('../pages/ScreeningPage.vue'), meta: { requiresAuth: true } },
      { path: 'companion', name: 'Companion', component: () => import('../pages/CompanionPage.vue'), meta: { requiresAuth: true } },
      { path: 'mood-calendar', name: 'MoodCalendar', component: () => import('../pages/MoodCalendarPage.vue'), meta: { requiresAuth: true } },
      { path: 'analytics', name: 'Analytics', component: () => import('../pages/AnalyticsPage.vue'), meta: { requiresAuth: true } },
      { path: 'about', name: 'About', component: () => import('../pages/AboutPage.vue'), meta: { requiresAuth: true } },
      { path: 'assessment/:type', name: 'Assessment', component: () => import('../pages/AssessmentPage.vue'), meta: { requiresAuth: true } },
      { path: 'report/:id', name: 'Report', component: () => import('../pages/ReportPage.vue'), meta: { requiresAuth: true } },
      { path: 'profile', name: 'Profile', component: () => import('../pages/ProfilePage.vue'), meta: { requiresAuth: true } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 })
})

// 导航守卫：未登录时跳转到登录页
router.beforeEach((to) => {
  const saved = localStorage.getItem('xinjing_auth')
  let parsed = null
  try {
    parsed = saved ? JSON.parse(saved) : null
  } catch {
    parsed = null
  }

  const userId = Number(parsed?.user?.id)
  const hasValidAuth = !!parsed?.token && Number.isInteger(userId) && userId > 0

  if (to.path === '/login' && hasValidAuth) {
    return { path: '/' }
  }

  if (to.meta.requiresAuth && !hasValidAuth) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  return true
})

export default router

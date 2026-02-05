import { createRouter, createWebHistory } from 'vue-router'
// 假设你原来的 Dashboard 组件叫 HomeView 或者 DashboardView，这里需要根据你实际的文件名引入
import HomeView from '../views/HomeView.vue' // 👈 这是你原来的主页组件
import LoginView from '../views/Login.vue' // 👈 新引入

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true } // 👈 标记：这个页面需要登录
    },
    // 如果你有其他页面，比如 workers，也加上 meta: { requiresAuth: true }
  ]
})

// 👮‍♂️ 全局路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 1. 如果要去的地方需要登录，且没有 Token
  if (to.meta.requiresAuth && !token) {
    next('/login') // 踢回登录页
  } 
  // 2. 如果已经登录了还想去登录页，直接送回首页
  else if (to.path === '/login' && token) {
    next('/')
  } 
  // 3. 放行
  else {
    next()
  }
})

export default router
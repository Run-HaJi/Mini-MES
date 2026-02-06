import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import MainLayout from '../views/MainLayout.vue' // 👈 引入布局
import DashboardView from '../views/DashboardView.vue'
import OperatorView from '../views/OperatorView.vue' // 👈 引入新页面

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      // 🟢 父路由：使用布局组件
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      // 🟡 子路由：内容展示区
      children: [
        {
          path: '', // 默认跳到 dashboard
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView
        },
        {
          path: 'operators', // 新地址 /operators
          name: 'operators',
          component: OperatorView
        }
      ]
    }
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
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import MainLayout from '../views/MainLayout.vue'
import DashboardView from '../views/DashboardView.vue'
import OperatorView from '../views/OperatorView.vue'
import StationView from '../views/StationView.vue' // ✅ 已引入

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    // 🟢 新增：工位终端 (HMI) 独立页面
    // 它不需要侧边栏，所以放在 MainLayout 外面，跟 Login 平级
    {
      path: '/station',
      name: 'station',
      component: StationView,
      // 注意：这里暂时不加 requiresAuth，因为工位机可能开机自启直接进这个页面
      // 具体的“工号登录”逻辑由 StationView 内部处理
    },
    {
      // 🔵 管理后台：使用布局组件
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true }, // 需要 Admin 登录才能进
      // 子路由：内容展示区
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
          path: 'operators', 
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
  // 3. 放行 (包括 /station)
  else {
    next()
  }
})

export default router
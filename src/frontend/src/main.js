import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// 1. 引入 Element Plus 及其样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入深色模式样式 (工业风常用黑底)
import 'element-plus/theme-chalk/dark/css-vars.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 2. 安装 UI 库
app.use(ElementPlus)

app.mount('#app')